import pygame
import defenses.defense as defense

class Barrier(defense.Defense):
    def __init__(self, screen, market, width=50, height=50, hp=5, dmg=1, cost=500, snapbox=35, type="on_land"):
        super().__init__(screen, market, width, height, hp, dmg, cost, snapbox, type, "on_land")
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
    def ondrag(self,screen, cached_mouse_pos):
            mouse_x, mouse_y = cached_mouse_pos
            orientation, _ = self.get_continuous_path_orientation((mouse_x, mouse_y))
            self.angle = 90 if orientation == "vertical" else 0
            if self.angle == 90:
                width, height = self.height, self.width
            else:
                width, height = self.width, self.height
            drag_rect = pygame.Rect(mouse_x - width // 2, mouse_y - height // 2, width, height)
            pygame.draw.rect(screen, self.color, drag_rect)

    def draw(self):
        if hasattr(self, 'pos') and self.pos is not None:
            if self.isfront:
                self.front_rect = self.barrier_front.get_rect(center=self.pos)
                self.screen.blit(self.barrier_front, self.front_rect)

            else:
                self.rect = self.barrier.get_rect(center=self.pos)
                self.screen.blit(self.barrier, self.rect)


