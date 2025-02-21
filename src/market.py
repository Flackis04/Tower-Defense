import pygame
import constants
import economy
import config  # configuration file for drag-and-drop settings
import math
import time
import path  # used to generate the path points
import defenses.barrier as barrier
import defenses.defense as defense
import defenses.mortar as mortar
import defenses.cannon as cannon
from defenses.defense import Defense
from effects import get_flash_instance, get_invalid_placement_flash_instance
import formulas

class Marketbtn:
    def __init__(
        self,
        market_instance,
        x,
        y,
        width,
        height,
        border_radius,
        text="Buy",
        color=(50, 205, 50),
        hover_color=(100, 255, 100),
        text_color=(255, 255, 255),
        transition_time=0.25,
    ):
        self.market = market_instance
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_color = text_color
        self.text = text
        self.font = pygame.font.SysFont(None, 24)
        self.border_radius = border_radius
        self.transition_time = transition_time  # Time in seconds
        self.transition_start = None  # Track transition start time
        self.hovering = False

    def draw(self, surface):
        pygame.draw.rect( 
            surface, self.current_color, self.rect, border_radius=self.border_radius
        )
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, events, cached_mouse_pos):
        is_hovering = self.rect.collidepoint(cached_mouse_pos)

        # Start transition if hover state changes
        if is_hovering != self.hovering:
            self.hovering = is_hovering
            self.transition_start = time.time()  # Record the start time

        # Handle smooth transition
        if self.transition_start is not None:
            elapsed = time.time() - self.transition_start
            t = min(elapsed / self.transition_time, 1)  # Normalize to [0, 1]
            self.current_color = self.lerp(self.color, self.hover_color, t) if self.hovering else self.lerp(self.hover_color, self.color, t)

            # Stop transition if completed
            if t >= 1:
                self.transition_start = None

        for event in events:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos)
            ):
                self.market.is_active = True
                return True
        return False
    
    def lerp(self, color1, color2, t):
        """Linear interpolation between two RGB colors."""
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )


def make_market_btn(screen, market_instance, border_radius=7, btn_width=100, btn_height=40, margin=10):
    screen_width, _ = screen.get_size()
    x = screen_width - btn_width - margin
    return Marketbtn(market_instance, x, margin, btn_width, btn_height, border_radius)


