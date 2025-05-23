import math
import ctypes
import pygame
import numpy as np
from scipy.special import comb
import other.helper as helper

pygame.init()
                    
pathwidth = helper.get_screen_size(True, False) / 45
default_margin = pathwidth / 2.0
screen_width, screen_height = helper.get_screen_size(False, False)

                                                                        

def coordinate_factor(pixel_coord, center_coord, half_width, margin):
    if center_coord - half_width <= pixel_coord <= center_coord + half_width:
        return 1.0
    else:
        if pixel_coord < center_coord - half_width:
            dist = (center_coord - half_width) - pixel_coord
        else:
            dist = pixel_coord - (center_coord + half_width)
        factor = max(0.0, 1 - (dist / margin))
        return factor

def Q(x, y, pathpoints, pathwidth, margin=default_margin):
    half_width = pathwidth / 2.0
    closest_point_x = min(pathpoints, key=lambda p: abs(x - p[0]))
    factor_x = coordinate_factor(y, closest_point_x[1], half_width, margin)
    closest_point_y = min(pathpoints, key=lambda p: abs(y - p[1]))
    factor_y = coordinate_factor(x, closest_point_y[0], half_width, margin)
    return factor_x * factor_y

def get_path_polygon(points, width):
    half_width = width / 2.0
    left_points = []
    right_points = []
    
    for i in range(len(points)):
        x, y = points[i]
                                        
        if i == 0:
            dx = points[1][0] - x
            dy = points[1][1] - y
        elif i == len(points) - 1:
            dx = x - points[i - 1][0]
            dy = y - points[i - 1][1]
        else:
            dx = points[i + 1][0] - points[i - 1][0]
            dy = points[i + 1][1] - points[i - 1][1]
        
        length = math.hypot(dx, dy)
        if length == 0:
            norm_dx, norm_dy = 0, 0
        else:
            norm_dx = dx / length
            norm_dy = dy / length
        
                                        
        nx = -norm_dy
        ny = norm_dx
        
        left_points.append((x + nx * half_width, y + ny * half_width))
        right_points.append((x - nx * half_width, y - ny * half_width))
    
    right_points.reverse()
    return left_points + right_points

def draw_path(screen, path_points):
    path_polygon = get_path_polygon(path_points, pathwidth)
    pygame.draw.polygon(screen, (45, 45, 45), path_polygon)

                                                           

def bezier_curve(points, num_points=100):
    """
    Calculate points on a Bézier curve given control points.
    Uses the Bernstein polynomial formulation.
    """
    n = len(points) - 1
    t_values = np.linspace(0, 1, num_points)
    curve = np.zeros((num_points, 2))
    for i in range(n + 1):
        binomial_coeff = comb(n, i)
        curve += binomial_coeff * ((1 - t_values) ** (n - i))[:, None] * (t_values ** i)[:, None] * points[i]
    return curve

def get_path_points():
    """
    Return predetermined path points generated from a Bézier curve.
    The control points are chosen so that the path starts at (0,200) and ends at (1920,880).
    """
    control_points = np.array([
        [0, screen_height//8],
        [screen_width//4, screen_height//8],
        [screen_width//2, screen_height//3],
        [screen_width//1.6, screen_height//1.2],
        [screen_width, screen_height/1.2]
    ], dtype=float)
    curve = bezier_curve(control_points, num_points=200)
    path_points = [tuple(point) for point in curve]
    return path_points

                                                          

def compute_arc_lengths(points):
    """
    Given a list of points, compute cumulative arc lengths along the path.
    This is used to allow constant-speed traversal along a curved path.
    """
    arc_lengths = [0.0]
    for i in range(1, len(points)):
        dx = points[i][0] - points[i - 1][0]
        dy = points[i][1] - points[i - 1][1]
        segment_length = math.hypot(dx, dy)
        arc_lengths.append(arc_lengths[-1] + segment_length)
    return arc_lengths

def get_position_at_distance(path_points, arc_lengths, d):
    """
    Given the list of path points and their cumulative arc lengths,
    return the interpolated (x, y) position corresponding to the distance 'd' along the path.
    """
    if d <= 0:
        return path_points[0]
    elif d >= arc_lengths[-1]:
        return path_points[-1]
    
                                    
    for i in range(len(arc_lengths) - 1):
        if arc_lengths[i] <= d < arc_lengths[i+1]:
                                                                               
            segment_length = arc_lengths[i+1] - arc_lengths[i]
            f = (d - arc_lengths[i]) / segment_length
            x = path_points[i][0] + f * (path_points[i+1][0] - path_points[i][0])
            y = path_points[i][1] + f * (path_points[i+1][1] - path_points[i][1])
            return (x, y)
    return path_points[-1]