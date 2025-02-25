import pygame

class Projectile:
    def __init__(self, screen, startx=100, starty=100):
        self.screen = screen  # ✅ Store screen reference
        self.width, self.height = screen.get_size()
        self.dia = 25
        self.startx = startx
        self.starty = starty
        self.rect = pygame.Rect(self.startx, self.starty, self.dia, self.dia)
        self.speed = 5  # ✅ Set speed

    def fire(self):
        print("Fire!")
        self.rect.x += self.speed 

    def draw_projectile(self, screen):
        """Draw the projectile (for debugging or effect purposes)."""
        pygame.draw.rect(screen, (200, 0, 0), self.rect)
