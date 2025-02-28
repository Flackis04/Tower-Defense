import pygame
import random
import enemies
import path.pathgen as path

class EnemySpawner:
    def __init__(self, screen, path_points):
        self.screen = screen
        self.path_points = path_points
        self.spawn_timer = 0.0
        self.spawn_interval = 2500  # initial delay between spawns in ms.
        self.wave_count = 0
        self.enemies_list = enemies.enemies_list

    def update(self, dt):
        """Update spawner to handle enemy spawning only."""
        self.spawn_timer += dt
        new_enemies = []

        while self.spawn_timer >= self.spawn_interval:
            max_group = 3 + self.wave_count // 20
            group_quantity = random.randint(1, max_group)
            for _ in range(group_quantity):
                new_enemies.append(self.spawn_enemy())

            self.spawn_timer -= self.spawn_interval
            self.wave_count += group_quantity
            # Remove debug print to avoid overhead.
            self.spawn_interval = int(self.spawn_interval * random.uniform(0.9, 1.2))

        self.enemies_list.extend(new_enemies)
        return new_enemies


    def spawn_enemy(self):
        """Creates a new enemy at the start of the path."""
        base_tier = 1 + self.wave_count // 10
        tier = base_tier + 1 if random.random() < 0.3 else base_tier
        tier = min(tier, 5)

        color = enemies.Enemy.tier_to_color[tier]
        radius = 15
        base_speed = 75  # Adjusted to pixels per second.
        speed = base_speed * (1 + (tier - 1) * 0.2)
        reward = tier * 10

        # Pass the path points.
        start_position = self.path_points

        return enemies.Enemy(self.screen, start_position, tier, color, radius, speed, reward)

        
    def remove_defeated_enemies(self):
        """Removes defeated enemies (hp <= 0) from the spawner's enemy list."""
        alive_enemies = [enemy for enemy in self.enemies_list if enemy.hp > 0]
        self.enemies_list = alive_enemies