# --- New Container class for inventory management ---
class Container:
    def __init__(self, container_id, row, col, tab):
        self.id = container_id   # A unique ID for the container
        self.row = row           # The grid row (0-indexed)
        self.col = col           # The grid column (0-indexed)
        self.tab = tab # Which tab this container belongs to
        self.defense = None      # Holds a defense instance when assigned

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
        defensetypes = ["default", "special", "other"],
        defenselist = [],
    ):
        if x is None:
            screen_width, _ = screen.get_size()
            x = screen_width - width  # align flush with the right edge
        # Initialize basic attributes
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.market_has_been_opened = False
        self.tab_index = 0
        self.new_flash = get_flash_instance()
        self.invalid_placement_flash = get_invalid_placement_flash_instance()


        # Containers for the grid layout
        self.num_cols = 2
        self.num_rows = 5
        self.gap = 5
        self.container_size = 70

        # Colors
        self.color = color
        self.current_color = color
        self.text_color = text_color
        self.non_focus_color = constants.color_theme
        self.focus_color = (50, 50, 205)

        # Text and font
        self.text = text
        self.font = pygame.font.SysFont(None, 24)

        # Market and button states
        self.is_active = False  # Replaces market_is_active
        self.btn_is_active = True  # Replaces market_btn_is_active
        self.market_is_pinned = False  # Whether market stays open
        self.pin_btn_pressed = False  # To debounce the pin button

        # Drag-and-drop functionality
        self.drag_drop_enabled = config.DRAG_DROP_ENABLED
        self.dragging_item = None
        self.drag_offset = (0, 0)

        # UI and tab-related attributes
        self.focused_btn = None
        self.tab_btns = []
        self.tab_type = None
        self.cached_mouse_pos = None
        self.orientation = None

        # Defense-related attributes
        self.defensetypes = defensetypes
        self.defenselist = [
            cannon.Cannon(self.screen, market=self),
            barrier.Barrier(self.screen, market=self),
            mortar.Mortar(self.screen, market=self)
        ]

        # Temporary defense object (possibly for previewing or ghosting)
        self.temp_defense = defense.Defense(
            self.screen, market=self, width=0, height=0, hp=0, dmg=0, cost=0,
            snapbox=0, type="default", scope=0, has_front=False, front_img=False
        )

        # Placed defenses list
        self.placed_defenses = []

        # Ghost mode for UI interactions
        self.is_ghost_active = False

        # Load and scale item icon
        self.item_icon = pygame.image.load("assets/up-arrow.png").convert_alpha()
        self.item_icon = pygame.transform.scale(self.item_icon, (20, 20))

                # Pre-calculate the path points using the current screen dimensions.
        screen_width, screen_height = screen.get_size()
        self.path_points = path.generate_path_points(screen_width, screen_height)


        self.start_time = None
        self.is_animating = False

        self.make_pin_btn()
        self.make_tab_btns()
        self.setup_inventory()
        self.make_containers() #FIXX SO IT GETS USED
        self.draw_defenses(screen)

    


    def setup_inventory(self):
        self.inventory = [False] * 10  
        self.all_container_indices = [(r, c) for r in range(self.num_rows) for c in range(self.num_cols)]
        self.chunk_size = len(self.all_container_indices) // (len(self.tab_btns)-1)  # Determine how many elements per sublist
        self.container_index = [self.all_container_indices[i * self.chunk_size: (i + 1) * self.chunk_size] for i in range(3)]        

    def make_containers(self):
        # Get grid positions for all containers (row, col tuples).
        self.all_container_indices = [(r, c) for r in range(self.num_rows) for c in range(self.num_cols)]
        # Divide the total containers among categories (using ceiling division).
        containers_per_tab = math.ceil(len(self.all_container_indices) / len(self.defensetypes))
        self.containers_by_tab = {}
        self.containers_all = []
        container_id = 0
        for cat in range(len(self.defensetypes)):
            self.containers_by_tab[cat] = []
            for i in range(containers_per_tab):
                idx = cat * containers_per_tab + i
                if idx < len(self.all_container_indices):
                    row, col = self.all_container_indices[idx]
                    container = Container(container_id, row, col, cat)
                    self.containers_by_tab[cat].append(container)
                    self.containers_all.append(container)
                    container_id += 1

    def make_pin_btn(self):
        small_btn_width = 10
        small_btn_height = 10
        small_btn_x = self.rect.x + 5  # align with the market's left edge
        small_btn_y = self.rect.y - 5 + self.rect.height - small_btn_height  # bottom aligned with the market
        self.pin_btn = Marketbtn(
            self,
            small_btn_x,
            small_btn_y,
            small_btn_width,
            small_btn_height,
            border_radius=1,
            text="",
            color=(150, 150, 150),
            hover_color=(180, 180, 180)
        )
        
    def make_tab_btns(self):
        btn_height = 40
        btn_width = self.rect.width // 3
        for i in range(3):
            x_btn = self.rect.x + btn_width * i
            btn = Marketbtn(
                self,
                x_btn,
                self.rect.y,
                btn_width,
                btn_height,
                border_radius=0,
                text=f"{i+1}",
                color=self.non_focus_color,
            )
            self.tab_btns.append(btn)
        if self.market_has_been_opened == False:
            self.focused_btn = self.tab_btns[0]
        return self.tab_btns
    
    def get_filtered_defenses(self, tab_index):
        self.tab_type = self.defensetypes[tab_index]
        
        # Filter defenses that belong to the current tab
        filtered_defenses = [defense for defense in self.defenselist if defense.type == self.tab_type]
        
        if not filtered_defenses:
            for defense in self.defenselist:
                if defense.type == self.tab_type[2]:
                    filtered_defenses.append(defense)
        
        self.set_container_index(filtered_defenses)
        return filtered_defenses
    
    def set_container_index(self, defenses):
        # Reset the counter and assign indices for the given list of defenses
        Defense.local_container_index = 0
        for defense in defenses:
            defense.container_index = Defense.local_container_index
            Defense.local_container_index += 1

    def draw_defenses_for_tab(self, filtered_defenses):
        for defense in filtered_defenses:
            # Only update the position if the defense hasn't been placed yet.
            if defense not in self.placed_defenses and self.is_active:
                defense.pos = self.get_container_rect(defense.container_index).center
            defense.front_img = True
            defense.draw()
            if getattr(defense, "hasfront", False) and getattr(defense, "front_img", False):
                defense.draw_front_img()

    def get_container_drag_initiation(self, event, tab_index):
        for defense in self.get_filtered_defenses(tab_index):
            container_rect = self.get_container_rect(defense.container_index)
            if container_rect.collidepoint(event.pos):
                # Check which defense is being clicked based on the active tab btn
                if self.focused_btn == self.tab_btns[tab_index]:
                    if economy.balance >= defense.cost:
                        self.dragging_item = defense
                    else:
                        dark_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                        dark_surface.fill((0, 0, 0, 128))  # 50% transparent black

                        # Draw the semi-transparent dark overlay
                        self.screen.blit(dark_surface, (0, 0))

                        flash = get_flash_instance()
                        flash.trigger()


    def handle_dragging(self, defense):
        """Handles dragging logic for a defense item."""
        if not defense:
            return  # Avoid errors if defense is None
        
        self.is_ghost_active = True

        # Get current mouse position as a tuple.
        mouse_pos = pygame.mouse.get_pos()

        # Always update the defense's position.
        defense.pos = mouse_pos

        # Check if the current mouse position is near the path.
        # Adjust the tolerance value as needed.
        # 15 is golden
        near_path = self.is_near_path(mouse_pos, tolerance=20)

        if near_path and isinstance(defense, barrier.Barrier):
            # If near the path, update orientation and rotate the defense.
            self.orientation, _ = self.get_continuous_path_orientation(mouse_pos)
            # Set new angle: if orientation is non-vertical, rotate 90°, otherwise 0°.
            new_angle = 90 if self.orientation != "vertical" else 0
            defense.last_angle = new_angle  # Save this as the last rotation value.
            defense.angle = new_angle
            defense.ondrag(mouse_pos)
        else:
            defense.draw()

        # Validate placement (flash if invalid)
        invalid_placement_flash = get_invalid_placement_flash_instance()
        if not self.is_placeable(defense.pos, defense) and not self.rect.collidepoint(defense.pos):
            invalid_placement_flash.trigger()
        else:
            invalid_placement_flash.stop()
    
    def get_container_rect(self, container_index): #local container index instead
        # Calculate the total grid dimensions.
        grid_width = self.num_cols * self.container_size + (self.num_cols + 1) * self.gap
        grid_height = self.num_rows * self.container_size + (self.num_rows + 1) * self.gap
        vertical_offset = 20  # Moves the grid 20 pixels lower.

        # Center the grid inside self.rect.
        start_x = self.rect.x + (self.rect.width - grid_width) // 2
        start_y = self.rect.y + (self.rect.height - grid_height) // 2 + vertical_offset

        # Determine the row and column based on the tab index.
        if container_index % 2 == 0:
            row = container_index // 2
            col = 0
        else:
            row = (container_index - 1) // 2
            col = 1

        # Calculate the x and y coordinates for the container.
        container_x = start_x + self.gap + col * (self.container_size + self.gap)
        container_y = start_y + self.gap + row * (self.container_size + self.gap)

        return pygame.Rect(container_x, container_y, self.container_size, self.container_size)
    
    def get_container_center(self, category_index):
        """
        Returns the (x, y) coordinates for the center of the container (category)
        specified by its index.
        """
        rect = self.get_container_rect(category_index)
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
            #remember this!!!
            d = math.hypot(point[0] - midpoint[0], point[1] - midpoint[1])
        if d < min_dist:
            min_dist = d
            best_midpoint = (int(midpoint[0]), int(midpoint[1]))
        if min_dist <= snap_tolerance:
            return best_midpoint
        else:
            return None

    def is_placeable(self, point, defense, base_tolerance=15):
        """
        Determines if the given point is close enough to some path segment,
        using an increased tolerance in areas where the path orientation is continuous.
        Also ensures the point is on-screen.
        """
        if defense is None:
            return False  # If there's no defense, placement is invalid

        if not self.screen.get_rect().collidepoint(point):
            return False  # Ensure point is inside the screen

        # Get the orientation and check if the path is continuous at this point
        self.orientation, continuous = self.get_continuous_path_orientation(point)
        
        # Ensure defense has a `snapbox` attribute before accessing it
        tolerance = base_tolerance if continuous else 0

        # Check if the point is close to the path
        near_path = any(
            self.distance_to_segment(point, self.path_points[i], self.path_points[i + 1]) <= tolerance
            for i in range(len(self.path_points) - 1)
        )

        # Placement rules:
        if isinstance(defense, barrier.Barrier):
            return near_path  # Barriers must be near the path
        return not near_path  # Other defenses must be placed away from the path

    def place_item(self, event):

        """Handles placing an item when the user releases the mouse button."""
        if self.dragging_item:
            self.drop_point = event.pos
            print("drop point", self.drop_point)

            if self.is_placeable(self.drop_point, self.dragging_item):
                snapped_point = self.snap_point_to_path(self.drop_point)
                final_point = snapped_point if snapped_point is not None else self.drop_point
                print("final point", final_point)

                # Create a NEW instance instead of modifying the market's version
                placed_defense = type(self.dragging_item)(
                    self.screen, self  # Use the same constructor
                )
                placed_defense.pos = final_point  # Set position to the placed location
                
                self.placed_defenses.append(placed_defense)  # Store the placed defense
                economy.balance -= self.dragging_item.cost  # Deduct cost
                                
            # Stop invalid placement flash
            invalid_placement_flash = get_invalid_placement_flash_instance()
            invalid_placement_flash.stop()
            
            self.is_ghost_active = False

            # Reset dragging item without removing it from the market
            self.dragging_item = None



    def update(self, events):
        """Called each frame to update market UI based on user interaction."""
        for event in events:
            if self.is_active:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.rect.collidepoint(event.pos): #HERE
                        self.get_container_drag_initiation(event, self.tab_index)
                    elif not self.market_is_pinned and not self.rect.collidepoint(event.pos) and self.is_active:
                        self.toggle()
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.dragging_item:
                        self.place_item(event)

        # Update tab btns and market open state.
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos) and self.is_active:
                    for btn in self.tab_btns:
                        if btn.rect.collidepoint(event.pos):
                            if self.focused_btn and self.focused_btn != btn:
                                self.focused_btn.current_color = self.non_focus_color
                            self.focused_btn = btn
                            self.focused_btn.current_color = self.focus_color
                            self.tab_index = self.tab_btns.index(btn)
                            break
                else:
                    if not self.market_is_pinned:
                        self.is_active = False

    def draw(self, screen, cached_mouse_pos):
        """Called each frame to KEEP updated market UI on display."""

        if self.is_animating:
            current_time = pygame.time.get_ticks() - self.start_time  # Calculate elapsed time
            distance = self.rect.width  # Move its own width to the right
            self.rect.x = self.screen.get_size()[0] - self.rect.width + formulas.ease_out_expo(current_time, 0, distance, 1000)  # Update position
            
            # Check if the animation is complete
            if current_time >= 1000:  # Assuming the animation lasts 1000 ms
                self.is_animating = False  # Stop the animation

        # Draw defenses for the currently focused tab (based on the focused btn)
        if self.is_active:
            #Drawing
            if not self.is_ghost_active:
                pygame.draw.rect(screen, self.current_color, self.rect)
                for container_index in range(len(self.get_filtered_defenses(self.tab_index))):
                    container_rect = self.get_container_rect(container_index)
                    pygame.draw.rect(screen, (15, 15, 15), container_rect, border_radius=12)
                for btn in self.tab_btns:
                    btn.draw(self.screen)
                if self.tab_btns:
                    self.focused_btn.current_color = self.focus_color
                self.pin_btn.draw(self.screen)
                if self.pin_btn.rect.collidepoint(cached_mouse_pos):
                    pygame.draw.rect(screen, (255, 255, 255), self.pin_btn.rect, 0, border_radius=1)
                    if pygame.mouse.get_pressed()[0]:
                        if not self.pin_btn_pressed:
                            self.market_is_pinned = not self.market_is_pinned
                            self.pin_btn_pressed = True
                    else:
                        self.pin_btn_pressed = False
                    self.pin_btn.current_color = (255, 255, 255) if self.market_is_pinned else (150, 150, 150)
                focused_tab_index = self.tab_btns.index(self.focused_btn)
                self.tab_type = self.defensetypes[focused_tab_index]  #behövs?
                self.get_filtered_defenses(focused_tab_index)
                self.draw_defenses_for_tab(self.get_filtered_defenses(focused_tab_index))
                
            #Logic 
            if self.dragging_item:
                self.handle_dragging(self.dragging_item)
            # Update the active flash reference to the new flash
            self.flash = self.new_flash
            if self.flash and self.flash.is_active and self.flash != self.new_flash:
                self.flash.stop()

            # Now update and draw the flash
            self.flash.update()
            self.flash.draw()
            self.invalid_placement_flash.update()
            self.invalid_placement_flash.draw()
            
    def draw_defenses(self, screen):
        """
        Draws all placed defenses so they remain visible regardless
        of whether the market menu is open.
        """
        for defense in self.placed_defenses:
            if isinstance(defense, barrier.Barrier) and self.is_near_path(defense.pos, tolerance=10):
                defense.ondrag(defense.pos)
            else:
                defense.draw()

    def toggle(self):
        """Toggles the market state (open/close)."""
        self.market_has_been_opened = True
        self.is_active = not self.is_active
        self.btn_is_active = not self.btn_is_active

        if self.is_active:
            self.start_time = pygame.time.get_ticks()  # Record the start time
            self.is_animating = True  # Start animation when opening the market
        # No action required
