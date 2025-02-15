import pygame
import defenses
import constants
import economy
import effects
import config  # configuration file for drag-and-drop settings
import math
import path  # used to generate the path points
from effects import get_flash_instance, get_invalid_placement_flash_instance

class MarketButton:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text="Buy",
        color=(50, 205, 50),
        hover_color=(70, 225, 70),
        text_color=(255, 255, 255),
        border_radius=0,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.text = text
        self.current_color = color
        self.font = pygame.font.SysFont(None, 24)
        self.border_radius = border_radius

    def draw(self, surface):
        pygame.draw.rect(
            surface, self.current_color, self.rect, border_radius=self.border_radius
        )
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, events, cached_mouse_pos):
        self.current_color = (
            self.hover_color if self.rect.collidepoint(cached_mouse_pos) else self.color
        )
        for event in events:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos)
            ):
                return True
        return False


def make_market_btn(screen, button_width=100, button_height=40, margin=10):
    screen_width, _ = screen.get_size()
    x = screen_width - button_width - margin
    return MarketButton(x, margin, button_width, button_height)


class Market:
    def __init__(
        self,
        screen,
        x=None,
        y=0,
        width=175,
        height=450,
        text="Items...",
        color=constants.color_theme,
        text_color=(255, 255, 255),
        defense=None,
    ):
        if x is None:
            screen_width, _ = screen.get_size()
            x = screen_width - width  # align flush with the right edge
        self.rect = pygame.Rect(x, y, width, height)
        self.screen = screen
        self.color = color
        self.text_color = text_color
        self.text = text
        self.current_color = color
        self.font = pygame.font.SysFont(None, 24)
        self.defense = defense

        # Colors for non-focused and focused buttons.
        self.non_focus_color = constants.color_theme
        self.focus_color = (255, 0, 0)

        self.focused_btn = None
        self.category_btns = []
        button_height = 40
        base_button_width = self.rect.width // 3
        for i in range(3):
            current_button_width = (
                base_button_width
                if i < 2
                else self.rect.width - base_button_width * 2
            )
            x_button = self.rect.x + base_button_width * i
            btn = MarketButton(
                x_button,
                self.rect.y,
                current_button_width,
                button_height,
                text=f"{i+1}",
                color=self.non_focus_color,
            )
            self.category_btns.append(btn)
        if self.category_btns:
            self.focused_btn = self.category_btns[0]
            self.focused_btn.current_color = self.focus_color
            self.category_index_ = 0

        # For drag-and-drop functionality:
        self.drag_drop_enabled = config.DRAG_DROP_ENABLED  # use configuration value
        self.dragging_item = None
        self.drag_offset = (0, 0)

        self.placed_defenses = []
        self.market_is_pinned = False
        # New attribute to debounce the small pin button
        self.pin_btn_pressed = False

        # Set up an inventory for the market's containers.
        # Assuming we have 5 rows x 2 columns (10 containers); you can adjust the logic here.
        self.num_cols = 2
        self.num_rows = 5
        self.gap = 5
        self.container_size = 70
        
        self.inventory = [False] * 10  
        self.all_container_indices = [(r, c) for r in range(self.num_rows) for c in range(self.num_cols)]
        self.chunk_size = len(self.all_container_indices) // (len(self.category_btns)-1)  # Determine how many elements per sublist
        self.container_index = [self.all_container_indices[i * self.chunk_size: (i + 1) * self.chunk_size] for i in range(3)]        

        # Load the small icon image for items.
        # Make sure that the image file exists in the specified path.
        self.item_icon = pygame.image.load("img/up-arrow.png").convert_alpha()
        # Scale the icon to a desired size (e.g. 20x20 pixels).
        self.item_icon = pygame.transform.scale(self.item_icon, (20, 20))
        
        # Pre-calculate the path points using the current screen dimensions.
        screen_width, screen_height = screen.get_size()
        self.path_points = path.generate_path_points(screen_width, screen_height)

        # Add a very small button in the bottom-left corner of the market.
        small_button_width = 10
        small_button_height = 10
        small_button_x = self.rect.x + 5  # align with the market's left edge
        small_button_y = self.rect.y - 5 + self.rect.height - small_button_height  # bottom aligned with the market
        self.pin_btn = MarketButton(
            small_button_x,
            small_button_y,
            small_button_width,
            small_button_height,
            text="",
            color=(150, 150, 150),
            hover_color=(180, 180, 180)
        )

    def get_container_rect(self, container_index):
        """
        Returns the pygame.Rect for the container specified by its index (0-9).
        """  # fixed container size

        grid_width = self.num_cols * self.container_size + (self.num_cols + 1) * self.gap
        grid_height = self.num_rows * self.container_size + (self.num_rows + 1) * self.gap
        vertical_offset = 20  # Move the grid 20 pixels lower
        start_x = self.rect.x + (self.rect.width - grid_width) // 2
        start_y = self.rect.y + (self.rect.height - grid_height) // 2 + vertical_offset

        row = self.container_index[container_index] // self.num_cols
        col = self.container_index[container_index] % self.num_cols
        container_x = start_x + self.gap + col * (self.container_size + self.gap)
        container_y = start_y + self.gap + row * (self.container_size + self.gap)
        return pygame.Rect(container_x, container_y, self.container_size, self.container_size)

    def get_container_center(self, container_index):
        """
        Returns the (x, y) coordinates for the center of the container specified by its index.
        """
        rect = self.get_container_rect(container_index)
        return rect.center

    def distance_to_segment(self, point, start, end):
        # Compute the distance from a point to a line segment (start to end)
        x, y = point
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(x - x1, y - y1)
        t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(x - proj_x, y - proj_y)

    def is_near_path(self, point, tolerance=10):
        # Check if the point is within a given tolerance of any segment in the path
        for i in range(len(self.path_points) - 1):
            seg_start = self.path_points[i]
            seg_end = self.path_points[i + 1]
            if self.distance_to_segment(point, seg_start, seg_end) <= tolerance:
                return True
        return False

    def get_path_orientation(self, point, tolerance=10):
        # Existing logic: find orientation of the single nearest segment.
        for i in range(len(self.path_points) - 1):
            seg_start = self.path_points[i]
            seg_end = self.path_points[i + 1]
            if self.distance_to_segment(point, seg_start, seg_end) <= tolerance:
                dx = seg_end[0] - seg_start[0]
                dy = seg_end[1] - seg_start[1]
                if abs(dx) >= abs(dy):
                    return "horizontal"
                else:
                    return "vertical"
        return "horizontal"

    def get_continuous_path_orientation(self, point, tolerance=10, window=5):
        """
        Find the index of the nearest segment to point, then examine a window of segments
        around that point to determine if the orientation is continuous.
        Returns a tuple (orientation, continuous) where orientation is either "horizontal" or "vertical"
        and continuous is a boolean that is True when at least 70% of the segments in the window
        share the same orientation.
        """
        min_dist = float('inf')
        min_idx = 0
        for i in range(len(self.path_points) - 1):
            d = self.distance_to_segment(point, self.path_points[i], self.path_points[i + 1])
            if d < min_dist:
                min_dist = d
                min_idx = i

        h_count = 0
        v_count = 0
        total = 0
        start_idx = max(0, min_idx - window)
        end_idx = min(len(self.path_points) - 1, min_idx + window)
        for i in range(start_idx, end_idx):
            p1 = self.path_points[i]
            p2 = self.path_points[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            if abs(dx) >= abs(dy):
                h_count += 1
            else:
                v_count += 1
            total += 1

        if total == 0:
            return (self.get_path_orientation(point, tolerance), False)
        if h_count / total >= 0.7:
            return ("horizontal", True)
        elif v_count / total >= 0.7:
            return ("vertical", True)
        else:
            return (self.get_path_orientation(point, tolerance), False)

    def snap_point_to_path(self, point, snap_tolerance=15):
        """
        Instead of projecting the drop point onto the segment,
        snap to the midpoint of the nearest segment if the midpoint is within snap_tolerance.
        """
        best_midpoint = None
        min_dist = float('inf')
        # Loop over every segment in the path.
        for i in range(len(self.path_points) - 1):
            A = self.path_points[i]
            B = self.path_points[i + 1]
            # Calculate the midpoint of the segment.
            midpoint = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
            d = math.hypot(point[0] - midpoint[0], point[1] - midpoint[1])
            if d < min_dist:
                min_dist = d
                best_midpoint = (int(midpoint[0]), int(midpoint[1]))
        if min_dist <= snap_tolerance:
            return best_midpoint
        else:
            return None

    def is_placeable(self, point, defense, base_tolerance=10):
        """
        Determines if the given point is close enough to some path segment,
        using an increased tolerance in areas where the path orientation is continuous.
        Also ensures the point is on-screen.
        """
        if not self.screen.get_rect().collidepoint(point):
            return False
        orientation, continuous = self.get_continuous_path_orientation(point)
        tolerance = base_tolerance + (defense.snapbox * 0.5 if continuous else 0)
        for i in range(len(self.path_points) - 1):
            seg_start = self.path_points[i]
            seg_end = self.path_points[i + 1]
            if self.distance_to_segment(point, seg_start, seg_end) <= tolerance:
                return True
        return False

    def update(self, events):
        # Check for clicks in containers for drag-and-drop functionality.
        for event in events:
            if self.drag_drop_enabled:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Iterate through all 10 containers.
                    for container_index in range(10):
                        container_rect = self.get_container_rect(container_index)
                        if container_rect.collidepoint(event.pos) and economy.balance >= defenses.Blöja(self.screen, self, (255, 0, 255)).cost:
                            print(f"Clicked container: {container_index}")
                            # In this example, container 0 holds the Blöja defense.
                            if container_index == 0:
                                self.dragging_item = defenses.Blöja(self.screen, self, (255, 0, 255))
                                # Set drag_offset so the object's center aligns with the cursor.
                                self.drag_offset = (0, 0)
                                print("Dragging Blöja initiated.")
                            else:
                                print("Clicked container does not hold a draggable item.")
                            break
                        else:
                            container_rect = self.get_container_rect(0)
                            if container_rect.collidepoint(event.pos) and self.focused_btn == self.category_btns[2] and self.category_index == 2 and container_index == 0:
                                flash = get_flash_instance()
                                flash.trigger()
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.dragging_item:
                        drop_point = event.pos
                        # Determine nearby path orientation and set angle accordingly.
                        orientation, continuous = self.get_continuous_path_orientation(drop_point)
                        self.dragging_item.angle = 90 if orientation == "vertical" else 0
                        # Use improved placement logic.
                        if self.is_placeable(drop_point, self.dragging_item):
                            snapped_point = self.snap_point_to_path(drop_point)
                            # If snapping succeeds, use that; otherwise fallback to the drop point.
                            final_point = snapped_point if snapped_point is not None else drop_point
                            self.dragging_item.pos = final_point
                            self.placed_defenses.append(self.dragging_item)
                            # Subtract defense cost from the balance once it is placed.
                            economy.balance -= self.dragging_item.cost
                            print("Placed defense at:", self.dragging_item.pos)
                        else:
                            print("Release position is not valid. Defense not placed.")
                    flash = get_invalid_placement_flash_instance()
                    flash.stop()
                    self.dragging_item = None

        # Existing category button update.
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    for btn in self.category_btns:
                        if btn.rect.collidepoint(event.pos):
                            if self.focused_btn and self.focused_btn != btn:
                                self.focused_btn.current_color = self.non_focus_color
                            self.focused_btn = btn
                            self.focused_btn.current_color = self.focus_color
                            self.category_index = self.category_btns.index(btn)
                            
                            break
                else:
                    if not self.market_is_pinned:
                        return True
                    
        return False

    def draw(self, screen, cached_mouse_pos):
        # Draw market background
        pygame.draw.rect(screen, self.current_color, self.rect)

        # Center the grid of 10 containers (5 rows x 2 columns) within the market.
        num_cols = 2
        num_rows = 5
        gap = 5
        container_size = 70  # fixed container size

        grid_width = num_cols * container_size + (num_cols + 1) * gap
        grid_height = num_rows * container_size + (num_rows + 1) * gap
        vertical_offset = 20  # consistent vertical offset
        start_x = self.rect.x + (self.rect.width - grid_width) // 2
        start_y = self.rect.y + (self.rect.height - grid_height) // 2 + vertical_offset

        for row in range(num_rows):
            for col in range(num_cols):
                x = start_x + gap + col * (container_size + gap)
                y = start_y + gap + row * (container_size + gap)
                container_rect = pygame.Rect(x, y, container_size, container_size)
                pygame.draw.rect(screen, (15, 15, 15), container_rect, border_radius=3)

        for btn in self.category_btns:
            btn.draw(screen)
        if self.focused_btn == self.category_btns[2]:
            blöja = defenses.Blöja(self.screen, self, (255, 0, 255))
            center = self.get_container_center(0)
            orientation, continuous = self.get_continuous_path_orientation(center)
            if orientation == "vertical":
                blöja.angle = 90
                width, height = 50, 20
            else:
                blöja.angle = 0
                width, height = 20, 50
            rect = pygame.Rect(center[0] - width // 2, center[1] - height // 2, width, height)
            if economy.balance >= blöja.cost:
                pygame.draw.rect(screen, blöja.color, rect)
            else:
                blöja = defenses.Blöja(self.screen, self, (55, 0, 55))
                pygame.draw.rect(screen, blöja.color, rect)

        # If an item is being dragged (from a container), attach it to the cursor.
        if self.dragging_item:
            mouse_x, mouse_y = cached_mouse_pos
            orientation, _ = self.get_continuous_path_orientation((mouse_x, mouse_y))
            self.dragging_item.angle = 90 if orientation == "vertical" else 0
            if self.dragging_item.angle == 90:
                width, height = 50, 20
            else:
                width, height = 20, 50
            drag_rect = pygame.Rect(mouse_x - width // 2, mouse_y - height // 2, width, height)
            pygame.draw.rect(screen, self.dragging_item.color, drag_rect)

            # Draw a semi-transparent red circle if placement is not allowed.
            if not self.is_placeable((mouse_x, mouse_y), self.dragging_item) and not self.rect.collidepoint(cached_mouse_pos):
                flash = get_invalid_placement_flash_instance()
                flash.trigger()
            else:
                flash = get_invalid_placement_flash_instance()
                flash.stop()
        # Update and draw the invalid placement flash
        flash = get_invalid_placement_flash_instance()
        flash.update()
        flash.draw()
        # Draw the very small button (pin button) in the bottom-left corner of the market.
        self.pin_btn.draw(screen)
        if self.pin_btn.rect.collidepoint(cached_mouse_pos):
            pygame.draw.rect(screen, (255, 255, 255), self.pin_btn.rect, 2)
            # Use rising edge detection to avoid multiple toggles per press.
            if pygame.mouse.get_pressed()[0]:
                if not self.pin_btn_pressed:
                    self.market_is_pinned = not self.market_is_pinned
                    self.pin_btn_pressed = True
            else:
                self.pin_btn_pressed = False
            self.pin_btn.current_color = (255, 255, 255) if self.market_is_pinned else (150, 150, 150)

    def draw_defenses(self, screen):
        """
        Draws all placed defenses so they remain visible regardless
        of whether the market menu is open.
        """
        for defense in self.placed_defenses:
            defense.draw()


def make_market(screen, width=175, height=450):
    return Market(screen, width=width, height=height)

class UpgradeButton:
    def __init__(self, x, y, width, height, container_index):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (50, 205, 50)
        self.hover_color = (70, 225, 70)

    def draw(self, screen):    # Calculate the container index (assuming row-major order).
        container_index = Market.row * Market.num_cols + Market.col
        if self.inventory[container_index]:
            # Define the upgrade button dimensions and position.
            upgrade_button_width = 20
            upgrade_button_height = 20
            upgrade_button_color = (50, 205, 50)
            button_padding = 2
            button_x = Market.rect.x + Market.container_size - upgrade_button_width - button_padding
            button_y = Market.rect.y + Market.container_size - upgrade_button_height - button_padding
            upgrade_button_rect = pygame.Rect(button_x, button_y, upgrade_button_width, upgrade_button_height)
            
            # Draw a green rounded rectangle as the upgrade button.
            pygame.draw.rect(screen, (upgrade_button_color), upgrade_button_rect, border_radius=5)
            if Market.cached_mouse_pos.collidepoint(upgrade_button_rect):
                current_upgrade_button_color[container_index] = (70, 225, 70)
                if pygame.mouse.get_pressed()[0]:
                    self.current_upgrades[container_index] += 1
                    print(f"Upgraded container {container_index} to level {self.current_upgrades[container_index]}")
            # Draw a white upward arrow on the upgrade button.
            arrow_points = [
                (button_x + upgrade_button_width // 2, button_y + 4),
                (button_x + 4, button_y + upgrade_button_height - 4),
                (button_x + upgrade_button_width - 4, button_y + upgrade_button_height - 4)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), arrow_points)

