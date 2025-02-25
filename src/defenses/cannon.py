import pygame
import enemies
import math
import economy  # for refunding when selling
import defenses.defense
import defenses.projectile

class Cannon(defenses.defense.Defense):
    def __init__(self, screen, market, enemy_list, width, height, hp, dmg, cost, scope, tags, has_front, front_img):
        super().__init__(screen, market, enemy_list, width, height, hp, dmg, cost, scope, tags, has_front, front_img)
        self.cannon_base = pygame.image.load("assets/cannon/base.png").convert_alpha()
        self.cannon_pipe = pygame.image.load("assets/cannon/pipe.png").convert_alpha()
        self.cannon_pipe_original = self.cannon_pipe.copy()
        self.base_rect = self.cannon_base.get_rect(center=self.get_rect().center)
        self.pipe_rect = self.cannon_pipe.get_rect(center=self.get_rect().center)
        self.pos = self.get_rect().center  # Set the cannon's position
        #self.start_time = pygame.time.get_ticks()
        self.delay = 750
        self.start_time = 0
        #self.elapsed_time = self.current_time-self.start_time

    def draw(self):
        if hasattr(self, 'pos') and self.pos is not None:
            # Update the rects to be centered at the cannon's position
            self.base_rect = self.cannon_base.get_rect(center=self.pos)
            self.pipe_rect = self.cannon_pipe.get_rect(center=self.pos)
            self.screen.blit(self.cannon_base, self.base_rect)
            self.screen.blit(self.cannon_pipe, self.pipe_rect)