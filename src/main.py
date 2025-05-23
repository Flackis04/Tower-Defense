import pygame
import path.pathx as pathx
import market
import enemies.enemies as enemies
import enemies.spawner as spawner
import defenses.defense as defense
import defenses.projectile as projectile
import defenses.barrier as barrier
import ui.text as text
import ui.game_over
import ui.ui_renderer
import ui.home
import other.colors as colors
import other.config as config
import numpy as np
import other.helper as helper

def draw_fps(screen, clock, font):
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, colors.WHITE)
    text_rect = fps_text.get_rect(bottomleft=(10, screen.get_height() - 10))
    screen.blit(fps_text, text_rect)

def handle_events(market_inst, btn_inst):
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_j):
            return None, None
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pass                      
    for btn in market_inst.btn_list:
        btn.handle_event(event_list)
        btn.update()
    event_list = market.update_market(event_list, market_inst, btn_inst)
    btn_inst.update()
    return event_list

def main():
    pygame.init()
    development = True
    if development:
        info = pygame.display.Info()
        screen_width, screen_height = info.current_w, info.current_h
        screen = pygame.display.set_mode((helper.get_screen_size(False, False)), pygame.DOUBLEBUF | pygame.HWSURFACE)
    else:
        info = pygame.display.Info()
        screen_width, screen_height = info.current_w, info.current_h
        screen = pygame.display.set_mode((helper.get_screen_size(False, False)), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)

    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()
    bg_image = pygame.image.load("assets/bg.png")
    path_points = pathx.get_path_points()

    enemy_spawner_inst = spawner.EnemySpawner(screen, path_points)
    market_inst = market.make_market(
        screen, screen_width, screen_height)
    btn_inst = market.Button()
    projectile_inst = projectile.Projectile(screen)
    barrier_inst = barrier.Barrier(screen=screen, market=market_inst)
    balance_display = text.Balance_Display(screen)
    hp_font = pygame.font.Font(None, 24)
    fps_font = pygame.font.SysFont(None, 30)

    enemy_spawner_inst.spawning = True
    home = ui.home.Home(screen)
    running_game = True
    running = True

    while running:
        events = handle_events(market_inst, btn_inst)
        if events is None:
            break
        dt_ms = clock.tick(60)

        if enemy_spawner_inst.spawning and not enemy_spawner_inst.pause_spawn:
            new_enemies = enemy_spawner_inst.update(dt_ms)
            enemies.enemies_list.extend(new_enemies)

        for enemy in enemies.enemies_list:
            enemy.update(dt_ms)

        enemy_spawner_inst.remove_defeated_enemies()
        market_inst.update(events)
        defense.Defense.check_collisions(enemies.enemies_list, market_inst, barrier_inst)
        config.player_hp = enemies.Enemy.update_enemy_escapes(enemies.enemies_list, config.player_hp)

        screen.blit(bg_image, (0, 0))
        pathx.draw_path(screen, path_points)
        projectile_inst.draw_projectile(screen)
        enemies.draw_enemies(enemies.enemies_list)
        ui.ui_renderer.draw_ui(
            screen, events, market_inst, market_inst.market_btn, balance_display, hp_font, config.player_hp
        )
        draw_fps(screen, clock, fps_font)
        pygame.display.flip()

        if config.player_hp <= 0:
            running = False

    if config.player_hp <= 0:
        ui.game_over.show_game_over(screen, screen_width, screen_height, clock)
    pygame.quit()

if __name__ == "__main__":
    main()
