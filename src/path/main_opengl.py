import pygame
import numpy as np
from scipy.ndimage import distance_transform_edt                                
import path.pathx as pathx

                                                                 
screen_width, screen_height = 800, 600
pathwidth = 20
D_max = 100                                            

pathpoints = pathx.generate_path_points(screen_width, screen_height, step_size=1, default_radius=50, points_per_segment=250)
pathpoints_np = np.array(pathpoints)

perlin_rgb = (70,70,70)


                                       
path_surface = pygame.Surface((screen_width, screen_height))
path_surface.fill((0, 0, 0))                    

                                              
if len(pathpoints) > 1:
    pygame.draw.lines(path_surface, (255, 255, 255), False, pathpoints, pathwidth)

                                           
mask = pygame.surfarray.array_alpha(path_surface)                                      
                                                                                 
binary_mask = (mask < 128).astype(np.uint8)                          

                                   
distance_field = distance_transform_edt(binary_mask)

                                                                        
brightness_factor = 1 - np.clip(distance_field / D_max, 0, 1)

                                                                          
                                             

                                                                   
                                                                                       
modified_rgb = perlin_rgb * brightness_factor[..., None]                                          

                                                                        

                                       
pygame.init()
screen_width, screen_height = 800, 600                    
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

                                                                                          
                                                            
                                                          
                               
modified_rgb = modified_rgb.astype(np.uint8)

                                                                                                          
                           
surface = pygame.surfarray.make_surface(modified_rgb.transpose(1, 0, 2))

                   
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

                                             
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    clock.tick(60)                                           

pygame.quit()
