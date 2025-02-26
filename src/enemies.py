import pygame
import bisect

enemies_list = []

class Enemy:
    # Define casual colors for each tier.
    tier_to_color = {
        1: (255, 0, 0),       # red
        2: (0, 0, 255),       # blue
        3: (0, 255, 0),       # green
        4: (255, 255, 0),     # yellow
        5: (255, 192, 203)    # pink
    }

    def __init__(self, screen, hp, color, radius, step, reward):
        self.screen = screen
        # Use the passed hp as the tier value and current health.
        self.tier = hp
        self.hp = hp
        self.radius = radius
        self.reward = reward
        self.step = step  # speed factor (e.g., red: 1, green: 2, blue: 3)
        self.distance = 0.0  # total distance traveled along the path in pixels
        self.posx, self.posy = self.get_start_position()
        # Override the color based on the current tier.
        self.color = Enemy.tier_to_color.get(self.tier, color)

    def get_start_position(self):
        _, height = self.screen.get_size()
        return (0 - self.radius, int(height * 0.125))
    
    def get_position(self):
        return (self.posx, self.posy)

    def update(self, path_points, cumulative_lengths):
        # Increase the traveled distance by the enemy's speed factor.
        self.distance += self.step

        total_distance = cumulative_lengths[-1]
        if self.distance > total_distance:
            self.distance = total_distance

        # Use binary search to locate the segment where the enemy is.
        segment_index = bisect.bisect_right(cumulative_lengths, self.distance) - 1
        if segment_index >= len(path_points) - 1:
            self.posx, self.posy = path_points[-1]
        else:
            seg_start_distance = cumulative_lengths[segment_index]
            seg_end_distance = cumulative_lengths[segment_index + 1]
            segment_length = seg_end_distance - seg_start_distance
            fraction = 0
            if segment_length > 0:
                fraction = (self.distance - seg_start_distance) / segment_length

            x1, y1 = path_points[segment_index]
            x2, y2 = path_points[segment_index + 1]
            self.posx = x1 + fraction * (x2 - x1)
            self.posy = y1 + fraction * (y2 - y1)

    def pop(self):
        """
        Called when the enemy's hp reaches 0.
        If the enemy is not at the lowest tier (tier 1), then update the tier,
        reset hp to the new tier, and update its color so that it reappears.
        Return False to indicate the enemy remains in play.
        If already at tier 1, return True to signal full pop and removal.
        """
        if self.hp <= 0:
            if self.tier > 1:
                self.tier -= 1
                self.hp = self.tier  # Reset hp to the new tier value.
                self.color = Enemy.tier_to_color[self.tier]
                # Optionally, trigger a pop effect here.
                return False
            else:
                return True
        return False
    
    @staticmethod
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

    @staticmethod
    def update_enemies(enemies_list, enemy_spawner, dt, path_points, cumulative_lengths):
        """
        Spawn new enemies, add them to the list, and update each enemy's state.
        """
        new_enemies = enemy_spawner.update(dt)
        enemies_list.extend(new_enemies)
        for enemy in enemies_list:
            enemy.update(path_points, cumulative_lengths)

    def draw(self):
        """
        Draw the enemy as a circle using its casual color.
        """
        pygame.draw.circle(
            self.screen, 
            self.color, 
            (int(self.posx), int(self.posy)), 
            self.radius
        )

def make_enemies():
    return []  # Return an empty list properly

def draw_enemies(enemies_list):
    for enemy in enemies_list:
        enemy.draw()  # Draw each enemy as a circle
