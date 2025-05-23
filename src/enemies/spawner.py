import pygame
import random
import enemies.enemies as enemies
import other.helper as helper

class EnemySpawner:
    def __init__(self, screen, path_points):
        self.screen = screen
        self.path_points = path_points
        self.spawn_timer = 0.0
        self.spawn_interval = 2500
        self.wave_count = 0
        self.pause_spawn = False
        self.spawning = True

    def update(self, dt):
        self.spawn_timer += dt
        new_enemies = []

        while self.spawn_timer >= self.spawn_interval:
            max_group = 3 + self.wave_count // 20
            group_quantity = random.randint(1, max_group)
            for _ in range(group_quantity):
                new_enemies.append(self.spawn_enemy())

            self.spawn_timer -= self.spawn_interval
            self.wave_count += group_quantity
            self.spawn_interval = int(self.spawn_interval * random.uniform(0.9, 1.2))
            print(f"wave count: {self.wave_count}")
            print(f"enemy count: {len(enemies.enemies_list)}")

        if self.wave_count >= 5 and self.spawning:
            self.spawning = False
            self.pause_spawn = True
            if len(enemies.enemies_list) == 0:
                self.spawning = True
                self.pause_spawn = False
                print("spawning continued")
            print("spawning stopped")

        return new_enemies

    def spawn_enemy(self):
        base_tier = 1 + self.wave_count // 10
        tier = base_tier + 1 if random.random() < 0.3 else base_tier
        tier = min(tier, 6)
        color = enemies.Enemy.tier_to_color[tier]
        radius = helper.get_screen_size(True, False) // 90
        base_speed = 125
        speed = base_speed * (1 + (tier - 1) * 0.2)
        reward = tier * 10
        start_position = self.path_points
        return enemies.Enemy(self.screen, start_position, tier, color, radius, speed, reward)

    def remove_defeated_enemies(self):
        alive_enemies = [enemy for enemy in enemies.enemies_list if enemy.hp > 0]
        enemies.enemies_list = alive_enemies
