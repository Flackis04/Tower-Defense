import pygame
import sys
import os
import math
import defenses.defense
import enemies
import path.pathgen
import market
import defenses.projectile as projectile
import defenses.cannon as cannon
import defenses.barrier as barrier
import defenses.reverser as reverser
import other.constants
import economy
import utils.collision
import ui.text as text
import spawner
import ui
import ui.game_over
import ui.ui_renderer

def main():
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    width, height = screen.get_size()
    bg_image = pygame.image.load("assets/smooth_noise_bg.png")
    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()

    # Path generation
    path_points = path.pathgen.generate_path_points(width, height)
    cumulative_lengths = path.pathgen.cumulative_distances(path_points)

    # Game objects and modules
    enemies_list = enemies.make_enemies()
    enemy_spawner = spawner.EnemySpawner(screen, path_points, cumulative_lengths)
    market_inst = market.make_market(screen, screen_width, screen_height)
    barrier_inst = barrier.Barrier(
        screen, market, enemy_list=enemies.enemies_list, width=50, height=50,
        hp=50, dmg=1, cost=500, scope=False, tags=("other",), has_front=False, front_img=False
    )
    balance_display = text.Balance_Display(screen)
    projectile_inst = defenses.projectile.Projectile(screen)
    hp_font = pygame.font.Font(None, 24)
    player_hp = 50000

    running = True
    while running:
        dt = clock.tick(60)
        event_list = pygame.event.get()  # Fetch all events at once
        for btn in market_inst.btn_list: 
            btn.handle_event(event_list)

        # Process remaining events
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                running = False

        dt = clock.tick(60)  # dt in milliseconds.

        # Update enemy spawner and add any new enemies to the enemy list.
        new_enemies = enemy_spawner.update(dt)
        enemies_list.extend(new_enemies)

        # Update enemy positions.
        for enemy in enemies_list:
            enemy.update(path_points, cumulative_lengths)

        # Draw all enemies.
        enemies.draw_enemies(enemies_list)



        market_inst.update(event_list)

        # Draw background and projectile.
        screen.blit(bg_image, (0, 0))
        projectile_inst.draw_projectile(screen)

        # Update enemies.
        enemies.Enemy.update_enemies(enemies_list, enemy_spawner, dt, path_points, cumulative_lengths)

        # Process market events.
        event_list, cached_mouse_pos = market.update_market(event_list, market_inst, market_inst.market_btn)
        defenses.defense.Defense.update_defenses_events(market_inst, event_list, cached_mouse_pos)

        # Draw the path.
        path.pathgen.draw_path(screen, path_points)

        # Handle collisions and enemy escapes.
        defenses.defense.Defense.check_collisions(enemies_list, market_inst, barrier_inst)
        player_hp = enemies.Enemy.update_enemy_escapes(enemies_list, cumulative_lengths, player_hp)

        # Draw enemies and UI.
        enemies.draw_enemies(enemies_list)
        ui.ui_renderer.draw_ui(screen, market_inst, market_inst.market_btn, balance_display, hp_font, player_hp, cached_mouse_pos)
        
        pygame.display.flip()

        # End the game loop if the player's HP reaches 0.
        if player_hp <= 0:
            running = False

    if player_hp <= 0:
        ui.game_over.show_game_over(screen, width, height, clock)
    pygame.quit()

if __name__ == "__main__":
    main()
