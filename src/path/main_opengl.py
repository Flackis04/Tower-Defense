import pygame
import numpy as np
from scipy.ndimage import distance_transform_edt  # Efficient distance transform
import pathgen

# Assume screen dimensions, pathpoints, and pathwidth are defined
screen_width, screen_height = 800, 600
pathwidth = 20
D_max = 100  # Maximum distance to influence brightness

pathpoints = pathgen.generate_path_points(screen_width, screen_height, step_size=1, default_radius=50, points_per_segment=250)
pathpoints_np = np.array(pathpoints)

perlin_rgb = (70,70,70)


# 1. Create a surface for the path mask
path_surface = pygame.Surface((screen_width, screen_height))
path_surface.fill((0, 0, 0))  # Black background

# Draw the path on the surface as a thick line
if len(pathpoints) > 1:
    pygame.draw.lines(path_surface, (255, 255, 255), False, pathpoints, pathwidth)

# 2. Convert the path mask to a numpy array
mask = pygame.surfarray.array_alpha(path_surface)  # or array3d if using grayscale info
# Invert the mask: pixels on the path should be zero distance, background nonzero
binary_mask = (mask < 128).astype(np.uint8)  # 0 on path, 1 elsewhere

# 3. Compute the distance transform
distance_field = distance_transform_edt(binary_mask)

# 4. Map the distance to a brightness factor (using linear mapping here)
brightness_factor = 1 - np.clip(distance_field / D_max, 0, 1)

# 5. Generate your Perlin noise terrain as an RGB numpy array (perlin_rgb)
# ... [your perlin noise generation code] ...

# 6. Multiply perlin noise by brightness factor (applied per pixel)
# Make sure brightness_factor has the same shape as perlin_rgb (or reshape accordingly)
modified_rgb = perlin_rgb * brightness_factor[..., None]  # assuming perlin_rgb shape is (H, W, 3)

# Finally, convert modified_rgb back to a pygame surface and display it.

# Initialize Pygame and create a screen
pygame.init()
screen_width, screen_height = 800, 600  # adjust as needed
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Assume modified_rgb is a numpy array of shape (height, width, 3) with values in [0, 255]
# For example, if you have computed it as described earlier:
# modified_rgb = perlin_rgb * brightness_factor[..., None]
# Make sure it's of type uint8:
modified_rgb = modified_rgb.astype(np.uint8)

# Pygame expects surfaces to have dimensions (width, height) so if your array shape is (height, width, 3),
# you need to transpose it:
surface = pygame.surfarray.make_surface(modified_rgb.transpose(1, 0, 2))

# Main display loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Blit the surface and update the display
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    clock.tick(60)  # limits the loop to 60 frames per second

pygame.quit()
