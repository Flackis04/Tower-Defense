import pygame
import enemies.enemies as enemy
import math
import economy                              
import defenses.defense as defense
import defenses.projectile

class Cannon(defense.Defense):
    def __init__(self, **kwargs):
                                                               
        self.img = pygame.image.load("assets/defenses/cannon/base.png").convert_alpha()                    
        self.img2 = pygame.image.load("assets/defenses/cannon/pipe.png").convert_alpha()                            
        self.img2_original = self.img2.copy()                                              

        img_width, img_height = self.img.get_size()

        defaults = {
            "screen": pygame.display.get_surface(),
            "market": None,
            "enemies_list": enemy.enemies_list,
            "width": img_width,                                    
            "height": img_height,                                      
            "hp": 250,
            "dmg": 1,
            "cost": 1000,
            "scope": 200,
            "tags": ("default", "aim"),
            "is_composite": True,                                      
            "preview": True,                
            "img": self.img,                           
            "img2": self.img2,
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

                                                        
        self.delay = 1250
        self.start_time = 0
        self.elapsed_time = 0

                                                         
        self.projectiles = []