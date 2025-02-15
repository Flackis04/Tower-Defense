import pygame
import market

class Defense:
    def __init__(self, screen, market, color, hp, dmg, cost, snapbox, width, height):
        self.screen = screen
        self.market = market
        self.color = color
        self.hp = hp
        self.dmg = dmg
        self.cost = cost
        self.snapbox = snapbox
        self.pos = None  # Initial position
        self.angle = 0   # Angle: 0 for normal, 90 for rotated
        self.width = width
        self.height = height

    def get_rect(self):
        if self.pos is not None:
            x, y = self.pos
        else:
            # Use a default container center (here, container 2) if no position was set.
            x, y = self.market.get_container_center(2)
        if self.angle == 90:
            w, h = self.height, self.width
        else:
            w, h = self.width, self.height
        return pygame.Rect(x - w // 2, y - h // 2, w, h)

    def draw(self):
        # Generic draw method draws a simple rectangle.
        rect = self.get_rect()
        pygame.draw.rect(self.screen, self.color, rect)

class Blöja(Defense):
    def __init__(self, screen, market, color, hp=5, dmg=1, cost=500, snapbox=35):
        super().__init__(screen, market, color, hp, dmg, cost, snapbox, width=20, height=48)

class Cannon(Defense):
    def __init__(self, screen, market, color, hp=250, dmg=1, cost=1000, snapbox=35):
        super().__init__(screen, market, color, hp, dmg, cost, snapbox, width=48, height=48)

    def draw(self):
        # For the Cannon, we no longer draw a blue box.
        # Instead, we use the actual cannon images (base and pipe) loaded by the Market.
        if self.pos is not None:
            center = self.pos
        else:
            # Default to container 0 for preview
            center = self.market.get_container_center(0)
        # You can adjust the rotation handling if required.
        base_rect = self.market.cannon_base.get_rect(center=center)
        pipe_rect = self.market.cannon_pipe.get_rect(center=center)
        self.screen.blit(self.market.cannon_base, base_rect)
        self.screen.blit(self.market.cannon_pipe, pipe_rect)