import pygame
import defenses.defense as defense
import market as market

class Barrier(defense.Defense):
    def __init__(self, screen, market, width=50, height=50, hp=5, dmg=1, cost=500, snapbox=35, type="other", hasfront=True):
        super().__init__(screen, market, width, height, hp, dmg, cost, snapbox, type, "other", hasfront)
        self.isfront = False
        self.screen = screen
        self.barrier = pygame.image.load("assets/barrier/barrier.png").convert_alpha()
        self.barrier_front = pygame.image.load("assets/barrier/barrier_front.png").convert_alpha()
        self.barrier_original = self.barrier.copy()
        self.center = self.market.get_container_center(0)
        self.rect = self.barrier.get_rect(center=self.center)
        self.front_rect = self.barrier_front.get_rect(center=self.center)
        original_barrier = self.barrier_original.copy()
        barrier_width, barrier_height = original_barrier.get_size()
        offset_surface = pygame.Surface((barrier_width, barrier_height), pygame.SRCALPHA)
        offset_surface.blit(original_barrier, (0, 0))
        self.pos = None
        self.market = market

    def ondrag(self, screen):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.orientation, _ = self.market.get_continuous_path_orientation((mouse_x, mouse_y))
        self.angle = 90 if self.orientation == "vertical" else 0 
        if self.orientation == "vertical":
            self.market.defenselist[1].angle = 90
        else:
            self.market.defenselist[1].angle = 0
        return self.market.defenselist[1].draw()

    def draw(self):
        if hasattr(self, 'pos') and self.pos is not None:
            if self.isfront:
                self.front_rect = self.barrier_front.get_rect(center=self.pos)
                self.screen.blit(self.barrier_front, self.front_rect)

            else:
                self.rect = self.barrier.get_rect(center=self.pos)
                self.screen.blit(self.barrier, self.rect)