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
            self.has_front = kwargs.get("has_front", False)
            self.use_front = kwargs.get("use_front", False)

            self.been_selected = False
            self.selected = False
            self.pos = None
            self.angle = 0

            # Set width & height from the image if it exists
            if hasattr(self, "img") and self.img:
                self.width, self.height = self.img.get_size()
            else:
                self.width, self.height = 150, 150  # Default size

    def get_rect(self, use_front_img=False):
        """Returns a pygame.Rect centered on the object's position.
        
        If `use_front_img` is True and `self.front_img` exists, the rect is based on `front_img`.
        Otherwise, it uses `self.img`.
        """
        if self.pos is not None:
            x, y = self.pos
        else:
            x, y = 1, 3

        # Determine which image to use for size calculation
        img_to_use = self.front_img if use_front_img and self.front_img else self.img

        # Get the actual size of the selected image
        if img_to_use:
            w, h = img_to_use.get_size()
        else:
            w, h = self.width, self.height  # Default to class-defined width/height if no image

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
            if isinstance(self, defenses.cannon.Cannon):
                img2_rotated = pygame.transform.rotate(
                    self.img2_original, 
                    -(math.degrees(self.angle) - 90)
                )
                self.img2 = img2_rotated
                current_time = pygame.time.get_ticks()
                elapsed_time = current_time - self.start_time
                if elapsed_time >= self.delay:  # Use >= instead of ==
                    defenses.projectile.Projectile.fire(self)
                    self.start_time = current_time  # Optionally reset the timer


        else:
            self.angle = 0
            if isinstance(Defense, defenses.cannon.Cannon):
                self.img2 = self.img2_original()

    def draw(self):
        if self.use_front:
            if self.pos:
                print("hej")
                self.front_rect = self.get_rect(True)  # Use front_img if available
            self.screen.blit(self.front_img, self.front_rect)
        else:
            self.rect = self.get_rect()  # Use img if no front_img
            self.screen.blit(self.img, self.rect)
            if self.is_composite:
                self.screen.blit(self.img2, self.rect)

#Big ball cannon!
#vind
#bank