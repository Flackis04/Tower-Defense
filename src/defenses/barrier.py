import pygame
import defenses.defense as defense

class Barrier(defense.Defense):
    def __init__(self, screen, market, enemy_list, width=50, height=50, hp=50, dmg=1, cost=500, snapbox=35, type="other", hasfront=False, front_img=False):
        super().__init__(screen, market, enemy_list, width, height, hp, dmg, cost, snapbox, type, "other", hasfront, front_img)
        self.barrier = pygame.image.load("assets/barrier/barrier.png").convert_alpha()
        self.barrier_front = pygame.image.load("assets/barrier/barrier_front.png").convert_alpha()
        self.barrier_original = self.barrier.copy()
        self.rect = self.barrier.get_rect(center=(self.width // 2, self.height // 2))
        self.front_rect = self.barrier_front.get_rect(center=(self.width // 2, self.height // 2))
        original_barrier = self.barrier_original.copy()
        barrier_width, barrier_height = original_barrier.get_size()
        offset_surface = pygame.Surface((barrier_width, barrier_height), pygame.SRCALPHA)
        offset_surface.blit(original_barrier, (0, 0))
        self.pos = None
        self.angle = 0
        self.canrotate =False

    def draw(self):
        if self.front_img == True:
            self.front_rect = self.barrier_front.get_rect(center=self.pos)
            self.screen.blit(self.barrier_front, self.front_rect)

        else:
            if self.angle == 90 and self.canrotate == True:
                self.canrotate = False
                self.barrier = pygame.transform.rotate(self.barrier, self.angle)
            else:
                self.canrotate=True
            self.rect = self.barrier.get_rect(center=self.pos)
            self.screen.blit(self.barrier, self.rect)