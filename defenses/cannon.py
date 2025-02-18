import pygame
import market
import math
import economy  # for refunding when selling
import defenses.defense as defense

class Cannon(defense.Defense):
    def __init__(self, screen, market, width=4, height=4, hp=250, dmg=1, cost=1000, snapbox=35, scope=200, type="default"):
        super().__init__(screen, market, hp, dmg, cost, width, height, snapbox, scope, type)
        self.screen = screen
        self.scope = scope
        self.cannon_base = pygame.image.load("assets/cannon/base.png").convert_alpha()
        self.cannon_pipe = pygame.image.load("assets/cannon/pipe.png").convert_alpha()
        self.cannon_pipe_original = self.cannon_pipe.copy()
        self.center = self.market.get_container_center(0)
        self.base_rect = self.cannon_base.get_rect(center=self.center)
        self.pipe_rect = self.cannon_pipe.get_rect(center=self.center)
        original_pipe = self.cannon_pipe_original.copy()
        pipe_width, pipe_height = original_pipe.get_size()
        offset_surface = pygame.Surface((pipe_width, pipe_height), pygame.SRCALPHA)
        # IMPORTANT: blit the original pipe image onto the offset surface
        offset_surface.blit(original_pipe, (0, 0))
        self.pos = None


    def get_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_closest_enemy(self):
        enemies = self.market.enemies_list
        closest_enemy = None
        scope_distance = self.scope
        for enemy in enemies:
            distance = self.get_distance(self.pos, enemy.get_position())
            if distance < scope_distance:
                scope_distance = distance
                closest_enemy = enemy
        return closest_enemy
    
    def get_angle_to(self, enemy):
        dx = enemy.posx - self.pos[0]
        dy = enemy.posy - self.pos[1]
        return math.atan2(dy, dx)
    
    def aim_at_enemy(self):
        enemy = self.get_closest_enemy()
        if enemy and self.pos:
            self.angle = self.get_angle_to(enemy)
            # Rotate the instance-specific pipe image.
            rotated_pipe = pygame.transform.rotate(self.cannon_pipe_original, -(math.degrees(self.angle) - 90))
            self.cannon_pipe = rotated_pipe
        else:
            self.angle = 0
            self.cannon_pipe = self.cannon_pipe_original.copy()
    
    def draw(self):
        if hasattr(self, 'pos') and self.pos is not None:
            # Update the rects to be centered at the cannon's position
            self.base_rect = self.cannon_base.get_rect(center=self.pos)
            self.pipe_rect = self.cannon_pipe.get_rect(center=self.pos)
            self.screen.blit(self.cannon_base, self.base_rect)
            self.screen.blit(self.cannon_pipe, self.pipe_rect)