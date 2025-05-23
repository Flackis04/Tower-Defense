import pygame
import path.pathx as pathx
import pathdebug

global screen_width, screen_height

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
                                                  
                                                                        
                                                            
def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
    clock = pygame.time.Clock()

                          

    path_points = pathx.generate_path_points(screen_width, screen_height)

    while True:
        screen.fill((0, 0, 0))                              

        pathdebug.display_path_points(screen, path_points)
        pathdebug.display_polygon(screen, path_points, width=1)



        pygame.display.flip()                     

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        clock.tick(60)                          

if __name__ == "__main__":
    main()