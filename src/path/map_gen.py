import pygame
import random
import numpy as np
from scipy.ndimage import gaussian_filter

def generate_smooth_noise_background(width, height, scale=100):
    pygame.init()
    screen = pygame.Surface((width, height))
    pixels = pygame.PixelArray(screen)
    
    def perlin_noise(shape, scale, octaves=6, persistence=0.6, contrast=1.2, smoothness=2):
        def fade(t):
            return t * t * t * (t * (t * 6 - 15) + 10)
        
        noise = np.zeros(shape)
        frequency = 1.0 / scale
        amplitude = 1.0
        
        for _ in range(octaves):
            grid_size_x = int(shape[1] * frequency) + 1
            grid_size_y = int(shape[0] * frequency) + 1
            
            gradient = np.random.randn(grid_size_y, grid_size_x, 2)
            gradient /= np.linalg.norm(gradient, axis=2, keepdims=True)
            
            grid_x, grid_y = np.meshgrid(
                np.linspace(0, grid_size_x - 1, shape[1], endpoint=False),
                np.linspace(0, grid_size_y - 1, shape[0], endpoint=False)
            )
            
            wx = fade(grid_x % 1)
            wy = fade(grid_y % 1)
            
            def dot_grid_gradient(ix, iy, x, y):
                dx, dy = x - ix, y - iy
                return dx * gradient[iy, ix, 0] + dy * gradient[iy, ix, 1]
            
            n00 = dot_grid_gradient(np.floor(grid_x).astype(int), np.floor(grid_y).astype(int), grid_x, grid_y)
            n10 = dot_grid_gradient(np.ceil(grid_x).astype(int), np.floor(grid_y).astype(int), grid_x, grid_y)
            n01 = dot_grid_gradient(np.floor(grid_x).astype(int), np.ceil(grid_y).astype(int), grid_x, grid_y)
            n11 = dot_grid_gradient(np.ceil(grid_x).astype(int), np.ceil(grid_y).astype(int), grid_x, grid_y)
            
            nx0 = n00 + wx * (n10 - n00)
            nx1 = n01 + wx * (n11 - n01)
            octave_noise = nx0 + wy * (nx1 - nx0)
            
            noise += amplitude * octave_noise
            frequency *= 2
            amplitude *= persistence
        
        noise = (noise - noise.min()) / (noise.max() - noise.min())
        noise = np.power(noise, contrast)  # Increase contrast for better elevation distinction
        noise = gaussian_filter(noise, smoothness)  # Smooth transitions
        return noise
    
    noise = perlin_noise((height, width), scale, octaves=6, persistence=0.6, contrast=1.2, smoothness=3)
    
    # Define 5 evenly spaced color levels from min to max
    color_min = np.array([70, 70, 70])   # #0A4500
    color_max = np.array([90, 90, 90])   # #1AAE00
    num_levels = 5
    color_levels = [color_min + (i / (num_levels - 1)) * (color_max - color_min) for i in range(num_levels)]
    target_levels = np.linspace(0, 1, num_levels)
    
    # sigma controls the width of the blending transition between levels
    sigma = 0.1
    
    # Map noise values to a smooth blend of the discrete color levels.
    for x in range(width):
        for y in range(height):
            f = noise[y, x]
            # Compute Gaussian weights for each target level
            weights = np.exp(-((f - target_levels) ** 2) / (2 * sigma ** 2))
            weights /= np.sum(weights)
            color = np.zeros(3)
            for i in range(num_levels):
                color += weights[i] * color_levels[i]
            color = color.astype(int)
            pixels[x, y] = (color[0], color[1], color[2])
    
    del pixels
    return screen

# Example usage
width, height = 800, 600
background = generate_smooth_noise_background(width, height, scale=150)
pygame.image.save(background, "smooth_noise_bg.png")
