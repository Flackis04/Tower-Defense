import pygame
import market
import math
import economy  # for refunding when selling

class Defense:
    def __init__(self, screen, market, color, hp, dmg, cost, snapbox, width, height):
        self.screen = screen
        self.market = market
        self.color = color
        self.hp = hp
        self.dmg = dmg
        self.cost = cost
        self.snapbox = snapbox
        self.pos = None  # Initial position
        self.angle = 0   # Angle: 0 for normal, 90 for rotated
        self.width = width
        self.height = height

    def get_rect(self):
        if self.pos is not None:
            x, y = self.pos
        else:
            # Use a default container center (here, container 2) if no position was set.
            x, y = self.market.get_container_center(2)
        if self.angle == 90:
            w, h = self.height, self.width
        else:
            w, h = self.width, self.height
        return pygame.Rect(x - w // 2, y - h // 2, w, h)

    def draw(self):
        # Generic draw method draws a simple rectangle.
        rect = self.get_rect()
        pygame.draw.rect(self.screen, self.color, rect)

class Blöja(Defense):
    def __init__(self, screen, market, color, hp=5, dmg=1, cost=500, snapbox=35):
        super().__init__(screen, market, color, hp, dmg, cost, snapbox, width=20, height=48)
    
    def ondrag(self,screen, cached_mouse_pos):
            mouse_x, mouse_y = cached_mouse_pos
            orientation, _ = self.get_continuous_path_orientation((mouse_x, mouse_y))
            self.angle = 90 if orientation == "vertical" else 0
            if self.angle == 90:
                width, height = 50, 20
            else:
                width, height = 20, 50
            drag_rect = pygame.Rect(mouse_x - width // 2, mouse_y - height // 2, width, height)
            pygame.draw.rect(screen, self.color, drag_rect)

class Cannon(Defense):
    def __init__(self, screen, market, color, scope=200, hp=250, dmg=1, cost=1000, snapbox=35):
        super().__init__(screen, market, color, hp, dmg, cost, snapbox, width=48, height=48)
        self.scope = scope
        # Create instance-specific images for the cannon's pipe and base.
        original_pipe = market.cannon_pipe_original.copy()
        pipe_width, pipe_height = original_pipe.get_size()
        # Create a new transparent surface of the same size.
        offset_surface = pygame.Surface((pipe_width, pipe_height), pygame.SRCALPHA)
        offset_surface.fill((0, 0, 0, 0))
        # Blit the original image onto the new surface at (5, 0) to shift it 5 pixels to the right.
        offset_surface.blit(original_pipe, (5, 0))
        self.pipe_original = offset_surface.copy()
        self.pipe = self.pipe_original.copy()
        self.base = market.cannon_base  # optionally create a copy if needed
        # New attribute to track if this cannon is selected (pressed on)
        self.selected = False

    def get_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_closest_enemy(self):
        enemies = self.market.enemies_list
        closest_enemy = None
        scope_distance = self.scope
        for enemy in enemies:
            distance = self.get_distance(self.pos, enemy.get_position())
            if distance < scope_distance:
                scope_distance = distance
                closest_enemy = enemy
        return closest_enemy
    
    def get_angle_to(self, enemy):
        dx = enemy.posx - self.pos[0]
        dy = enemy.posy - self.pos[1]
        return math.atan2(dy, dx)
    
    def aim_at_enemy(self):
        enemy = self.get_closest_enemy()
        if enemy and self.pos:
            self.angle = self.get_angle_to(enemy)
            # Rotate the instance-specific pipe image.
            rotated_pipe = pygame.transform.rotate(self.pipe_original, -(math.degrees(self.angle) - 90))
            self.pipe = rotated_pipe
        else:
            self.angle = 0
            self.pipe = self.pipe_original.copy()
    
    def get_sell_button_rect(self):
        # Get the cannon's rectangle as drawn.
        canon_rect = self.get_rect()
        # Define the sell button dimensions.
        button_width = canon_rect.width // 2
        button_height = 20
        # Position it centered below the cannon with a small gap.
        button_x = canon_rect.centerx - button_width // 2
        button_y = canon_rect.bottom + 5
        return pygame.Rect(button_x, button_y, button_width, button_height)
    
    def handle_event(self, event, mouse_pos):
        # Get the cannon's area.
        canon_rect = self.get_rect()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # If the cannon itself is clicked, toggle its selection.
            if canon_rect.collidepoint(mouse_pos):
                self.selected = not self.selected
            # If already selected, check if the sell button was clicked.
            elif self.selected:
                sell_button_rect = self.get_sell_button_rect()
                if sell_button_rect.collidepoint(mouse_pos):
                    # Refund half the cost and remove this cannon from placed defenses.
                    refund = self.cost // 2
                    economy.balance += refund
                    if self in self.market.placed_defenses:
                        self.market.placed_defenses.remove(self)
    
    def draw(self):
        if self.pos is not None:
            center = self.pos
        else:
            center = self.market.get_container_center(0)
        base_rect = self.base.get_rect(center=center)
        pipe_rect = self.pipe.get_rect(center=center)
        self.screen.blit(self.base, base_rect)
        self.screen.blit(self.pipe, pipe_rect)
        # If this cannon is selected, display the sell button under it.
        if self.selected:
            sell_button_rect = self.get_sell_button_rect()
            # Draw a red rectangle as the sell button background.
            pygame.draw.rect(self.screen, (200, 0, 0), sell_button_rect)
            sell_font = pygame.font.SysFont(None, 20)
            text_surface = sell_font.render("Sell", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=sell_button_rect.center)
            self.screen.blit(text_surface, text_rect)