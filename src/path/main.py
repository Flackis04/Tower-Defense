import pygame
import path.pathx as pathx
import pathdebug


# Assuming `screen` is your Pygame display surface
# path_points is the list of points returned from `generate_path_points`
# width is the desired width for the path polygon (e.g., 10)
def main():
    pygame.init()
    screen_width, screen_height = 1920, 1080
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
    clock = pygame.time.Clock()

    # Generate path points

    path_points = pathx.generate_path_points(screen_width, screen_height)

    while True:
        screen.fill((0, 0, 0))  # Fill the screen with black

        pathdebug.display_path_points(screen, path_points)
        pathdebug.display_polygon(screen, path_points, width=1)



        pygame.display.flip()  # Update the screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        clock.tick(60)  # Run the game at 60 FPS

if __name__ == "__main__":
    main()