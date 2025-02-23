import math

path_width = 25

def catmull_rom_spline(points, points_per_segment):
    """
    Given a list of points, generate a Catmull-Rom spline
    that interpolates between them. Returns a list of (x,y) points.
    """
    spline_points = []
    n = len(points)
    # Iterate from the second point to the second-to-last point.
    # This ensures that for each segment we have P0, P1, P2, and P3.
    for i in range(1, n - 2):
        P0 = points[i - 1]
        P1 = points[i]
        P2 = points[i + 1]
        P3 = points[i + 2]
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
            spline_points.append((int(x), int(y)))
    return spline_points

def calculate_distance(p1, p2):
    """Calculate the Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def calculate_angle(points):
    """
    Given a list of (x, y) points along a path, return a list of angles (in degrees)
    that are perpendicular to the path at each point.
    
    For the first point, the tangent is computed from the first segment.
    For the last point, the tangent is computed from the last segment.
    For interior points, the tangent is computed as the average of the angles of the
    segments before and after the point.
    """
    angles = []
    n = len(points)
    
    for i in range(n):
        if i == 0:
            # Use the direction of the first segment.
            dx = points[1][0] - points[0][0]
            dy = points[1][1] - points[0][1]
            tangent_angle = math.atan2(dy, dx)
        elif i == n - 1:
            # Use the direction of the last segment.
            dx = points[i][0] - points[i-1][0]
            dy = points[i][1] - points[i-1][1]
            tangent_angle = math.atan2(dy, dx)
        else:
            # For interior points, average the normalized vectors from the previous and next segments.
            dx1 = points[i][0] - points[i-1][0]
            dy1 = points[i][1] - points[i-1][1]
            dx2 = points[i+1][0] - points[i][0]
            dy2 = points[i+1][1] - points[i][1]
            # Normalize both vectors.
            mag1 = math.hypot(dx1, dy1)
            mag2 = math.hypot(dx2, dy2)
            if mag1 == 0 or mag2 == 0:
                tangent_angle = math.atan2(dy2, dx2)  # fallback
            else:
                nx = (dx1 / mag1) + (dx2 / mag2)
                ny = (dy1 / mag1) + (dy2 / mag2)
                tangent_angle = math.atan2(ny, nx)
        
        # To rotate perpendicular to the path, add 90 degrees (pi/2 radians).
        perpendicular_angle = tangent_angle + math.pi / 2
        # Convert to degrees.
        angle_degrees = math.degrees(perpendicular_angle)
        angles.append(angle_degrees)
        print(angles)
    
    return angles
def resample_path(points, step_size):
    """Resample the path so that the distance between consecutive points is uniform."""
    resampled_points = [points[0]]
    current_distance = 0.0
    i = 1
    while i < len(points):
        last_point = resampled_points[-1]
        next_point = points[i]
        segment_distance = calculate_distance(last_point, next_point)
        if current_distance + segment_distance >= step_size:
            # Calculate the position of the new point
            ratio = (step_size - current_distance) / segment_distance
            new_x = last_point[0] + ratio * (next_point[0] - last_point[0])
            new_y = last_point[1] + ratio * (next_point[1] - last_point[1])
            resampled_points.append((int(new_x), int(new_y)))
            current_distance = 0.0
        else:
            current_distance += segment_distance
            i += 1
    return resampled_points

def generate_path_points(width, height, step_size=5, default_radius=50, points_per_segment=50):
    """
    Generate a smooth path for the game using a Catmull-Rom spline.
    The path is built from a set of anchors that define key positions.
    The endpoints are duplicated to ensure the spline passes through
    the anchors (and subsequently through the midpoints).
    """
    start = (0 - default_radius, int(height * 0.125))
    generate_path_points.start = start
    end = (width, int(height * 0.875))
    dy = end[1] - start[1]
    anchors = [
        start,
        (int(width * 0.7), start[1]),
        (int(width * 0.7), start[1] + int(dy * 0.5)),
        (int(width * 0.3), start[1] + int(dy * 0.5)),
        (int(width * 0.3), end[1]),
        end
    ]
    # Duplicate the first and last anchors to handle the endpoints.
    extended = [anchors[0]] + anchors + [anchors[-1]]
    path_points = catmull_rom_spline(extended, points_per_segment)
    # Resample the path to ensure uniform spacing between points.
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
        
        # Normalize the tangent.
        length = math.hypot(dx, dy)
        if length == 0:
            norm_dx, norm_dy = 0, 0
        else:
            norm_dx = dx / length
            norm_dy = dy / length
        
        # Get the perpendicular (normal) vector.
        nx = -norm_dy
        ny = norm_dx
        
        # Offset the center point to get the left and right boundaries.
        left_points.append((x + nx * half_width, y + ny * half_width))
        right_points.append((x - nx * half_width, y - ny * half_width))
    
    # Combine the left side and the reversed right side to make a closed polygon.
    right_points.reverse()
    return left_points + right_points