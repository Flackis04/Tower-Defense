from pathgen import generate_path_points
import pygame
import pathgen
import defenses.reverser as reverser

reverser_inst = reverser.Reverse()

# Assuming `screen` is your Pygame display surface
# path_points is the list of points returned from `generate_path_points`
# width is the desired width for the path polygon (e.g., 10)
def main():
    pygame.init()
    # Use the instance's screen dimensions for the window size.
    screen = pygame.display.set_mode((reverser_inst.screen_width, reverser_inst.screen_height))
    clock = pygame.time.Clock()

    # Generate path points.
    path_points = pathgen.generate_path_points(reverser_inst.screen_width, reverser_inst.screen_height)

    # Call the method to compute path limits (note the parentheses).
    reverser_inst.get_path_limits()

    # Calculate angles for each point on the path.
    pathgen.calculate_angle(path_points)

    # Initialize x, y to (0, 0) (previously 'x,y = 0' is invalid).

    running = True
    while running:
        # Process events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with black.
        screen.fill((0, 0, 0))
        
        # Get the path polygon using a defined path width.
        # If 'pathgen.path_width' isn't defined in pathgen, you can use the global 'path_width' variable.
        path_polygon = pathgen.get_path_polygon(path_points, pathgen.path_width)
        pygame.draw.polygon(screen, (45, 45, 45), path_polygon)
        
        # Get the current mouse position.
        x, y = pygame.mouse.get_pos()
        
        # Optionally, update rect position and draw it.
        reverser_inst.rect.topleft = (x, y)
        pygame.draw.rect(screen, (255, 0, 0), reverser_inst.rect)

        


        pygame.display.flip()  # Update the screen

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        clock.tick(60)  # Run the game at 60 FPS

if __name__ == "__main__":
    main()