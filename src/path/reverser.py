import pygame
import pathgen

class Reverse:
    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.width = 25
        self.height = 100
        self.start_point = None
        self.end_point = None

        self.get_path_limits()
        
        self.rect = pygame.Rect(self.start_point[0], self.start_point[1], self.width, self.height)

    def get_path_limits(self):
        points = pathgen.generate_path_points(self.screen_width, self.screen_height)

        #adda för y kordinater senare när jag skaffar nya mappar

        for point in points:
            if point[0] == 0 and self.start_point ==None:
                self.start_point = point
            elif point[0] > 0 and self.start_point == None:
                self.start_point = (0, point[1])
            if point[0] == self.screen_width and self.end_point ==None:
                self.end_point = point
            elif point[0] > self.screen_width and self.end_point == None:
                self.end_point = (self.screen_width, point[1])
        if self.end_point == None:
            self.end_point = (self.screen_width, points[-1][1])

    def scope(self):
        pass