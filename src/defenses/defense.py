import pygame
import economy

class Defense:

    local_container_index = 0
    def __init__(self, screen, market, width, height, hp, dmg, cost, snapbox, scope, type, has_front, front_img=False):

        self.market = market
        self.screen = screen
        self.hp = hp
        self.dmg = dmg
        self.cost = cost
        self.snapbox = snapbox
        self.pos = None  # Initial position
        self.angle = 0   # Angle: 0 for normal, 90 for rotated
        self.width = width
        self.height = height
        self.type = type
        self.selected = False
        self.scope = scope
        self.othertypes = [] #3rd category
        self.front_img = front_img
        self.hasfront = has_front
        self.container_index = None

                
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
    
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # If the cannon itself is clicked, toggle its selection.
            if self.get_rect().collidepoint(mouse_pos):
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
    
    def get_sell_button_rect(self):
        # Get the defense's rectangle as drawn.
        defense_rect = self.get_rect()
        # Define the sell button dimensions.
        button_width = defense_rect.width / 1.5
        button_height = 15
        # Position the button centered below the defense with a small gap.
        button_x = defense_rect.centerx - button_width // 2
        button_y = defense_rect.bottom + 10
        return pygame.Rect(button_x, button_y, button_width, button_height)

    def draw(self, front_img):
        
        if self.selected and self.type == "default":
            sell_button_rect = self.get_sell_button_rect()
            pygame.draw.rect(self.screen, (200, 0, 0), sell_button_rect)
            sell_font = pygame.font.SysFont(None, 20)
            text_surface = sell_font.render("Sell", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=sell_button_rect.center)
            self.screen.blit(text_surface, text_rect)

        if isinstance(self, Defense) and economy.balance >= self.cost:
            self.draw()
            if self.hasfront == True and self.front_img == True:
                self.draw_front_img()
        else:
            darkness_filter = self.copy()
            dark_surface = pygame.Surface(darkness_filter.get_size(), pygame.SRCALPHA)
            dark_surface.fill((0, 0, 0, 128))  # 50% transparent black
            darkness_filter.blit(dark_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(darkness_filter, self.rect)

#Big ball cannon!
#vind
#bank