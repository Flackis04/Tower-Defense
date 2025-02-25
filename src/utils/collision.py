def circle_rect_collision(circle_center, circle_radius, rect):
    """Return True if a circle and rectangle intersect."""
    cx, cy = circle_center
    nearest_x = max(rect.left, min(cx, rect.right))
    nearest_y = max(rect.top, min(cy, rect.bottom))
    dx = cx - nearest_x
    dy = cy - nearest_y
    return dx * dx + dy * dy <= circle_radius * circle_radius