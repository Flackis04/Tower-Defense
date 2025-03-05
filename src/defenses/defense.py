import pygame
import economy
import utils
import utils.collision
import math
import enemies.enemies as enemies
import defenses.projectile

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
            self.preview = kwargs.get("preview", False)

            self.been_selected = False
            self.selected = False
            self.pos = None
            self.angle = 0
            self.scale_factor = 2.5
            self.preview_scale_factor = 1
            self.original_img = self.img
            if self.is_composite:
                self.original_img2 = self.img2
            else:
                self.original_img2 = self.img

                        # Determine the scale factor for img based on the preview state
            self.resulting_scale_factor = 32 * self.preview_scale_factor if self.preview else 32 * self.scale_factor

            # Apply scaling to img
            self.img = pygame.transform.smoothscale(self.img, (self.resulting_scale_factor, self.resulting_scale_factor))

            # Handle scaling for composite images
            if self.is_composite:
                # Scale img2 based on preview state
                self.img2 = pygame.transform.smoothscale(self.img2, (self.resulting_scale_factor, self.resulting_scale_factor))
                self.original_img2 = pygame.transform.smoothscale(self.original_img2, (self.resulting_scale_factor, self.resulting_scale_factor))


            # Set width & height from the image if it exists
            if hasattr(self, "img") and self.img:
                self.width, self.height = self.img.get_size()
            else:
                self.width, self.height = 150, 150  # Default size

    def get_rect(self, preview=False):
        """Returns a pygame.Rect centered on the object's position.

        If `preview` is True and `self.front_img` exists, the rect is based on `front_img`,
        smoothscaled properly. Otherwise, it uses `self.img`.
        """
        # Use the object's position, or fallback to a default if not set
        if self.pos is not None:
            x, y = self.pos
        else:
            x, y = 1, 3
            print("WoWWW")

        original_w, original_h = self.original_img.get_size()  # This should be (800, 800)
        w, h = int(original_w * self.resulting_scale_factor), int(original_h * self.resulting_scale_factor)

        # Create and return a rect centered on (x, y)
        return pygame.Rect(x - w // 2, y - h // 2, w, h)




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

    def get_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_closest_enemy(self):
        closest_enemy = None
        scope_distance = self.scope

        for enemy in enemies.enemies_list:
            distance = self.get_distance(self.pos, (enemy.posx, enemy.posy))
            # Now you can use 'distance' as needed, e.g. check if the enemy is in range.

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
            if isinstance(self, defenses.cannon.Cannon): #smooth aim transition
                img2_rotated = pygame.transform.rotate(
                    self.original_img2, 
                    -(math.degrees(self.angle) + 90)
                )
                self.img2 = img2_rotated
                
                current_time = pygame.time.get_ticks()
                elapsed_time = current_time - self.start_time
                if elapsed_time >= self.delay:  # Use >= instead of ==
                    defenses.projectile.Projectile.fire(self)
                    self.start_time = current_time  # Optionally reset the timer


        else:
            self.angle = 0

    def draw(self):
        # Get the appropriate image rectangle based on the preview state
        if self.preview:
            print("1")
            # Use front image if preview is True and front_img exists
            img_rect = self.get_rect(preview=True)  # Get the rect for preview scaling
            self.screen.blit(self.img, img_rect)  # Blit front_img or img based on preview
            
            # If composite, draw the second image as well
            if self.is_composite:
                img2_rect = self.img2.get_rect(center=img_rect.center)  # Align with main image
                self.screen.blit(self.img2, img2_rect)

        else:
            print("2")
            # If preview is False, display the regular image
            img_rect = self.get_rect(preview=False)  # Get the rect for regular scaling
            self.screen.blit(self.img, img_rect)

            # If the object is composite, draw the second image as well
            if self.is_composite:
                img2_rect = self.img2.get_rect(center=img_rect.center)  # Align with main image
                self.screen.blit(self.img2, img2_rect)



#Big ball cannon!
#vind
#bank