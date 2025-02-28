import pygame
import path.pathgen as pathgen
import market
import enemies
import spawner
import defenses.defense as defense
import defenses.projectile as projectile
import defenses.barrier as barrier
import ui.text as text
import ui.game_over
import ui.ui_renderer

def draw_fps(screen, clock, font):
    """Render the FPS counter on the screen."""
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    text_rect = fps_text.get_rect(bottomleft=(10, screen.get_height() - 10))
    screen.blit(fps_text, text_rect)


def handle_events(market_inst, btn_inst):
    """
    Process all pygame events and handle market button events.
    Returns a tuple (events) unless a quit event is detected.
    If a quit event is detected, returns (None, None) to signal termination.
    """
    event_list = pygame.event.get()

    # Check for quit or specific key events early.
    for event in event_list:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_j):
            return None, None

    # Process market button events.
    for btn in market_inst.btn_list:
        btn.handle_event(event_list)
        btn.update()  # Update button hover state & transitions

    # Update market-specific events (e.g., mouse position caching).
    event_list = market.update_market(event_list, market_inst, btn_inst)

    # Update the pinned button separately
    btn_inst.update()

    return event_list



def main():
    # Initialization
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    # Update dimensions in case the display mode changes the size.
    screen_width, screen_height = screen.get_size()
    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()
    bg_image = pygame.image.load("assets/smooth_noise_bg.png")

    # Path generation
    path_points = pathgen.generate_path_points(screen_width, screen_height)

    # Initialize game modules and objects.
    enemy_spawner_inst = spawner.EnemySpawner(screen, path_points)
    market_inst = market.make_market(screen, screen_width, screen_height)
    btn_inst = market.Button(xpos=100, ypos=100, text="Click Me", color=(0, 128, 255), hover_color=(255, 0, 0))
    projectile_inst = projectile.Projectile(screen)
    barrier_inst = barrier.Barrier(
        screen, market, enemies_list=enemies.enemies_list, width=50, height=50,
        hp=50, dmg=1, cost=500, scope=False, tags=("other",), has_front=False, front_img=False
    )
    balance_display = text.Balance_Display(screen)
    hp_font = pygame.font.Font(None, 24)
    fps_font = pygame.font.SysFont(None, 30)
    player_hp = 500000

    running = True
    while running:
        # Handle events and check for quit signal.
        events = handle_events(market_inst, btn_inst)
        if events is None:  # Quit event received.
            break

        # Limit the framerate and get delta time (in milliseconds).
        dt_ms = clock.tick(60)

        # Game state updates.
        # Spawner now only spawns enemies
        new_enemies = enemy_spawner_inst.update(dt_ms)
        enemies.enemies_list.extend(new_enemies)

        # Update all enemy positions once using dt
        for enemy in enemies.enemies_list:
            enemy.update(dt_ms)

        # Remove or comment out any duplicate update calls such as:
        # enemies.Enemy.update_enemies(enemies.enemies_list, enemy_spawner_inst, dt_ms)


        market_inst.update(events)
        defense.Defense.update_defenses_events(market_inst, events)
        defense.Defense.check_collisions(enemies.enemies_list, market_inst, barrier_inst)
        player_hp = enemies.Enemy.update_enemy_escapes(enemies.enemies_list, player_hp)

        # Rendering.
        screen.blit(bg_image, (0, 0))
        projectile_inst.draw_projectile(screen)
        pathgen.draw_path(screen, path_points)
        enemies.draw_enemies(enemies.enemies_list)
        ui.ui_renderer.draw_ui(
            screen, market_inst, market_inst.market_btn, balance_display, hp_font, player_hp
        )
        draw_fps(screen, clock, fps_font)
        pygame.display.flip()

        # End game loop if the player's HP drops to 0 or below.
        if player_hp <= 0:
            running = False

    # Show game over screen if the player lost.
    if player_hp <= 0:
        ui.game_over.show_game_over(screen, screen_width, screen_height, clock)
    pygame.quit()


if __name__ == "__main__":
    main()
