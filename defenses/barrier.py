import pygame
import defenses.defense as defense
import market as market
import math

class Barrier(defense.Defense):
    def __init__(self, screen, market, width=50, height=50, hp=5, dmg=1, cost=500, snapbox=35, type="other", hasfront=True, front_img=False):
        super().__init__(screen, market, width, height, hp, dmg, cost, snapbox, type, "other", hasfront, front_img)
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

    
    def ondrag(self, mouse_pos):
        """Handles orientation updates while dragging for this defense.
        This method rotates the defense image according to self.angle.
        """
        # Assume self.barrier is the original image (for Barrier defenses).
        rotated_image = pygame.transform.rotate(self.barrier, self.angle)
        # Center the rotated image on the current mouse position.
        rotated_rect = rotated_image.get_rect(center=mouse_pos)
        self.screen.blit(rotated_image, rotated_rect)
        print(f"ondrag: Rotated to {self.angle} degrees at {mouse_pos}")



    def draw(self):
        if hasattr(self, 'pos') and self.pos is not None:
            if self.front_img == True:
                self.front_rect = self.barrier_front.get_rect(center=self.pos)
                self.screen.blit(self.barrier_front, self.front_rect)

            else:
                self.rect = self.barrier.get_rect(center=self.pos)
                self.screen.blit(self.barrier, self.rect)

    def draw_front_img(self):
        self.screen.blit(self.barrier_front, self.front_rect)