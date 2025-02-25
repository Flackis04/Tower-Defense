import pygame
import path.pathgen
import defenses.barrier as barrier

class Reverse(barrier.Barrier):
    def __init__(self, screen, market, enemy_list, width, height, hp, dmg, cost, scope, tags, has_front, front_img):
        super().__init__(screen, market, enemy_list, width, height, hp, dmg, cost, scope, tags, has_front, front_img)
        self.start_point = None
        self.end_point = None
        self.scope = scope
        x, y = 0, 0
        x, y = pygame.mouse.get_pos()
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.get_path_limits()


    def get_path_limits(self):
        points = path.pathgen.generate_path_points(800, 600)

        #adda för y kordinater senare när jag skaffar nya mappar

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

    def draw(self):    
        pygame.draw.rect(self.screen, (0,45,128), self.rect)