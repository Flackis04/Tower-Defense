import pygame

def get_screen_size(get_width, get_height):
    info = pygame.display.Info()
    if get_width:
        return info.current_w
    if get_height:
        return info.current_h
    else:
        return info.current_w, info.current_h