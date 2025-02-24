import pygame
import sys
import os
import math
import enemies
import path.pathgen
import market
import defenses.cannon
import defenses.barrier as barrier
import constants
import economy
import text
import spawner

def circle_rect_collision(circle_center, circle_radius, rect):
    """Return True if a circle and rectangle intersect."""
    cx, cy = circle_center
    nearest_x = max(rect.left, min(cx, rect.right))
    nearest_y = max(rect.top, min(cy, rect.bottom))
    dx = cx - nearest_x
    dy = cy - nearest_y
    return dx * dx + dy * dy <= circle_radius * circle_radius

def update_market(event_list, market_instance, market_btn):
    """
    Handle market button and market toggle events.
    Returns the updated event_list (with MOUSEBUTTONDOWN events removed, if needed)
    and the current mouse position.
    """
    cached_mouse_pos = pygame.mouse.get_pos()
    if market_btn.update(event_list, cached_mouse_pos) and market_instance.btn_is_active:
        print("Market button clicked")
        market_instance.toggle()
        market_instance.is_active = True
        # Remove MOUSEBUTTONDOWN events to prevent click propagation
        event_list = [e for e in event_list if e.type != pygame.MOUSEBUTTONDOWN]
    elif market_instance.update(event_list) and market_instance.is_active:
        market_instance.toggle()
        market_instance.is_active = False
    return event_list, cached_mouse_pos

def update_defenses_events(market_instance, event_list, cached_mouse_pos):
    """
    Update defenses that require aiming and event handling.
    """
    for defense in market_instance.placed_defenses:
        if isinstance(defense, defenses.cannon.Cannon):
            defense.aim_at_enemy()
            for event in event_list:
                defense.handle_event(event, cached_mouse_pos)

def check_collisions(enemies_list, market_instance, barrier_inst):
    """
    Process collisions between enemies and defenses (specifically barriers).
    If a collision occurs, adjust HP accordingly and schedule objects for removal.
    """
    enemies_to_remove = []
    defenses_to_remove = []
    for enemy in enemies_list:
        enemy_center = (enemy.posx, enemy.posy)
        for defense in market_instance.placed_defenses:
            # For barriers, use the barrier instance's rect.
            if isinstance(defense, barrier.Barrier):
                defense_rect = barrier_inst.rect
                if circle_rect_collision(enemy_center, enemy.radius, defense_rect):
                    enemy.hp -= defense.dmg
                    defense.hp -= 1
                    if enemy.hp <= 0:
                        enemies_to_remove.append(enemy)
                        economy.balance += enemy.reward
                    if defense.hp <= 0:
                        defenses_to_remove.append(defense)
    for enemy in enemies_to_remove:
        if enemy in enemies_list:
            enemies_list.remove(enemy)
    for defense in defenses_to_remove:
        if defense in market_instance.placed_defenses:
            market_instance.placed_defenses.remove(defense)

def update_enemy_escapes(enemies_list, cumulative_lengths, player_hp):
    """
    Remove enemies that have reached the end of the path and subtract their damage
    from the player's HP.
    """
    enemies_escaped = []
    for enemy in enemies_list:
        if enemy.distance >= cumulative_lengths[-1]:
            enemies_escaped.append(enemy)
    for enemy in enemies_escaped:
        player_hp -= enemy.tier * 5  # Adjust damage cost as desired.
        enemies_list.remove(enemy)
    return player_hp

def update_enemies(enemies_list, enemy_spawner, dt, path_points, cumulative_lengths):
    """
    Spawn new enemies, add them to the list, and update each enemy's state.
    """
    new_enemies = enemy_spawner.update(dt)
    enemies_list.extend(new_enemies)
    for enemy in enemies_list:
        enemy.update(path_points, cumulative_lengths)

def draw_projectile(screen, projectile_inst):
    """Draw the projectile (for debugging or effect purposes)."""
    pygame.draw.rect(screen, (200, 0, 0), projectile_inst.rect, projectile_inst.dia)

def draw_path(screen, path_points):
    """Draw the game path as a filled polygon."""
    path_polygon = path.pathgen.get_path_polygon(path_points, 35)
    pygame.draw.polygon(screen, (45, 45, 45), path_polygon)

def draw_enemies(enemies_list):
    """Draw all enemies."""
    for enemy in enemies_list:
        enemy.draw()

def draw_ui(screen, market_instance, market_btn, balance_display, hp_font, player_hp, cached_mouse_pos):
    """
    Draw UI elements including defenses, market, balance display, and HP.
    """
    market_instance.draw_defenses(screen)
    if market_instance.is_active:
        market_instance.draw(screen, cached_mouse_pos)
    if market_instance.btn_is_active:
        market_btn.draw(screen)
    balance_display.update()
    balance_display.draw()
    hp_text = hp_font.render(f"HP: {player_hp}", True, (255, 255, 255))
    screen.blit(hp_text, (10, 50))

def show_game_over(screen, width, height, clock):
    """
    Display a game over screen with a blurred background and a "Try Again" button.
    Clicking the button will restart the game.
    """
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
        button_background = try_again_rect.inflate(20, 10)
        pygame.draw.rect(screen, (50, 50, 50), button_background)
        pygame.draw.rect(screen, (255, 255, 255), button_background, 2)
        screen.blit(try_again_text, try_again_rect)
        # Check for click on the Try Again button.
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if button_background.collidepoint(mouse_pos):
                os.execl(sys.executable, sys.executable, *sys.argv)
        pygame.display.flip()
        clock.tick(60)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    width, height = screen.get_size()
    bg_image = pygame.image.load("assets/smooth_noise_bg.png")
    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()

    # Path generation
    path_points = path.pathgen.generate_path_points(width, height)
    cumulative_lengths = path.pathgen.cumulative_distances(path_points)

    # Game objects and modules
    enemies_list = enemies.make_enemies(screen)
    enemy_spawner = spawner.EnemySpawner(screen, path_points, cumulative_lengths)
    market_instance = market.make_market(screen)
    market_btn = market.make_market_btn(screen, market_instance)
    barrier_inst = barrier.Barrier(screen, market, enemies)
    balance_display = text.Balance_Display(screen)
    projectile_inst = defenses.cannon.Projectile(screen)
    hp_font = pygame.font.Font(None, 24)
    player_hp = 50

    running = True
    while running:
        dt = clock.tick(60)
        event_list = pygame.event.get()
        # Process quit events.
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                running = False

        # Draw background and projectile.
        screen.blit(bg_image, (0, 0))
        draw_projectile(screen, projectile_inst)

        # Update enemies.
        update_enemies(enemies_list, enemy_spawner, dt, path_points, cumulative_lengths)

        # Process market events.
        event_list, cached_mouse_pos = update_market(event_list, market_instance, market_btn)
        update_defenses_events(market_instance, event_list, cached_mouse_pos)

        # Draw the path.
        draw_path(screen, path_points)

        # Handle collisions and enemy escapes.
        check_collisions(enemies_list, market_instance, barrier_inst)
        player_hp = update_enemy_escapes(enemies_list, cumulative_lengths, player_hp)

        # Draw enemies and UI.
        draw_enemies(enemies_list)
        draw_ui(screen, market_instance, market_btn, balance_display, hp_font, player_hp, cached_mouse_pos)

        pygame.display.flip()

        # End the game loop if the player's HP reaches 0.
        if player_hp <= 0:
            running = False

    if player_hp <= 0:
        show_game_over(screen, width, height, clock)
    pygame.quit()

if __name__ == "__main__":
    main()
