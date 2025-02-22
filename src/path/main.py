from pathgen import generate_path_points
import pygame
import pathgen
import reverser
import pathdebug

reverser_inst = reverser.Reverse()

# Assuming `screen` is your Pygame display surface
# path_points is the list of points returned from `generate_path_points`
# width is the desired width for the path polygon (e.g., 10)
def main():
    pygame.init()
    screen = pygame.display.set_mode((reverser_inst.screen_width, reverser_inst.screen_height))
    clock = pygame.time.Clock()

    # Generate path points

    path_points = pathgen.generate_path_points(reverser_inst.screen_width, reverser_inst.screen_height)

    reverser_inst.get_path_limits

    print(len(path_points))

    while True:
        screen.fill((0, 0, 0))  # Fill the screen with black

        # Display the path points
        pathdebug.display_path_points(screen, path_points)

        # Optionally display the path polygon
        pathdebug.display_polygon(screen, path_points, width=1)



        pygame.draw.rect(screen, (255,0,0), reverser_inst.rect)

        pygame.display.flip()  # Update the screen

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        clock.tick(60)  # Run the game at 60 FPS

if __name__ == "__main__":
    main()