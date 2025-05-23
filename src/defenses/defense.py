import pygame
import economy
import utils
import utils.collision
import math
import enemies.enemies as enemies
import defenses.projectile

import pygame

class Defense:
    local_container_index = 0

    def __init__(self, **kwargs):
        self.screen = kwargs.get("screen", pygame.display.get_surface())
        self.market = kwargs.get("market", None)
        self.enemies_list = kwargs.get("enemies_list", [])
        self.hp = kwargs.get("hp", 250)
        self.dmg = kwargs.get("dmg", 1)
        self.cost = kwargs.get("cost", 1000)
        self.scope = kwargs.get("scope", 400)
        self.tags = kwargs.get("tags", ())
        self.is_composite = kwargs.get("is_composite", False)
        self.preview = kwargs.get("preview", True)

        self.been_selected = False
        self.selected = False
        self.pos = kwargs.get("pos", (0, 0))                    

        self.angle = 0
        self.S = 2 if self.preview else 3                  
        self.scale_factor = (38 / 800) * self.S                        

                     
        self.img = kwargs.get("img")
        self.img2 = kwargs.get("img2") if self.is_composite else None

        if not self.img:
            raise ValueError("No image provided for Defense instance.")

        self.original_img = self.img
        self.original_size = self.original_img.get_size()

        if self.is_composite and self.img2:
            self.original_img2 = self.img2
            self.original_size2 = self.original_img2.get_size()
        else:
            self.original_img2 = self.img
            self.original_size2 = self.original_size

                       
        self.apply_scaling()

    def apply_scaling(self):
        """Scales images based on the computed scale factor."""
        new_size = (int(self.original_size[0] * self.scale_factor), int(self.original_size[1] * self.scale_factor))
        self.img = pygame.transform.smoothscale(self.original_img, new_size)

        if self.is_composite and self.img2:
            new_size2 = (int(self.original_size2[0] * self.scale_factor), int(self.original_size2[1] * self.scale_factor))
            self.img2 = pygame.transform.smoothscale(self.original_img2, new_size2)

        self.width, self.height = self.img.get_size()                         

    def get_rect(self):
        """Returns a pygame.Rect centered on the object's position."""
        x, y = self.pos
        return pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)

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

    def get_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_closest_enemy(self):
        closest_enemy = None
        scope_distance = self.scope

        for enemy in enemies.enemies_list:
            distance = self.get_distance(self.pos, (enemy.posx, enemy.posy))
                                                                                        

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
                                                      
            if isinstance(self, defenses.cannon.Cannon):                       
                new_size = (int(self.original_size[0] * self.scale_factor), int(self.original_size[1] * self.scale_factor))
                img2_rotated = pygame.transform.smoothscale(self.original_img2, new_size)
                img2_rotated = pygame.transform.rotate(
                    img2_rotated, 
                    -(math.degrees(self.angle) + 90)
                )
                self.img2 = img2_rotated
                
                current_time = pygame.time.get_ticks()
                elapsed_time = current_time - self.start_time
                if elapsed_time >= self.delay:                        
                    defenses.projectile.Projectile.fire(self)
                    self.start_time = current_time                              


        else:
            self.angle = 0

    def draw(self):
        """Draws the defense unit on the screen."""
        if not self.screen:
            return

        img_rect = self.get_rect()
        self.screen.blit(self.img, img_rect)

        if self.is_composite and self.img2:
            img2_rect = self.img2.get_rect(center=img_rect.center)
            self.screen.blit(self.img2, img2_rect)

                 
     
     