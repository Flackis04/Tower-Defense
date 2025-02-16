import pygame
import defenses.defense as defense

class Blöja(defense.Defense):
    def __init__(self, screen, market, color, hp=5, dmg=1, cost=500, snapbox=35):
        super().__init__(screen, market, color, hp, dmg, cost, snapbox, width=20, height=48, type="on_land")
    
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