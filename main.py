import pygame
import sys
import os
import enemies, path, market, defenses.cannon, defenses.barrier as barrier, constants, economy, text, spawner
from effects import initialize_flash, get_flash_instance, initialize_invalid_placement_flash, get_invalid_placement_flash_instance

pygame.init()
screen = pygame.display.set_mode((800, 600))
width, height = screen.get_size()
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

initialize_flash(screen)
initialize_invalid_placement_flash(screen)

path_points = path.generate_path_points(width, height)
# Precompute cumulative distances along the path for constant speed progression.
cumulative_lengths = path.cumulative_distances(path_points)

enemies_list = []

market_btn = market.make_market_btn(screen)
market_instance = market.make_market(screen)
market_instance.enemies_list = enemies_list
balance_display = text.Balance_Display(screen)

# Create a defense instance using market_instance
barrier_defense = barrier.Barrier(screen, market_instance, (255, 0, 255))

market_is_active = False
market_btn_is_active = True

# Create an enemy spawner instance (using our BloonTD6-style spawner)
enemy_spawner = spawner.EnemySpawner(screen, path_points, cumulative_lengths)

# Initialize the player's health.
player_hp = 50
game_over = False

# Create a font for the HP display (using a smaller font size than the balance)
hp_font = pygame.font.Font(None, 24)

def circle_rect_collision(circle_center, circle_radius, rect):
    cx, cy = circle_center
    nearest_x = max(rect.left, min(cx, rect.right))
    nearest_y = max(rect.top, min(cy, rect.bottom))
    dx = cx - nearest_x
    dy = cy - nearest_y
    return dx * dx + dy * dy <= circle_radius * circle_radius

running = True
while running:
    # Get delta time in milliseconds and update the game clock.
    dt = clock.tick(60)
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
            running = False

    # Cache the mouse position for use in update and draw calls.
    cached_mouse_pos = pygame.mouse.get_pos()

    # Check if the market button is clicked.
    if market_btn.update(event_list, cached_mouse_pos) and market_btn_is_active:
        market_is_active = not market_is_active
        market_btn_is_active = not market_btn_is_active
        # Remove the MOUSEBUTTONDOWN events so the click does not propagate further.
        event_list = [e for e in event_list if e.type != pygame.MOUSEBUTTONDOWN]
    elif market_instance.update(event_list) and market_is_active:
        market_is_active = not market_is_active
        market_btn_is_active = not market_btn_is_active

    # Update enemy spawner and add any newly spawned enemies.
    new_enemies = enemy_spawner.update(dt)
    enemies_list.extend(new_enemies)

    screen.fill((0, 0, 0))
    # Generate and draw the path polygon.
    path_polygon = path.get_path_polygon(path_points, 25)
    pygame.draw.polygon(screen, constants.color_theme, path_polygon)

    enemies_to_remove = []
    defenses_to_remove = []

    for defense in market_instance.placed_defenses:
        if isinstance(defense, defenses.cannon.Cannon) and defense.pos is not None:
            defense.aim_at_enemy()
            for event in event_list:
                defense.handle_event(event, cached_mouse_pos)

    # Collision detection between enemies and placed defenses.
        for enemy in enemies_list:
            enemy_center = (enemy.posx, enemy.posy)
            for defense in market_instance.placed_defenses:
                defense_rect = defense.get_rect()
                if circle_rect_collision(enemy_center, enemy.radius, defense_rect) and isinstance(defense, barrier.Barrier):
                    enemy.hp -= defense.dmg
                    defense.hp -= 1
                    if enemy.hp <= 0:
                        enemies_to_remove.append(enemy)
                        economy.balance += enemy.reward
                    if defense.hp <= 0:
                        defenses_to_remove.append(defense)

    # Remove defeated enemies and destroyed defenses.
    for enemy in enemies_to_remove:
        if enemy in enemies_list:
            enemies_list.remove(enemy)
    for defense in defenses_to_remove:
        if defense in market_instance.placed_defenses:
            market_instance.placed_defenses.remove(defense)

    # Check for enemy escapes – if an enemy has reached or exceeded the end of the path,
    # subtract its "damage" from the player's HP (here, enemy.tier * 5) and remove it.
    enemies_escaped = []
    for enemy in enemies_list:
        if enemy.distance >= cumulative_lengths[-1]:
            enemies_escaped.append(enemy)
    for enemy in enemies_escaped:
        player_hp -= enemy.tier * 5  # adjust damage cost as desired
        enemies_list.remove(enemy)           

    if player_hp <= 0:
        game_over = True
        running = False  # end the main game loop and transition to the game over state

    # Update and draw all enemies.
    for enemy in enemies_list:
        enemy.update(path_points, cumulative_lengths)
        enemy.draw()

    # Draw any placed defenses.
    market_instance.draw_defenses(screen)

    if market_is_active:
        market_instance.draw(screen, cached_mouse_pos)

    if market_btn_is_active:
        market_btn.draw(screen)

    flash = get_flash_instance()
    flash.update()
    flash.draw()

    balance_display.update()
    balance_display.draw()

    # Draw player's HP below the balance text in a smaller font.
    hp_text = hp_font.render(f"HP: {player_hp}", True, (255, 255, 255))
    screen.blit(hp_text, (10, 50))
    pygame.display.flip()

# Game Over state: Show a blurred screen with GAME OVER text and a Try Again button.
if game_over:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        # Create a blurred version of the current screen.
        blurred = pygame.transform.smoothscale(screen, (width // 10, height // 10))
        blurred = pygame.transform.smoothscale(blurred, (width, height))
        screen.blit(blurred, (0, 0))
        
        # Draw the GAME OVER text.
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 40))
        screen.blit(game_over_text, game_over_rect)
        
        # Draw the Try Again button.
        button_font = pygame.font.SysFont(None, 36)
        try_again_text = button_font.render("Try Again", True, (255, 255, 255))
        try_again_rect = try_again_text.get_rect(center=(width // 2, height // 2 + 40))
        # Draw a background rectangle for the button.
        button_background = try_again_rect.inflate(20, 10)
        pygame.draw.rect(screen, (50, 50, 50), button_background)
        pygame.draw.rect(screen, (255, 255, 255), button_background, 2)
        screen.blit(try_again_text, try_again_rect)
        
        # Check for click on the Try Again button.
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if button_background.collidepoint(mouse_pos):
                # Restart the script by re-executing the Python interpreter with the same arguments.
                os.execl(sys.executable, sys.executable, *sys.argv)
        
        pygame.display.flip()
        clock.tick(60)

pygame.quit()