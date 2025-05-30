import pygame
import path.pathx as pathx
import other.helper as helper

enemies_list = []

class Enemy:


    tier_to_color = {
        1: (255, 0, 64),            
        2: (64, 0, 255),             
        3: (0, 255, 64),              
        4: (255, 255, 64),             
        5: (255, 64, 255),            
        6: (0, 0, 0)            
    }

    def __init__(self, 
                screen, 
                path_points,
                tier,
                color, 
                radius,
                speed, 
                reward, ):
        
        self.screen = screen
        self.tier = tier
        self.radius = radius
        self.reward = reward
        self.speed = speed                                   
                                                                 
        self.path_points = path_points() if callable(path_points) else path_points
        self.color = color if color is not None else Enemy.tier_to_color.get((255, 255, 255))

                                                           
        self.arc_lengths = pathx.compute_arc_lengths(path_points)
        self.total_length = self.arc_lengths[-1]

                                 
        self.distance_traveled = 0.0
        self.posx, self.posy = self.path_points[0]
        self.hp = 1

    def update(self, dt):
        """
        Move the enemy uniformly along the path based on arc-length.
        dt: delta time in milliseconds.
        """
        dt_sec = dt / 1000.0                                   
        if self.distance_traveled < self.total_length:
                                                               
            self.distance_traveled += self.speed * dt_sec
            if self.distance_traveled > self.total_length:
                self.distance_traveled = self.total_length

                                            
            segment_index = 0
            for i in range(len(self.arc_lengths) - 1):
                if self.arc_lengths[i] <= self.distance_traveled <= self.arc_lengths[i + 1]:
                    segment_index = i
                    break

            segment_start = self.arc_lengths[segment_index]
            segment_end = self.arc_lengths[segment_index + 1]
            segment_length = segment_end - segment_start

                                                    
            t = (self.distance_traveled - segment_start) / segment_length if segment_length != 0 else 0

                                                    
            start_point = self.path_points[segment_index]
            end_point = self.path_points[segment_index + 1]
            self.posx = (1 - t) * start_point[0] + t * end_point[0]
            self.posy = (1 - t) * start_point[1] + t * end_point[1]
        else:
                                         
            self.posx, self.posy = self.path_points[-1]

    def pop(self):
        if self.hp <= 0:
            if self.tier > 1:
                self.tier -= 1
                self.hp = self.tier
                self.color = Enemy.tier_to_color[self.tier]
                return False
            else:
                return True
        return False

    @staticmethod
    def update_enemy_escapes(enemies_list, player_hp):
        """Remove enemies that have reached the end of the path."""
        enemies_escaped = [enemy for enemy in enemies_list if enemy.distance_traveled >= enemy.total_length]
        for enemy in enemies_escaped:
            player_hp -= enemy.tier
            enemies_list.remove(enemy)
        return player_hp

    @staticmethod
    def update_enemies(enemies_list, enemy_spawner, dt):
        """Spawn new enemies and update all enemy positions with dt."""
        new_enemies = enemy_spawner.update(dt)
        enemies_list.extend(new_enemies)
        for enemy in enemies_list:
            enemy.update(dt)

    def draw(self):
        pygame.draw.circle(
            self.screen, 
            self.color, 
            (int(self.posx), int(self.posy)), 
            self.radius
        )

def draw_enemies(enemies_list):
    for enemy in enemies_list:
        enemy.draw()

def get_path(width, height):
    return pathx.generate_path_points(width, height)