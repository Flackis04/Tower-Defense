import pygame
import random
import enemies

class EnemySpawner:
    def __init__(self, screen, path_points, cumulative_lengths):
        self.screen = screen
        self.path_points = path_points
        self.cumulative_lengths = cumulative_lengths
        self.spawn_timer = 0.0
        self.spawn_interval = 2000  # Start with 2000ms (2 seconds) delay between spawns.
        self.wave_count = 0       # Total count of enemies spawned to influence difficulty.

    def update(self, dt):
        """
        dt: Time in milliseconds since the last frame.
        Returns a list of new enemies spawned during this update.
        """
        new_enemies = []
        self.spawn_timer += dt

        # Check if it's time to spawn a new group of enemies.
        while self.spawn_timer >= self.spawn_interval:
            # Determine the number of enemies to spawn this wave.
            # Spawns between 1 and (3 + (wave_count // 20)) enemies.
            group_quantity = random.randint(1, 3 + self.wave_count // 20)
            for _ in range(group_quantity):
                enemy = self.spawn_enemy()
                new_enemies.append(enemy)
            self.spawn_timer -= self.spawn_interval
            self.wave_count += group_quantity

            # Vary the spawn delay for the next group using a random factor,
            # but never let the delay drop below 500ms.
            random_factor = random.uniform(0.9, 1.2)
            self.spawn_interval = max(500, int(self.spawn_interval * random_factor))
        
        return new_enemies

    def spawn_enemy(self):
        # Base tier increases roughly every 10 enemies spawned.
        base_tier = 1 + self.wave_count // 10
        # With a 30% chance, spawn an enemy one tier higher (capped at tier 5).
        if random.random() < 0.3:
            tier = min(5, base_tier + 1)
        else:
            tier = min(5, base_tier)

        # Map tiers to colors.
        tier_to_color = {
            1: (255, 0, 0),       # red
            2: (0, 0, 255),       # blue
            3: (0, 255, 0),       # green
            4: (255, 255, 0),     # yellow
            5: (255, 192, 203)    # pink
        }
        color = tier_to_color[tier]
        radius = 10  # Adjust if desired per tier.
        # Base speed increases with the overall enemy count.
        base_speed = 1 + self.wave_count / 50.0
        # Each enemy tier above 1 increases speed by 20%.
        speed_multiplier = 1 + (tier - 1) * 0.2
        step = base_speed * speed_multiplier
        # Reward scales with the enemy tier.
        reward = tier * 10

        # Create and return a new Enemy instance.
        return enemies.Enemy(self.screen, tier, color, radius, step, reward)
