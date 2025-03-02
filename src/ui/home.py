import pygame
import pygame

class Home:
    def __init__(self, screen, bg_color=(0, 0, 0)):  # Default to black
        self.screen = screen
        self.bg_color = bg_color

    def draw(self):
        self.screen.fill(self.bg_color)  # Fill the screen with the background color
        pygame.display.flip()  # Update the display