def make_market(screen, width=175, height=450):
    return Market(screen, width=width, height=height)
    

#class Upgradebtn:
    def __init__(self, x, y, width, height, container_index):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (50, 205, 50)
        self.hover_color = (70, 225, 70)

    def draw(self, screen):    # Calculate the container index (assuming row-major order).
        container_index = Market.row * Market.num_cols + Market.col
        if self.inventory[container_index]:
            # Define the upgrade btn dimensions and position.
            upgrade_btn_width = 20
            upgrade_btn_height = 20
            upgrade_btn_color = (50, 205, 50)
            btn_padding = 2
            btn_x = Market.rect.x + Market.container_size - upgrade_btn_width - btn_padding
            btn_y = Market.rect.y + Market.container_size - upgrade_btn_height - btn_padding
            upgrade_btn_rect = pygame.Rect(btn_x, btn_y, upgrade_btn_width, upgrade_btn_height)
            
            # Draw a green rounded rectangle as the upgrade btn.
            pygame.draw.rect(screen, (upgrade_btn_color), upgrade_btn_rect, border_radius=5)
            if Market.cached_mouse_pos.collidepoint(upgrade_btn_rect):
                current_upgrade_btn_color[container_index] = (70, 225, 70)
                if pygame.mouse.get_pressed()[0]:
                    self.current_upgrades[container_index] += 1
                    print(f"Upgraded container {container_index} to level {self.current_upgrades[container_index]}")
            # Draw a white upward arrow on the upgrade btn.
            arrow_points = [
                (btn_x + upgrade_btn_width // 2, btn_y + 4),
                (btn_x + 4, btn_y + upgrade_btn_height - 4),
                (btn_x + upgrade_btn_width - 4, btn_y + upgrade_btn_height - 4)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), arrow_points)

