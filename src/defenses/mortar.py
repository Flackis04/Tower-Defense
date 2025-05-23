import pygame
import market
import math
import economy                              
import defenses.defense
import enemies.enemies as enemies

class Mortar(defenses.defense.Defense):
    def __init__(self, **kwargs):

        self.img = pygame.image.load("assets/defenses/mortar/mortar.png").convert_alpha()

        img_width, img_height = self.img.get_size()

        defaults = {
            "screen": pygame.display.get_surface(),
            "market": None,
            "enemies_list": enemies.enemies_list,
            "width": img_width,                   
            "height": img_height,                    
            "hp": 300,
            "dmg": 3,
            "cost": 5000,
            "scope": 300,
            "tags": ("default", "aim"),
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
