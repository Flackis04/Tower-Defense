import pygame
import path.pathx as pathx

def display_path_points(screen, path_points, radius=3):
    """
    Draw the generated path points on the screen.
    """
    for point in path_points:
        pygame.draw.circle(screen, (255, 0, 0), point, radius)

def display_polygon(screen, path_points, width):
    """
    Draw the path polygon with a constant width.
    """
    polygon_points = pathx.get_path_polygon(path_points, width)
    pygame.draw.polygon(screen, (0, 255, 0), polygon_points, width=2)

# Assuming `screen` is your Pygame display surface
# path_points is the list of points returned from `generate_path_points`
# width is the desired width for the path polygon (e.g., 10)
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Generate path points
    width, height = 800, 600
    path_points = pathx.generate_path_points(width, height)

    while True:
        screen.fill((0, 0, 0))  # Fill the screen with black

        # Display the path points
        display_path_points(screen, path_points)

        # Optionally display the path polygon
        display_polygon(screen, path_points, width=1)

        print(len(path_points))

        pygame.display.flip()  # Update the screen

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        clock.tick(60)  # Run the game at 60 FPS

if __name__ == "__main__":
    main()
