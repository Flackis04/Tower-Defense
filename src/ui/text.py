import pygame
import economy

class Balance_Display:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.color = (255, 255, 255)
        self.x = 10
        self.y = 10
        
    def draw(self):
        text = self.font.render(f"Balance: {economy.balance}", True, self.color)
        self.screen.blit(text, (self.x, self.y))

    def update(self):
        self.draw()