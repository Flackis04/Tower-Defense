import pygame
import path.pathx
import defenses.barrier as barrier
import enemies.enemies as enemies

class Reverse(barrier.Barrier):
    def __init__(self, **kwargs):
        defaults = {
            "screen": pygame.display.get_surface(),
            "market": None,
            "enemies_list": enemies.enemies_list,
            "width": 35,
            "height": 50,
            "hp": 50,
            "dmg": 1,
            "cost": 500,
            "scope": 50,
            "tags": ("other",),
            "is_composite": False,
            "has_front": False,
            "use_front": False,
        }
        defaults.update(kwargs)
        super().__init__(**defaults)
        

        self.start_point = None
        self.end_point = None
        x, y = 0, 0
        x, y = pygame.mouse.get_pos()
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.get_path_limits()


    def get_path_limits(self):
        points = path.pathx.generate_path_points(800, 600)

                                                                

        for point in points:
            if point[0] == 0 and self.start_point ==None:
                self.start_point = point
            elif point[0] > 0 and self.start_point == None:
                self.start_point = (0, point[1])
            if point[0] == 800 and self.end_point ==None:
                self.end_point = point
            elif point[0] > 800 and self.end_point == None:
                self.end_point = (800, point[1])
        if self.end_point == None:
            self.end_point = (800, points[-1][1])

    def scope(self):
        import market
        market_inst = market.Market
        if market_inst.is_near_path:
            print("yes")