from turtle import onclick
import pygame
import other.constants
import economy
import other.config  # configuration file for drag-and-drop settings
import math
import time
import path.pathgen  # used to generate the path points
import defenses.barrier as barrier
import defenses.defense as defense
import defenses.mortar as mortar
import defenses.cannon as cannon
import defenses.reverser as reverser
from defenses.defense import Defense
import ui.effects as effects
import other.formulas
import enemies

import pygame



class Button:
    def __init__(
            self,
            market=None,
            xpos=0,
            ypos=0,
            width=100,
            height=40,
            border_radius=5,
            text="Button",
            font="Arial",
            text_size=20,
            bold=False,
            icon=None,
            color=(200, 200, 200),
            hover_color=(150, 150, 150),
            text_color=(0, 0, 0),
            transition_time=0.2,
            on_click=None,
            on_hover=None,
            toggle=False
        ):
            self.market = market
            self.xpos = xpos  # Store position
            self.ypos = ypos
            self.width = width  # Store size
            self.height = height
            self.border_radius = border_radius
            self.font = pygame.font.SysFont(font, text_size, bold)
            self.icon = icon
            self.text = text
            self.color = color
            self.hover_color = hover_color
            self.text_color = text_color
            self.transition_time = transition_time
            self.on_click = on_click
            self.on_hover = on_hover
            self.toggle = toggle

            # Create button rectangle
            self.rect = pygame.Rect(self.xpos, self.ypos, self.width, self.height)
        

            # Transition / hover state
            self.transition_start = None  # Track transition start time
            self.hovering = False
            self.current_color = self.color  # Default to normal color

            # Debugging - Check if button initializes properly
            print(f"Button '{self.text}' created at {self.xpos}, {self.ypos}, {self.width}x{self.height}")


    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=self.border_radius)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def update(self):
        
        is_hovering = self.is_hovered()

        # Start transition if hover state changes
        if is_hovering != self.hovering:
            self.hovering = is_hovering
            self.transition_start = time.time()

            if self.on_hover and is_hovering:
                self.on_hover()

                # Handle smooth transition
        if self.transition_start is not None and self.transition_time:  # Ensure transition_time is valid
            elapsed = time.time() - self.transition_start
            t = min(elapsed / self.transition_time, 1) if self.transition_time else 1  # Avoid division by None

            if self.hovering:
                self.current_color = self.lerp(self.color, self.hover_color, t) if self.hover_color else self.color
            else:
                self.current_color = self.lerp(self.hover_color, self.color, t) if self.hover_color else self.color

            # Stop transition if completed
            if t >= 1:
                self.transition_start = None


    def handle_event(self, event_list):
            """Handles button click events and stops propagation by removing the event."""
            for event in event_list[:]:  # Iterate over a copy
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, "rect") and self.rect.collidepoint(event.pos) and self.market.btn_is_active:  # Ensure rect exists
                        print(f"Button clicked at {event.pos}")  # Debug print
                        if self.on_click:
                            self.on_click()
                        event_list.remove(event)  # Remove the event to stop further propagation
                        return True  # Button handled the event
            return False

    @staticmethod
    def lerp(color1, color2, t):
        """Linear interpolation between two RGB colors."""
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t),
        )

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
        screen_width,
        screen_height,
        margin,
        xpos,
        ypos,
        width,
        height,
        text,
        color,
        text_color,
        defense_types,
        defense_list,
        container_spacing, #container_spacing
    ):
        #self.defense_list = defense_list


        # Initialize basic attributes
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin = margin
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.text_color = text_color
        self.defense_types = defense_types
        self.defense_list = defense_list
        self.container_spacing = container_spacing

        self.market_has_been_opened = False
        self.tab_index = 0
        self.economy_flash_inst = effects.Economy_flash(self.screen)
        self.placement_flash_inst = effects.placement_flash(self.screen)
        self.rect = pygame.Rect(xpos, ypos, width, height)  
        self.clickable_rect = pygame.Rect(xpos, ypos-60, width, height+60)
        self.btn_list = []

    
        self.market_btn = None  # Initialize as None
        self.make_market_btn()  # ✅ Create the button

        # Containers for the grid layout #eventually expand my markets arguments with similar...
        self.num_cols = 2
        self.num_rows = 5
        self.container_size = 70

        # Colors
        self.color = color
        self.current_color = color
        self.text_color = text_color
        self.non_focus_color = other.constants.color_theme
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
        self.drag_drop_enabled = other.config.DRAG_DROP_ENABLED
        self.dragging_item = None
        self.drag_offset = (0, 0)

        # UI and tab-related attributes
        
        self.focused_btn = None
        self.tab_btns = []
        self.tab_type = None
        self.orientation = None

        # Defense-related attributes
        self.defense_types = defense_types
        self.defense_list = [
            cannon.Cannon(self.screen, market=self, enemies_list=enemies.enemies_list, width=4, height=4, hp=250, dmg=1, cost=1000, scope=400, tags=("default", "aim"), has_front=False, front_img=False),
            barrier.Barrier(self.screen, market=self, enemies_list=enemies.enemies_list, width=50, height=50, hp=50, dmg=1, cost=500, scope=False, tags=("other"), has_front=False, front_img=False),
            mortar.Mortar(self.screen, market=self, enemies_list=enemies.enemies_list, width=4, height=4, hp=300, dmg=3, cost=5000, scope=300, tags=("default", "aim"), has_front=False, front_img=False),
            reverser.Reverse(self.screen, market=self, enemies_list=enemies.enemies_list, width=35, height=50, hp=50, dmg=1, cost=500, scope=50, tags=("other",), has_front=False, front_img=False)
            
        ]

        # Placed defenses list
        self.placed_defenses = []

        # Ghost mode for UI interactions
        self.is_ghost_active = False

        # Load and scale item icon
        self.item_icon = pygame.image.load("assets/up-arrow.png").convert_alpha()
        self.item_icon = pygame.transform.scale(self.item_icon, (20, 20))

                # Pre-calculate the path points using the current screen dimensions.
        screen_width, screen_height = screen.get_size()
        self.path_points = path.pathgen.generate_path_points(screen_width, screen_height)


        self.start_time = None
        self.is_animating = False

        self.make_pin_btn()
        self.make_tab_btns()
        self.setup_inventory()
        self.make_containers() #FIXX SO IT GETS USED
        self.draw_defenses()

        


        if self.market_has_been_opened == False:
            self.focused_btn = self.tab_btns[0]

    def setup_inventory(self):
        self.inventory = [False] * 10  
        self.all_container_indices = [(r, c) for r in range(self.num_rows) for c in range(self.num_cols)]
        self.chunk_size = len(self.all_container_indices) // (len(self.tab_btns)-1)  # Determine how many elements per sublist
        self.container_index = [self.all_container_indices[i * self.chunk_size: (i + 1) * self.chunk_size] for i in range(3)]        

    def make_containers(self):
        # Get grid positions for all containers (row, col tuples).
        self.all_container_indices = [(r, c) for r in range(self.num_rows) for c in range(self.num_cols)]
        # Divide the total containers among categories (using ceiling division).
        containers_per_tab = math.ceil(len(self.all_container_indices) / len(self.defense_types))
        self.containers_by_tab = {}
        self.containers_all = []
        container_id = 0
        for cat in range(len(self.defense_types)):
            self.containers_by_tab[cat] = []
            for i in range(containers_per_tab):
                idx = cat * containers_per_tab + i
                if idx < len(self.all_container_indices):
                    row, col = self.all_container_indices[idx]
                    container = Container(container_id, row, col, cat)
                    self.containers_by_tab[cat].append(container)
                    self.containers_all.append(container)
                    container_id += 1

    def update_buttons(self):
        """Update the position of buttons dynamically based on self.rect."""
        for i, btn in enumerate(self.tab_btns):
            btn.rect.x = self.rect.x + (self.rect.width // len(self.tab_btns)) * i
            btn.rect.y = self.rect.y

        # Update pin button position
        self.pin_btn.rect.x = self.rect.x + 5
        self.pin_btn.rect.y = self.rect.y + self.rect.height - self.pin_btn.rect.height - 5
        
    def make_info_btn(self):
        pass

    def make_upgrade_btn(self):
        """Creates the upgrade button."""
        upgrade_btn_width = 50
        upgrade_btn_height = 20
        upgrade_btn_x = self.rect.x + self.rect.width - upgrade_btn_width - 5  # Align to the right
        upgrade_btn_y = self.rect.y + self.rect.height - upgrade_btn_height - 5  # Bottom aligned

        self.upgrade_btn = Button(
            self,
            upgrade_btn_x,
            upgrade_btn_y,
            upgrade_btn_width,
            upgrade_btn_height,
            border_radius=3,
            text="Upgrade",
            font="Arial",
            text_size=14,
            bold=True,
            icon=None,
            color=(100, 100, 250),
            hover_color=(120, 120, 255),
            text_color=(255, 255, 255),
            transition_time=0.2,
            on_click=lambda: print("Upgrade Clicked"),
            on_hover=None,
            toggle=False
        )
        self.btn_list.append(self.upgrade_btn)

    def make_pin_btn(self):
        """Creates the pin button to keep the market open."""
        pin_btn_width = 10
        pin_btn_height = 10
        pin_btn_x = self.rect.x + 5  # Align with the market's left edge
        pin_btn_y = self.rect.y + self.rect.height - pin_btn_height - 5  # Bottom aligned

        self.pin_btn = Button(
            self,
            pin_btn_x,
            pin_btn_y,
            pin_btn_width,
            pin_btn_height,
            border_radius=1,
            text="",
            font="Arial",
            text_size=10,
            bold=False,
            icon=None,
            color=(150, 150, 150),  # Default gray
            hover_color=None,
            text_color=(255, 255, 255),
            transition_time=0.25,
            on_click=lambda: self.toggle_pin(),  # Call toggle_pin when clicked
            on_hover=None,
            toggle=False
        )

        self.btn_list.append(self.pin_btn)
        # Initialize state variables
        self.pin_btn_pressed = False
        self.market_is_pinned = False

    def toggle_pin(self):
        """Toggle pin button state and update market pin state."""
        self.pin_btn.toggle = not self.pin_btn.toggle  # Toggle state
        self.market_is_pinned = self.pin_btn.toggle  # Sync market pin state

    def update_pin_button(self):
        """Handles pin button events, updates its color, and draws it."""
        # Update button color based on toggle state:
        self.pin_btn.current_color = (255, 255, 255) if self.pin_btn.toggle else (150, 150, 150)
        # Check for mouse interaction on the pin button:
        if self.pin_btn.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.pin_btn_pressed:
                    self.toggle_pin()
                    self.pin_btn_pressed = True
            else:
                self.pin_btn_pressed = False
        # Draw the pin button on the screen:
        self.pin_btn.draw(self.screen)



    def on_tab_click(self, index):
        """Handles tab button click."""
        if self.is_active:
            self.focused_btn = self.tab_btns[index]  # Update the current tab index

    def make_tab_btns(self):
        """Creates tab buttons for different sections of the market."""
        self.tab_btn_height = 40
        tab_btn_width = self.rect.width // 3
            
        for i in range(3):
            x_tab_btn = self.rect.x + tab_btn_width * i
            tab_btn = Button(
                self,
                x_tab_btn,
                self.rect.y,
                tab_btn_width,
                self.tab_btn_height,
                border_radius=0,
                text=f"Tab {i+1}",
                font="Arial",
                text_size=16,
                bold=False,
                icon=None,
                color=self.non_focus_color,
                hover_color=None,
                text_color=(255, 255, 255),
                transition_time=None,
                on_click=lambda i=i: self.on_tab_click(i),  # Fix on_click
                on_hover=None,
                toggle=False
            )
            self.tab_btns.append(tab_btn)
            self.btn_list.append(tab_btn)
        return self.tab_btns

    
    def make_market_btn(self):
        margin = 20  # Margin from the edges
        btn_width = 140
        btn_height = 70

        xpos = self.screen_width - btn_width - margin  # Align right with margin
        ypos = margin  # Top position with margin

        self.market_btn = Button(
            self,
            xpos=xpos,
            ypos=ypos,
            width=btn_width,
            height=btn_height,
            border_radius=10,
            text="Market",
            font="Arial",
            text_size=24,
            bold=True,
            icon=None,  # No icon for now
            color=(65, 205, 65),
            hover_color=(100, 255, 100),
            text_color=(255, 255, 255),
            transition_time=0.25,
            on_click=lambda: self.toggle(),  # ✅ Use wrapper function
            on_hover=lambda: print("Hovering over Market Button"),
            toggle=False
        )
        self.btn_list.append(self.market_btn)
        return self.market_btn

    
    def get_filtered_defenses(self, tab_index):
        self.tab_type = self.defense_types[tab_index]

        filtered_defenses = [defense for defense in self.defense_list if self.tab_type in defense.tags]
        if not filtered_defenses and self.tab_type == self.defense_types[2]:
            for defense in self.defense_list:
                if self.defense_types[2] in defense.tags:
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
            if getattr(defense, "has_front", False) and getattr(defense, "front_img", False):
                defense.draw_front_img()
            else: 
                defense.draw()

    def get_container_drag_initiation(self, event, tab_index):
        for defense in self.get_filtered_defenses(tab_index):
            container_rect = self.get_container_rect(defense.container_index)
            if container_rect.collidepoint(event.pos):
                if self.focused_btn == self.tab_btns[tab_index]:
                    if economy.balance >= defense.cost:
                        self.dragging_item = defense
                    else:
                        dark_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                        dark_surface.fill((0, 0, 0, 128))  # 50% transparent black

                        # Draw the semi-transparent dark overlay
                        self.screen.blit(dark_surface, (0, 0))

                        self.economy_flash_inst.trigger()

    def handle_dragging(self, defense):
        """Handles dragging logic for a defense item."""
        if not defense:
            return  # Avoid errors if defense is None

        self.is_ghost_active = True

        # Update the defense's position with the current mouse position.
        defense.pos = pygame.mouse.get_pos()

        # Check if the current mouse position is near the path (tolerance 15).
        near_path = self.is_near_path(defense.pos, tolerance=15)

        # If the defense is a Barrier, apply barrier-specific logic.
        if isinstance(defense, barrier.Barrier):
            if near_path:
                # If intended as a method call, consider changing to defense.rotate()
                defense.rotate  
                defense.angle = 90
                defense.isrotated = True
            defense.front_img = False

        # Draw the defense item.
        defense.draw()

        # Validate placement (flash if invalid).
        if not self.is_placeable(defense.pos, defense):
            self.placement_flash_inst.trigger()
        else:
            self.placement_flash_inst.stop()

    
    def get_container_rect(self, container_index): #local container index instead
        # Calculate the total grid dimensions.
        grid_width = self.num_cols * self.container_size + (self.num_cols + 1) * self.container_spacing
        grid_height = self.num_rows * self.container_size + (self.num_rows + 1) * self.container_spacing
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
        container_x = start_x + self.container_spacing + col * (self.container_size + self.container_spacing)
        container_y = start_y + self.container_spacing + row * (self.container_size + self.container_spacing)

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
        
        "HERE"

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
            if self.is_placeable(self.drop_point, self.dragging_item):
                snapped_point = self.snap_point_to_path(self.drop_point)
                final_point = snapped_point if snapped_point is not None else self.drop_point
                
                # Create a NEW instance instead of modifying the market's version
                placed_defense = type(self.dragging_item)(
                    self.screen, 
                    market=self, 
                    enemies_list=self.dragging_item.enemies_list, 
                    width=self.dragging_item.width, 
                    height=self.dragging_item.height, 
                    hp=self.dragging_item.hp, 
                    dmg=self.dragging_item.dmg, 
                    cost=self.dragging_item.cost, 
                    scope=self.dragging_item.scope, 
                    tags=self.dragging_item.tags, 
                    has_front=self.dragging_item.has_front, 
                    front_img=self.dragging_item.front_img
                )
                placed_defense.pos = final_point  # Set position to the placed location
                
                self.placed_defenses.append(placed_defense)  # Store the placed defense
                economy.balance -= self.dragging_item.cost  # Deduct cost


            self.is_ghost_active = False

            # Reset dragging item without removing it from the market
            self.dragging_item = None
            self.placement_flash_inst.stop()     

    def draw_defenses(self):
        """
        Draws all placed defenses so they remain visible regardless
        of whether the market menu is open.
        """
        for defense in self.placed_defenses:
            if isinstance(defense, barrier.Barrier) and self.is_near_path(defense.pos, tolerance=10) and self.get_path_orientation(defense.pos) == "horizontal":
                defense.angle = 90
            defense.draw()

    def toggle(self):
        """Toggles the market state (open/close)."""
        self.market_has_been_opened = True
        self.is_active = not self.is_active
        self.btn_is_active = not self.btn_is_active
        if self.is_active:
            self.start_time = pygame.time.get_ticks()  # Record the start time
            self.is_animating = True  # Start animation when opening the market 
            print("Active")
        else: 
            print("Unactive")

    def update(self, event_list):

        """Called each frame to update market UI based on user interaction."""
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.market_is_pinned and not self.clickable_rect.collidepoint(event.pos) and self.is_active:
                    self.toggle()
                    print("Clicked outside market, closing...")  # Debugging
                else:
                    self.get_container_drag_initiation(event, self.tab_index)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging_item:
                    self.place_item(event)

        # Update tab btns and market open state.
        for event in event_list:
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

    def draw(self, screen):
        """Called each frame to KEEP updated market UI on display."""

        if self.is_animating:
            current_time = pygame.time.get_ticks() - self.start_time  # Calculate elapsed time
            distance = -self.rect.width  # Move its own width to the right
            self.rect.x = self.screen.get_size()[0] - self.rect.width + other.formulas.ease_out_expo(current_time, self.rect.width, distance, 750)  # Update position
            
            # Check if the animation is complete
            if current_time >= 750:  # Assuming the animation lasts 1000 ms
                self.is_animating = False  # Stop the animation
                
        if self.is_active:
            self.update_buttons()  # Update button positions
            if not self.is_ghost_active:
                pygame.draw.rect(screen, self.color, self.rect)
                for container_index in range(len(self.get_filtered_defenses(self.tab_index))):
                    container_rect = self.get_container_rect(container_index)
                    pygame.draw.rect(screen, (15, 15, 15), container_rect, border_radius=12)
                for btn in self.tab_btns:
                    btn.draw(self.screen)
                if self.tab_btns:
                    self.focused_btn.current_color = self.focus_color

                self.update_pin_button()

                focused_tab_index = self.tab_btns.index(self.focused_btn)
                self.tab_type = self.defense_types[focused_tab_index]  #behövs?
                self.get_filtered_defenses(focused_tab_index)
                self.draw_defenses_for_tab(self.get_filtered_defenses(focused_tab_index))
                
            #Logic 
            if self.dragging_item:
                self.handle_dragging(self.dragging_item)

            # Now update and draw the flash
            self.economy_flash_inst.update()
            self.economy_flash_inst.draw()
            self.placement_flash_inst.update()
            self.placement_flash_inst.draw()
            
def make_market(
        screen,
        screen_width,
        screen_height,
        margin=0,
        xpos=None,  # Default to None if not provided
        ypos=0,
        width=175,
        height=450,
        text="Items...",
        color=None,  # Use None or default it to a theme later
        text_color=(255, 255, 255),
        defense_types=None,  # Default to None to avoid mutable default arguments
        defense_list=None,   # Same as above
        container_spacing=5,

    ):

    if xpos is None:
        xpos = screen_width - width  # Set DYNamically

    # Provide default values if None was passed
    if color is None:
        color = other.constants.color_theme
    if defense_types is None:
        defense_types = ["default", "special", "other"]
    if defense_list is None:
        defense_list = []

    return Market(
        screen,
        screen_width,
        screen_height,
        margin,
        xpos,
        ypos,
        width,
        height,
        text,
        color,
        text_color,
        defense_types,
        defense_list,
        container_spacing,
    ) 

def update_market(event_list, market_instance, button_instance):
    if button_instance.handle_event(event_list) and market_instance.btn_is_active:
        market_instance.toggle()  # This should handle activation internally

        # Remove MOUSEBUTTONDOWN events to prevent click propagation
        event_list = [e for e in event_list if e.type != pygame.MOUSEBUTTONDOWN]

    return event_list

