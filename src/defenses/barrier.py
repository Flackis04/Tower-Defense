import pygame
import defenses.defense
import enemies.enemies as enemies

class Barrier(defenses.defense.Defense):
    def __init__(self, **kwargs):
        self.img = pygame.image.load("assets/defenses/barrier/barrier.png").convert_alpha()
        self.front_img = pygame.image.load("assets/defenses/barrier/barrier_front.png").convert_alpha()

        img_width, img_height = self.img.get_size()

        defaults = {
            "screen": pygame.display.get_surface(),
            "market": None,
            "enemies_list": enemies.enemies_list,
            "width": img_width,
            "height": img_height,
            "hp": 50,
            "dmg": 1,
            "cost": 500,
            "scope": False,
            "tags": ("other",),
            "is_composite": False,
            "preview": True,
            "img": self.img,                           
        }

        config = {**defaults, **kwargs}

        super().__init__(**config)

        self.screen = config["screen"]
        self.market = config["market"]
        self.enemies_list = config["enemies_list"]
        self.hp = config["hp"]
        self.dmg = config["dmg"]
        self.cost = config["cost"]
        self.scope = config["scope"]
        self.tags = config["tags"]
        self.is_composite = config["is_composite"]
        self.preview = config["preview"]

                                                              
        self.front_img = self.front_img or pygame.image.load("assets/barrier/barrier_front.png").convert_alpha()

                     
        self.pos = None
        self.angle = 0
        self.isrotated = False

    def find_closest_angle(self):
        pass

    def rotate(self):
        self.find_closest_angle()
        pass

"""         self.rect.height //= 8  # Reduce height while keeping the center unchanged
            pygame.draw.rect(self.screen, (255, 0, 0), self.rect, 2)"""