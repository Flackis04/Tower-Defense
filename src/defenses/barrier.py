import pygame
import defenses.defense as defense
import path.pathgen

class Barrier(defense.Defense):
    def __init__(self, screen, market, enemy_list, width, height, hp, dmg, cost, scope, tags, has_front, front_img):
        super().__init__(screen, market, enemy_list, width, height, hp, dmg, cost, scope, tags, has_front, front_img)
        
        # Load images
        self.barrier = pygame.image.load("assets/barrier/barrier.png").convert_alpha()
        self.barrier_front = pygame.image.load("assets/barrier/barrier_front.png").convert_alpha()
        
        # Scale images by 2.2x
        original_width, original_height = self.barrier.get_size()
        new_size = (int(original_width * 2.2), int(original_height * 2.2))
        new_size2 = (int(original_width * 1.5), int(original_height * 1.6))
        self.barrier = pygame.transform.scale(self.barrier, new_size)
        self.barrier_front = pygame.transform.scale(self.barrier_front, new_size2)
        self.barrier_original = self.barrier.copy()
        
        # Set up rects using the scaled image; initial center at half the given width and height
        self.rect = self.barrier.get_rect(center=(self.width // 2, self.height // 2))
        self.front_rect = self.barrier_front.get_rect(center=(self.width // 2, self.height // 2))
        
        self.pos = None
        self.angle = 0
        self.isrotated =False

    def find_closest_angle(self):
        pass
    def rotate(self):
        self.find_closest_angle()
        pass

    def draw(self):
        if self.front_img:
            if self.pos:
                self.front_rect = self.barrier_front.get_rect(center=self.pos)
            self.screen.blit(self.barrier_front, self.front_rect)
        else:
            self.rect = self.barrier.get_rect(center=self.pos)
            self.rect.height //= 8  # Reduce height while keeping the center unchanged

            self.screen.blit(self.barrier, self.rect)
            pygame.draw.rect(self.screen, (255, 0, 0), self.rect, 2)
