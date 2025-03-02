import math
import ctypes
import pygame

# --- Parameters ---
width, height = 800, 600
pathwidth = 35  # the constant width of the path (as used in get_path_polygon)
# You can set the "margin" for the falloff (if a pixel is outside the band, how fast should the factor drop)
# Here we choose margin = half the pathwidth so that pixels more than pathwidth away from the band get factor 0.
default_margin = pathwidth / 2.0

def catmull_rom_spline(points, points_per_segment):
    """
    Given a list of points, generate a Catmull-Rom spline that interpolates between them.
    Returns a list of (x, y) points as floats.
    """
    spline_points = []
    n = len(points)
    # Loop over points ensuring we have P0, P1, P2, P3 for each segment.
    for i in range(1, n - 2):
        P0, P1, P2, P3 = points[i - 1], points[i], points[i + 1], points[i + 2]
        for j in range(points_per_segment):
            t = j / (points_per_segment - 1)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                2 * P1[0]
                + (-P0[0] + P2[0]) * t
                + (2 * P0[0] - 5 * P1[0] + 4 * P2[0] - P3[0]) * t2
                + (-P0[0] + 3 * P1[0] - 3 * P2[0] + P3[0]) * t3
            )
            y = 0.5 * (
                2 * P1[1]
                + (-P0[1] + P2[1]) * t
                + (2 * P0[1] - 5 * P1[1] + 4 * P2[1] - P3[1]) * t2
                + (-P0[1] + 3 * P1[1] - 3 * P2[1] + P3[1]) * t3
            )
            spline_points.append((x, y))
    return spline_points

