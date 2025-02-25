import pygame
import economy
import utils
import utils.collision
import math
import enemies
import defenses.projectile

class Defense:

    local_container_index = 0
    def __init__(self, screen, market, enemy_list, width, height, hp, dmg, cost, scope, tags, has_front, front_img):
        self.screen = screen
        self.market = market
        self.enemies_list = enemy_list
        self.width = width
        self.height = height
        self.hp = hp
        self.dmg = dmg
        self.cost = cost
        self.scope = scope
        self.tags = tags
        self.has_front = has_front
        self.front_img = front_img

        self.selected = False
        self.pos = None
        self.angle = 0
                
    def get_rect(self):
        if self.pos is not None:
            x, y = self.pos
        else:
            x, y = 1,3
        w, h = self.height*1.25, self.width*1.25
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
    
    def check_collisions(enemies_list, market_instance, barrier_inst):
        """
        Process collisions between enemies and defenses (specifically barriers).
        If a collision occurs, adjust HP accordingly and schedule objects for removal.
        """
        enemies_to_remove = []
        defenses_to_remove = []
        for enemy in enemies_list:
            enemy_center = (enemy.posx, enemy.posy)
            for defense in market_instance.placed_defenses:
                # For barriers, use the barrier instance's rect.
                if defense == barrier_inst:
                    defense_rect = barrier_inst.rect
                    if utils.collision.circle_rect_collision(enemy_center, enemy.radius, defense_rect):
                        enemy.hp -= defense.dmg
                        defense.hp -= 1
                        if enemy.hp <= 0:
                            enemies_to_remove.append(enemy)
                            economy.balance += enemy.reward
                        if defense.hp <= 0:
                            defenses_to_remove.append(defense)
        for enemy in enemies_to_remove:
            if enemy in enemies_list:
                enemies_list.remove(enemy)
        for defense in defenses_to_remove:
            if defense in market_instance.placed_defenses:
                market_instance.placed_defenses.remove(defense)

    def update_defenses_events(market_instance, event_list, cached_mouse_pos):
        """
        Update defenses that require aiming and event handling.
        """
        
        for defense in market_instance.placed_defenses:
            if "aim" in defense.tags:
                defense.aim_at_enemy()
                for event in event_list:
                    defense.handle_event(event, cached_mouse_pos)

    def get_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_closest_enemy(self):
        closest_enemy = None
        scope_distance = self.scope
        # Reference the global enemy list from the enemies module
        for enemy in enemies.enemies_list:
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
            if isinstance(Defense, defenses.cannon.Cannon):
                rotated_pipe = pygame.transform.rotate(self.cannon_pipe_original, -(math.degrees(self.angle) - 90))
                self.cannon_pipe = rotated_pipe
                current_time = pygame.time.get_ticks()
                elapsed_time = current_time - self.start_time
                if elapsed_time == self.delay:
                    defenses.projectile.Projectile.fire()

        else:
            self.angle = 0
            if isinstance(Defense, defenses.cannon.Cannon):
                self.cannon_pipe = self.cannon_pipe_original.copy()

    def draw(self, front_img):
        
        if self.selected and self.type == "default":
            sell_button_rect = self.get_sell_button_rect()
            pygame.draw.rect(self.screen, (200, 0, 0), sell_button_rect)
            sell_font = pygame.font.SysFont(None, 20)
            text_surface = sell_font.render("Sell", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=sell_button_rect.center)
            self.screen.blit(text_surface, text_rect)

#Big ball cannon!
#vind
#bank