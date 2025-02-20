import pygame
import market
import math
import economy  # for refunding when selling
import defenses.defense as defense

class Mortar(defense.Defense):
    def __init__(self, screen, market, width=4, height=4, hp=300, dmg=3, cost=1500, snapbox=35, scope=300, type="default", has_front=False, front_img=False):
        super().__init__(screen, market, width, height, hp, dmg, cost, snapbox, scope, type, has_front, front_img)
        self.mortar_image = pygame.image.load("assets/mortar/mortar.png").convert_alpha()
        self.center = self.market.get_container_center(0)
        self.rect = self.mortar_image.get_rect(center=self.center)
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
    
    def attack(self):
        enemy = self.get_closest_enemy()
        if enemy:
            # Mortar attack logic (e.g., splash damage)
            enemy.take_damage(self.dmg)
    
    def draw(self):
        if self.pos is not None:
            self.rect = self.mortar_image.get_rect(center=self.pos)
            self.screen.blit(self.mortar_image, self.rect)