def calculate_distance(p1, p2):
    """Calculate the Euclidean distance between two points."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def calculate_angle(points):
    """
    Given a list of (x, y) points along a path, return a list of angles (in degrees)
    that are perpendicular to the path at each point.
    
    For the first point, the tangent is computed from the first segment.
    For the last point, the tangent is computed from the last segment.
    For interior points, the tangent is computed as the average of the directions
    of the segments before and after the point.
    """
    angles = []
    n = len(points)
    
    for i in range(n):
        if i == 0:
            dx = points[1][0] - points[0][0]
            dy = points[1][1] - points[0][1]
            tangent_angle = math.atan2(dy, dx)
        elif i == n - 1:
            dx = points[i][0] - points[i - 1][0]
            dy = points[i][1] - points[i - 1][1]
            tangent_angle = math.atan2(dy, dx)
        else:
            dx1 = points[i][0] - points[i - 1][0]
            dy1 = points[i][1] - points[i - 1][1]
            dx2 = points[i + 1][0] - points[i][0]
            dy2 = points[i + 1][1] - points[i][1]
            mag1 = math.hypot(dx1, dy1)
            mag2 = math.hypot(dx2, dy2)
            if mag1 == 0 or mag2 == 0:
                tangent_angle = math.atan2(dy2, dx2)  # fallback
            else:
                # Average the normalized direction vectors.
                nx = (dx1 / mag1) + (dx2 / mag2)
                ny = (dy1 / mag1) + (dy2 / mag2)
                tangent_angle = math.atan2(ny, nx)
        
        # Rotate by 90° (pi/2 radians) to get the perpendicular angle.
        perpendicular_angle = tangent_angle + math.pi / 2
        angle_degrees = math.degrees(perpendicular_angle)
        angles.append(angle_degrees)
    
    return angles

# --- Helper function to compute a 0-1 factor for one coordinate ---
def coordinate_factor(pixel_coord, center_coord, half_width, margin):
    """
    Returns 1 if pixel_coord is within [center_coord - half_width, center_coord + half_width].
    Otherwise, returns a linearly decreasing value from 1 to 0 over a distance of 'margin'.
    """
    if center_coord - half_width <= pixel_coord <= center_coord + half_width:
        return 1.0
    else:
        # Determine the distance from the nearest band edge.
        if pixel_coord < center_coord - half_width:
            dist = (center_coord - half_width) - pixel_coord
        else:
            dist = pixel_coord - (center_coord + half_width)
        # Linear falloff: if dist equals margin or more, factor becomes 0.
        factor = max(0.0, 1 - (dist / margin))
        return factor

# --- The Q function as described ---
def Q(x, y, pathpoints, pathwidth, margin=default_margin):
    """
    For a given pixel coordinate (x, y), computes a brightness factor (between 0 and 1)
    based on how close it is to the path defined by pathpoints.
    
    It does this by:
      - Finding the path point whose x coordinate is closest to x,
        then comparing the pixel's y to that point's y (with tolerance pathwidth/2).
      - Finding the path point whose y coordinate is closest to y,
        then comparing the pixel's x to that point's x.
      - The final factor is the product of the two individual factors.
    """
    half_width = pathwidth / 2.0

    # Find the pathpoint closest in x
    closest_point_x = min(pathpoints, key=lambda p: abs(x - p[0]))
    factor_x = coordinate_factor(y, closest_point_x[1], half_width, margin)

    # Find the pathpoint closest in y
    closest_point_y = min(pathpoints, key=lambda p: abs(y - p[1]))
    factor_y = coordinate_factor(x, closest_point_y[0], half_width, margin)

    # Combine both factors (multiplying means that both dimensions must be “close” to give 1)
    return factor_x * factor_y


def resample_path(points, step_size):
    """
    Resample the path so that the distance between consecutive points is uniform.
    Returns a list of (x, y) points as floats.
    """
    if not points:
        return []
    
    resampled_points = [points[0]]
    current_distance = 0.0
    i = 1
    
    while i < len(points):
        last_point = resampled_points[-1]
        next_point = points[i]
        segment_distance = calculate_distance(last_point, next_point)
        
        if current_distance + segment_distance >= step_size:
            # Compute the new point at the required step distance.
            ratio = (step_size - current_distance) / segment_distance
            new_x = last_point[0] + ratio * (next_point[0] - last_point[0])
            new_y = last_point[1] + ratio * (next_point[1] - last_point[1])
            resampled_points.append((new_x, new_y))
            current_distance = 0.0
        else:
            current_distance += segment_distance
            i += 1
    
    return resampled_points

def compute_arc_lengths(path_points):
    """Precompute cumulative distances along the path."""
    arc_lengths = [0]
    for i in range(1, len(path_points)):
        prev = path_points[i - 1]
        curr = path_points[i]
        segment_length = math.sqrt((curr[0] - prev[0])**2 + (curr[1] - prev[1])**2)
        arc_lengths.append(arc_lengths[-1] + segment_length)
    return arc_lengths

def generate_path_points(width, height, step_size=1, default_radius=50, points_per_segment=250):
    """
    Generate a smooth path using a Catmull-Rom spline.
    The path is built from a set of anchor points.
    The endpoints are duplicated to ensure the spline passes through them.
    """
    # Use floats for more precise computation.
    start = (-default_radius, height * 0.125)
    end = (width, height * 0.875)
    dy = end[1] - start[1]
    
    anchors = [
        start,
        (width * 0.7, start[1]),
        (width * 0.7, start[1] + dy * 0.5),
        (width * 0.3, start[1] + dy * 0.5),
        (width * 0.3, end[1]),
        end
    ]
    # Duplicate the first and last anchors to handle endpoints.
    extended = [anchors[0]] + anchors + [anchors[-1]]
    path_points = catmull_rom_spline(extended, points_per_segment)
    # Resample the spline for uniform spacing.
    path_points = resample_path(path_points, step_size)
    return path_points

def cumulative_distances(points):
    """Compute the cumulative distances along the path for a list of points."""
    distances = [0.0]
    for i in range(1, len(points)):
        distances.append(distances[-1] + calculate_distance(points[i - 1], points[i]))
    return distances
    

def get_path_polygon(points, width):
    """
    Given a list of points forming the center of a path,
    return a list of polygon points that describe a path with a constant width.
    This is useful for generating a mesh or collision boundary.
    """
    half_width = width / 2.0
    left_points = []
    right_points = []
    
    for i in range(len(points)):
        x, y = points[i]
        # Determine the tangent direction.
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
        
        # Compute the perpendicular (normal) vector.
        nx = -norm_dy
        ny = norm_dx
        
        left_points.append((x + nx * half_width, y + ny * half_width))
        right_points.append((x - nx * half_width, y - ny * half_width))
    
    # Combine left and reversed right to form a closed polygon.
    right_points.reverse()
    return left_points + right_points

def draw_path(screen, path_points):
    """Draw the game path as a filled polygon."""
    path_polygon = get_path_polygon(path_points, 35)
    pygame.draw.polygon(screen, (45, 45, 45), path_polygon)