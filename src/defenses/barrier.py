import pygame
import defenses.defense as defense
import market as market
import math

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

    
    def ondrag(self, mouse_pos):
        """Handles orientation updates while dragging for this defense.
        This method rotates the defense image according to self.angle.
        """
        # Assume self.barrier is the original image (for Barrier defenses).
        rotated_image = pygame.transform.rotate(self.barrier, self.angle)
        # Center the rotated image on the current mouse position.
        rotated_rect = rotated_image.get_rect(center=mouse_pos)
        self.screen.blit(rotated_image, rotated_rect)



    def draw(self):
        if hasattr(self, 'pos') and self.pos is not None:
            if self.front_img == True:
                self.front_rect = self.barrier_front.get_rect(center=self.pos)
                self.screen.blit(self.barrier_front, self.front_rect)

            else:
                self.front_img == False
                self.rect = self.barrier.get_rect(center=self.pos)
                self.screen.blit(self.barrier, self.rect)

    def draw_front_img(self):
        self.screen.blit(self.barrier_front, self.front_rect)