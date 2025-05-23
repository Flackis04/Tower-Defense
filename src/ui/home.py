import pygame
import pygame

class Home:
    def __init__(self, screen, bg_color=(0, 0, 0)):                    
        self.screen = screen
        self.bg_color = bg_color

    def draw(self):
        self.screen.fill(self.bg_color)                                             
        pygame.display.flip()                      