import pygame
import market
import math
import economy  # for refunding when selling
import defenses.defense
import enemies.enemies as enemies

class Mortar(defenses.defense.Defense):
    def __init__(self, **kwargs):
        # Load image first so we can get its size
        self.img = pygame.image.load("assets/mortar/mortar.png").convert_alpha()

        # Get image dimensions
        img_width, img_height = self.img.get_size()

        # Default values, using the image dimensions
        defaults = {
            "screen": pygame.display.get_surface(),
            "market": None,
            "enemies_list": enemies.enemies_list,
            "width": img_width,  # Use image width
            "height": img_height,  # Use image height
            "hp": 300,
            "dmg": 3,
            "cost": 5000,
            "scope": 300,
            "tags": ("default", "aim"),
            "is_composite": False,
            "has_front": False,
            "use_front": False,
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
        self.has_front = config["has_front"]

        # Update width and height to match the image
        self.width, self.height = self.img.get_size()

        # Set up rect using the image size
        self.rect = self.img.get_rect(center=(self.width // 2, self.height // 2))
        self.pos = None
