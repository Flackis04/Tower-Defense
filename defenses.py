import pygame
import market

class Blöja:
    def __init__(self, screen, market, color, hp=5, dmg=1, cost=500, snapbox=35):
        self.screen = screen
        self.market = market
        self.color = color
        self.hp = hp
        self.dmg = dmg
        self.cost = cost
        self.snapbox = snapbox
        self.pos = None  # Initialize position
        self.angle = 0   # 0 for normal, 90 for rotated

    def get_rect(self):
        if self.pos is not None:
            x, y = self.pos
        else:
            x, y = self.market.get_container_center(2)
        if self.angle == 90:
            width, height = 50, 20
        else:
            width, height = 20, 50
        return pygame.Rect(x - width // 2, y - height // 2, width, height)

    def draw(self):
        rect = self.get_rect()
        pygame.draw.rect(self.screen, self.color, rect)