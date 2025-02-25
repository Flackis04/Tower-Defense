import pygame
import sys
import os
import math
import defenses.defense
import enemies
import path.pathgen
import market
import defenses.projectile
import defenses.cannon
import defenses.barrier as barrier
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
    screen = pygame.display.set_mode((800, 600))
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
    market_instance = market.make_market(screen)
    market_btn = market.make_market_btn(screen, market_instance)
    barrier_inst = barrier.Barrier(screen, market, enemy_list=enemies.enemies_list, width=50, height=50, hp=50, dmg=1, cost=500, scope=False, tags=("other",), has_front=False, front_img=False)
    balance_display = text.Balance_Display(screen)
    projectile_inst = defenses.projectile.Projectile(screen)
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
        projectile_inst.draw_projectile(screen)

        # Update enemies.
        enemies.Enemy.update_enemies(enemies_list, enemy_spawner, dt, path_points, cumulative_lengths)

        # Process market events.
        event_list, cached_mouse_pos = market.update_market(event_list, market_instance, market_btn)
        defenses.defense.Defense.update_defenses_events(market_instance, event_list, cached_mouse_pos)

        # Draw the path.
        path.pathgen.draw_path(screen, path_points)

        # Handle collisions and enemy escapes.
        defenses.defense.Defense.check_collisions(enemies_list, market_instance, barrier_inst)
        player_hp = enemies.Enemy.update_enemy_escapes(enemies_list, cumulative_lengths, player_hp)

        # Draw enemies and UI.
        enemies.draw_enemies(enemies.make_enemies())
        ui.ui_renderer.draw_ui(screen, market_instance, market_btn, balance_display, hp_font, player_hp, cached_mouse_pos)

        pygame.display.flip()

        # End the game loop if the player's HP reaches 0.
        if player_hp <= 0:
            running = False

    if player_hp <= 0:
        ui.game_over.show_game_over(screen, width, height, clock)
    pygame.quit()

if __name__ == "__main__":
    main()
