import pygame

class Projectile:
    def __init__(self, screen, startx=100, starty=100):
        self.screen = screen                            
        self.width, self.height = screen.get_size()
        self.dia = 25
        self.startx = startx
        self.starty = starty
        self.rect = pygame.Rect(self.startx, self.starty, self.dia, self.dia)
        self.speed = 5               

    def fire(self):
        print("Fire!")
                               

    def draw_projectile(self, screen):
        """Draw the projectile (for debugging or effect purposes)."""
                                                           