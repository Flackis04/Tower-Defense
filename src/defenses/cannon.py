import pygame
import enemies.enemies as enemies
import math
import economy  # for refunding when selling
import defenses.defense as defense
import defenses.projectile
import pygame

class Cannon(defense.Defense):
    def __init__(self, **kwargs):
        # Load images first so we can get their sizes
        self.img = pygame.image.load("assets/cannon/base.png").convert_alpha()  # Main cannon base
        self.img2 = pygame.image.load("assets/cannon/pipe.png").convert_alpha()  # Cannon pipe (front part)
        self.img2_original = self.img2.copy()  # Keep original for rotation

        # Get image dimensions before calling super()
        img_width, img_height = self.img.get_size()

        # Default values, using the image dimensions
        defaults = {
            "screen": pygame.display.get_surface(),
            "market": None,
            "enemies_list": enemies.enemies_list,
            "width": img_width,  # Default width is the image width
            "height": img_height,  # Default height is the image height
            "hp": 250,
            "dmg": 1,
            "cost": 1000,
            "scope": 200,
            "tags": ("default", "aim"),
            "is_composite": True,
            "preview": False,  # Cannon has a separate front part
        }

        # Merge defaults with any provided keyword arguments
        config = {**defaults, **kwargs}

        # Initialize the parent class
        super().__init__(**config)

        # Assign instance variables
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

        # Timing variables
        self.delay = 1250
        self.start_time = 0

        #self.elapsed_time = self.current_time-self.start_time
