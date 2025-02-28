import pygame
import market
import math
import economy  # for refunding when selling
import defenses.defense

class Mortar(defenses.defense.Defense):
    def __init__(self, screen, market, enemies_list, width, height, hp, dmg, cost, scope, tags, has_front, front_img):
        super().__init__(screen, market, enemies_list, width, height, hp, dmg, cost, scope, tags, has_front, front_img)
        self.mortar_image = pygame.image.load("assets/mortar/mortar.png").convert_alpha()
        self.rect = self.mortar_image.get_rect(center=(self.width // 2, self.height // 2))
        self.pos = None
    
    def draw(self):
        if self.pos is not None:
            self.rect = self.mortar_image.get_rect(center=self.pos)
            self.screen.blit(self.mortar_image, self.rect)