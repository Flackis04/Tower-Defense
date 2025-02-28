import pygame
import numpy as np
from map_gen import generate_smooth_noise_background  # your perlin noise background generator
from pathgen import generate_path_points, draw_path, pathwidth  # pathgen functions and pathwidth

# Assuming `screen` is your Pygame display surface
# path_points is the list of points returned from `generate_path_points`
# width is the desired width for the path polygon (e.g., 10)
def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    # --- 1. Generate Background ---
    background = generate_smooth_noise_background(width, height, scale=150)

    # --- 2. Generate Path Points ---
    pathpoints = generate_path_points(width, height, step_size=1, default_radius=50, points_per_segment=250)
    # Convert list of (x,y) to a NumPy array of shape (N, 2)
    pathpoints_np = np.array(pathpoints)

    # --- 3. Vectorized Q Factor Computation ---
    # For our coordinate_factor we use half the pathwidth as our in-band tolerance.
    half_width = pathwidth / 2.0
    # Here we use the same value for margin as half_width (this was your default_margin)
    margin = half_width

    # Create 1D arrays for the x and y coordinates of the screen.
    x_arr = np.arange(width)   # shape: (width,)
    y_arr = np.arange(height)  # shape: (height,)

    # For each x, find the path point with the closest x coordinate and get its y.
    # diff_x has shape (num_pathpoints, width)
    diff_x = np.abs(x_arr[None, :] - pathpoints_np[:, 0][:, None])
    idx_min_x = np.argmin(diff_x, axis=0)         # shape: (width,)
    p_y_for_x = pathpoints_np[idx_min_x, 1]         # shape: (width,)

    # For each y, find the path point with the closest y coordinate and get its x.
    diff_y = np.abs(y_arr[None, :] - pathpoints_np[:, 1][:, None])
    idx_min_y = np.argmin(diff_y, axis=0)           # shape: (height,)
    p_x_for_y = pathpoints_np[idx_min_y, 0]           # shape: (height,)

    # Compute factor_x for every pixel.
    # For a given column x, the corresponding band is centered at p_y_for_x[x]
    # Create a 2D grid for y coordinates (rows) and for the center (per column).
    y_mat = y_arr[:, None]             # shape: (height, 1)
    center_for_x = p_y_for_x[None, :]    # shape: (1, width)
    factor_x = np.where(
        y_mat < (center_for_x - half_width),
        1 - ((center_for_x - half_width) - y_mat) / margin,
        np.where(
            y_mat > (center_for_x + half_width),
            1 - (y_mat - (center_for_x + half_width)) / margin,
            1
        )
    )
    factor_x = np.clip(factor_x, 0, 1)

    # Compute factor_y for every pixel.
    # For a given row y, the corresponding band is centered at p_x_for_y[y]
    x_mat = x_arr[None, :]             # shape: (1, width)
    center_for_y = p_x_for_y[:, None]    # shape: (height, 1)
    factor_y = np.where(
        x_mat < (center_for_y - half_width),
        1 - ((center_for_y - half_width) - x_mat) / margin,
        np.where(
            x_mat > (center_for_y + half_width),
            1 - (x_mat - (center_for_y + half_width)) / margin,
            1
        )
    )
    factor_y = np.clip(factor_y, 0, 1)

    # Total factor: pixels near the path in both dimensions get full (1) brightness.
    total_factor = factor_x * factor_y  # shape: (height, width)

    # --- 4. Apply the Q Factor to the Background ---
    # Use pygame.surfarray to access pixel data.
    # Note: pygame.surfarray.array3d returns an array with shape (width, height, 3),
    # so we transpose it to get (height, width, 3) to match our factor.
    bg_array = pygame.surfarray.array3d(background)
    bg_array = np.transpose(bg_array, (1, 0, 2)).astype(np.float32)  # shape: (height, width, 3)

    # Multiply each pixel's RGB by the Q factor.
    new_bg_array = (bg_array * total_factor[..., None]).clip(0, 255).astype(np.uint8)

    # Convert the modified array back to a Pygame surface.
    # Transpose back to (width, height, 3) as required by make_surface.
    new_surface = pygame.surfarray.make_surface(np.transpose(new_bg_array, (1, 0, 2)))

    # --- 5. Draw the Path on Top for Visualization ---
    draw_path(new_surface, pathpoints)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.blit(new_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()