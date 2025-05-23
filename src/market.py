import pygame
from other import helper
import other.colors
import economy
import other.config                                                 
import math
import time
import path.pathx                                    
import defenses.barrier as barrier
import defenses.defense as defense
import defenses.mortar as mortar
import defenses.cannon as cannon
import defenses.reverser as reverser
from defenses.defense import Defense
import ui.effects as effects
import other.formulas
import enemies.enemies as enemies

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
            self.xpos = xpos                  
            self.ypos = ypos
            self.width = width              
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

                                     
            self.rect = pygame.Rect(self.xpos, self.ypos, self.width, self.height)
        

                                      
            self.transition_start = None                               
            self.hovering = False
            self.current_color = self.color                           

                                                              
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

                                                 
        if is_hovering != self.hovering:
            self.hovering = is_hovering
            self.transition_start = time.time()

            if self.on_hover and is_hovering:
                self.on_hover()

                                          
        if self.transition_start is not None and self.transition_time:                                   
            elapsed = time.time() - self.transition_start
            t = min(elapsed / self.transition_time, 1) if self.transition_time else 1                          

            if self.hovering:
                self.current_color = self.lerp(self.color, self.hover_color, t) if self.hover_color else self.color
            else:
                self.current_color = self.lerp(self.hover_color, self.color, t) if self.hover_color else self.color

                                          
            if t >= 1:
                self.transition_start = None


    def handle_event(self, event_list):
            for event in event_list[:]:                       
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, "rect") and self.rect.collidepoint(event.pos) and self.market.btn_is_active:                      
                        print(f"Button clicked at {event.pos}")               
                        if self.on_click:
                            self.on_click()
                        event_list.remove(event)                                                
                        return True                            
            return False

    @staticmethod
    def lerp(color1, color2, t):
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t),
        )

                                                      
class Container:
    def __init__(self, container_id, row, col, tab):
        self.id = container_id                                  
        self.row = row                                     
        self.col = col                                        
        self.tab = tab                                      
        self.defense = None                                              

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
        num_rows,
        num_cols,
        vertical_offset,
        container_size,
        container_spacing,                   
    ):
                                         


                                     
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
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.vertical_offset = vertical_offset
        self.container_size = container_size
        self.container_spacing = self.width-self.num_cols*self.container_size-self.vertical_offset/2

        self.market_has_been_opened = False
        self.tab_index = 0
        self.economy_flash_inst = effects.Economy_flash(self.screen)
        self.placement_flash_inst = effects.placement_flash(self.screen)
        self.rect = pygame.Rect(xpos, ypos, width, height)  
        self.clickable_rect = pygame.Rect(xpos, ypos-60, width, height+60)
        self.btn_list = []

    
        self.market_btn = None                      
        self.make_market_btn()  

                
        self.color = color
        self.current_color = color
        self.text_color = text_color


                       
        self.text = text
        self.font = pygame.font.SysFont(None, 24)

                                  
        self.is_active = False                             
        self.btn_is_active = True                                 
        self.market_is_pinned = False                             
        self.pin_btn_pressed = False                              

                                     
        self.drag_drop_enabled = other.config.DRAG_DROP_ENABLED
        self.dragging_item = None
        self.drag_offset = (0, 0)

                                       
        
        self.focused_btn = None
        self.tab_btns = []
        self.tab_type = None
        self.orientation = None

                                    
        self.defense_types = defense_types
        self.defense_list = [
            cannon.Cannon(
                screen=self.screen,
                market=self,
            ),
            
            barrier.Barrier(
                screen=self.screen,
                market=self,
            ),
            
            mortar.Mortar(
                screen=self.screen,
                market=self,
            ),

                     
            
        ]

                              
        self.placed_defenses = []

                                        
        self.is_ghost_active = False

                                                                                    
        screen_width, screen_height = screen.get_size()
        self.path_points = path.pathx.get_path_points()


        self.start_time = None
        self.is_animating = False

        self.make_pin_btn()
        self.make_tab_btns()
        self.setup_inventory()
        self.make_containers()                      

        


        if self.market_has_been_opened == False:
            self.focused_btn = self.tab_btns[0]

    def setup_inventory(self):
        self.inventory = [False] * 10  
        self.all_container_indices = [(r, c) for r in range(self.num_rows) for c in range(self.num_cols)]
        self.chunk_size = len(self.all_container_indices) // (len(self.tab_btns)-1)                                           
        self.container_index = [self.all_container_indices[i * self.chunk_size: (i + 1) * self.chunk_size] for i in range(3)]        

    def make_containers(self):
                                                                  
        self.all_container_indices = [(r, c) for r in range(self.num_rows) for c in range(self.num_cols)]
                                                                                
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
        for i, btn in enumerate(self.tab_btns):
            btn.rect.x = self.rect.x + (self.rect.width // len(self.tab_btns)) * i
            btn.rect.y = self.rect.y

                                    
        self.pin_btn.rect.x = self.rect.x + 5
        self.pin_btn.rect.y = self.rect.y + self.rect.height - self.pin_btn.rect.height - 5
        
    def make_info_btn(self,x,y):

        info_btn_width = 15
        info_btn_height = info_btn_width

        info_is_seen = False

        self.info_btn = Button(
            self,
            x+self.container_size-info_btn_width+3,
            y-3,
            info_btn_width,
            info_btn_height,
            border_radius=3,
            text="i",
            font="Arial",
            text_size=14,
            bold=True,
            icon=None,
            color=other.colors.tabs_focus_color,
            hover_color=(120, 120, 255),
            text_color=(255, 255, 255),
            transition_time=0.2,
            on_click=lambda: print("Upgrade Clicked"),
            on_hover=None,
            toggle=False
        )
        self.btn_list.append(self.info_btn)

    def make_upgrade_btn(self, x, y):
        upgrade_btn_width = 20
        upgrade_btn_height = upgrade_btn_width

        self.upgrade_btn = Button(
            self,
            x,
            y,
            upgrade_btn_width,
            upgrade_btn_height,
            border_radius=3,
            text="+",
            font="Arial",
            text_size=14,
            bold=True,
            icon=None,
            color=other.colors.market_btn_color,
            hover_color=other.colors.market_btn_hover_color,
            text_color=(255, 255, 255),
            transition_time=0.2,
            on_click=lambda: print("Upgrade Clicked"),
            on_hover=None,
            toggle=False
        )
        self.btn_list.append(self.upgrade_btn)

    def make_sell_btn(self, defense, x , y):
        sell_btn_width = 20
        sell_btn_height = sell_btn_width

        self.sell_btn = Button(
            self,
            x,
            y+20,
            sell_btn_width,
            sell_btn_height,
            border_radius=3,
            text="+",
            font="Arial",
            text_size=14,
            bold=True,
            icon=None,
            color=other.colors.sell_btn_color,
            hover_color=other.colors.market_btn_hover_color,
            text_color=(255, 255, 255),
            transition_time=0.2,
            on_click=lambda: self.refund(defense),
            on_hover=None,
            toggle=False
        )
        self.btn_list.append(self.sell_btn)

    def refund(self, defense):
        refund = defense.cost // 2
        economy.balance += refund
        if defense in self.placed_defenses:
            self.placed_defenses.remove(defense)

    def draw_defense_ui(self):
        
        self.upgrade_btn.draw(self.screen)
        self.sell_btn.draw(self.screen)

    def make_pin_btn(self):
        pin_btn_width = 10
        pin_btn_height = pin_btn_width
        pin_btn_x = self.rect.x + 5                                     
        pin_btn_y = self.rect.y + self.rect.height - pin_btn_height - 5                  

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
            color=(150, 150, 150),                
            hover_color=None,
            text_color=(255, 255, 255),
            transition_time=0.25,
            on_click=lambda: self.toggle_pin(),                                
            on_hover=None,
            toggle=False
        )

        self.btn_list.append(self.pin_btn)
                                    
        self.pin_btn_pressed = False
        self.market_is_pinned = False

    def toggle_pin(self):
        self.pin_btn.toggle = not self.pin_btn.toggle                
        self.market_is_pinned = self.pin_btn.toggle                         

    def update_pin_button(self):
                                                    
        self.pin_btn.current_color = (255, 255, 255) if self.pin_btn.toggle else (150, 150, 150)
                                                        
        if self.pin_btn.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.pin_btn_pressed:
                    self.toggle_pin()
                    self.pin_btn_pressed = True
            else:
                self.pin_btn_pressed = False
                                            
        self.pin_btn.draw(self.screen)



    def on_tab_click(self, index):

        if self.is_active:
            self.focused_btn = self.tab_btns[index]                                

    def make_tab_btns(self):

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
                color=other.colors.market_color,
                hover_color=None,
                text_color=(255, 255, 255),
                transition_time=None,
                on_click=lambda i=i: self.on_tab_click(i),                
                on_hover=None,
                toggle=False
            )
            self.tab_btns.append(tab_btn)
            self.btn_list.append(tab_btn)
        return self.tab_btns

    
    def make_market_btn(self):
        margin = int(min(self.screen_width, self.screen_height) * 0.02)
        btn_width = int(min(self.screen_width, self.screen_height) * 0.225)
        btn_height = int(min(self.screen_width, self.screen_height) * 0.1)

        xpos = self.screen_width - btn_width - margin                           
        ypos = margin                            

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
            icon=None,                   
            color=(65, 205, 65),
            hover_color=(100, 255, 100),
            text_color=(255, 255, 255),
            transition_time=0.25,
            on_click=lambda: self.toggle(),
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
                                                                             
        Defense.local_container_index = 0
        for defense in defenses:
            defense.container_index = Defense.local_container_index
            Defense.local_container_index += 1

    def draw_content_for_tab(self, filtered_defenses):
        for defense in filtered_defenses:
                                                                             
            if defense not in self.placed_defenses and self.is_active:
                self.make_info_btn(self.get_container_rect(defense.container_index).x, self.get_container_rect(defense.container_index).y)
                defense.pos = self.get_container_rect(defense.container_index).center
            defense.draw()
            self.info_btn.draw(self.screen)

    def get_container_drag_initiation(self, event, tab_index):
        for defense in self.get_filtered_defenses(tab_index):
            container_rect = self.get_container_rect(defense.container_index)
            if container_rect.collidepoint(event.pos) and self.is_active:
                if self.focused_btn == self.tab_btns[tab_index]:
                    if economy.balance >= defense.cost:
                        defense.preview = False
                        self.dragging_item = defense
                    else:
                        dark_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                        dark_surface.fill((0, 0, 0, 128))                         

                                                                
                        self.screen.blit(dark_surface, (0, 0))

                        self.economy_flash_inst.trigger()

    def handle_dragging(self, defense):

        if not defense:
            return                                   

        self.is_ghost_active = True

                                                                        
        defense.pos = pygame.mouse.get_pos()

                                                                              
        near_path = self.is_near_path(defense.pos, tolerance=15)

                                                                    
        if isinstance(defense, barrier.Barrier):
            if near_path:
                                                                                     
                defense.rotate  
                defense.angle = 90
                defense.isrotated = True
            defense.preview = False

                                
        defense.draw()

                                                
        if not self.is_placeable(defense.pos, defense):
            self.placement_flash_inst.trigger()
        else:
            self.placement_flash_inst.stop()

    
    def get_container_rect(self, container_index):                               
                                              
        grid_width = self.num_cols * self.container_size + (self.num_cols + 1) * self.container_spacing
        grid_height = self.num_rows * self.container_size + (self.num_rows + 1) * self.container_spacing

                                           
        start_x = self.rect.x + (self.rect.width - grid_width) // 2
        start_y = self.rect.y + (self.rect.height - grid_height) // 2 + self.vertical_offset

                                                              
        if container_index % 2 == 0:
            row = container_index // 2
            col = 0
        else:
            row = (container_index - 1) // 2
            col = 1

                                                              
        container_x = start_x + self.container_spacing + col * (self.container_size + self.container_spacing)
        container_y = start_y + self.container_spacing + row * (self.container_size + self.container_spacing)

        return pygame.Rect(container_x, container_y, self.container_size, self.container_size)
    
    def get_container_center(self, category_index):

        rect = self.get_container_rect(category_index)
        return rect.center

    def distance_to_segment(self, point, start, end):
                                                                            
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
                                                                                   
        for i in range(len(self.path_points) - 1):
            seg_start = self.path_points[i]
            seg_end = self.path_points[i + 1]
            if self.distance_to_segment(point, seg_start, seg_end) <= tolerance:
                return True
        return False

    def get_path_orientation(self, point, tolerance=10):
                                                                         
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

        best_midpoint = None
        min_dist = float('inf')
                                              
        for i in range(len(self.path_points) - 1):
            A = self.path_points[i]
            B = self.path_points[i + 1]
                                                    
            midpoint = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
                             
            d = math.hypot(point[0] - midpoint[0], point[1] - midpoint[1])
        if d < min_dist:
            min_dist = d
            best_midpoint = (int(midpoint[0]), int(midpoint[1]))
        if min_dist <= snap_tolerance:
            return best_midpoint
        else:
            return None

    def is_placeable(self, point, defense, base_tolerance=15):

        if defense is None:
            return False                                               

        if not self.screen.get_rect().collidepoint(point):
            return False                                     
        
        "HERE"

                                                                               
        self.orientation, continuous = self.get_continuous_path_orientation(point)
        
                                                                      
        tolerance = base_tolerance if continuous else 0

                                                 
        near_path = any(
            self.distance_to_segment(point, self.path_points[i], self.path_points[i + 1]) <= tolerance
            for i in range(len(self.path_points) - 1)
        )

                          
        if isinstance(defense, barrier.Barrier):
            return near_path                                  
        return not near_path                                                    

    def place_item(self, event):

        if self.dragging_item:
            self.drop_point = event.pos
            if self.is_placeable(self.drop_point, self.dragging_item):
                snapped_point = self.snap_point_to_path(self.drop_point)
                final_point = snapped_point if snapped_point is not None else self.drop_point
                
                                                                                 
                                                                             
                placed_defense = type(self.dragging_item)(
                    **{  
                        "enemies_list": self.dragging_item.enemies_list, 
                        "width": self.dragging_item.width, 
                        "height": self.dragging_item.height, 
                        "hp": self.dragging_item.hp, 
                        "dmg": self.dragging_item.dmg, 
                        "cost": self.dragging_item.cost, 
                        "scope": self.dragging_item.scope, 
                        "tags": self.dragging_item.tags, 
                        "preview": self.dragging_item.preview
                    }
                )

                placed_defense.pos = final_point                                       
                
                self.placed_defenses.append(placed_defense)                            
                economy.balance -= self.dragging_item.cost               


            self.is_ghost_active = False

                                                                     
            self.dragging_item = None
            self.placement_flash_inst.stop()     

    def draw_defenses(self, event_list):

        if self.placed_defenses:
            for defense in self.placed_defenses:

                if isinstance(defense, barrier.Barrier):  
                    if (self.is_near_path(defense.pos, tolerance=10) and 
                        self.get_path_orientation(defense.pos) == "horizontal"):
                        defense.angle = 90                           

                if "aim" in defense.tags and hasattr(defense, "aim_at_enemy"):
                    defense.aim_at_enemy()                                           

                defense.draw()                                   


                for event in event_list:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        x,y = defense.pos
                        if defense.get_rect().collidepoint(mouse_pos) and defense.selected == False:
                            if defense.been_selected == False:
                                defense.been_selected = True
                                self.make_upgrade_btn(x,y)
                                self.make_sell_btn(defense,x,y)
                            defense.selected = True
                        elif not defense.get_rect().collidepoint(mouse_pos) and defense.selected == True:
                            defense.selected = False
            if  defense.selected == True:
                self.draw_defense_ui()

    def toggle(self):
        self.market_has_been_opened = True
        self.is_active = not self.is_active
        self.btn_is_active = not self.btn_is_active
        if self.is_active:
            self.start_time = pygame.time.get_ticks()                         
            self.is_animating = True                                            
            print("Active")
        else: 
            print("Unactive")

    def update(self, event_list):

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.market_is_pinned and not self.clickable_rect.collidepoint(event.pos) and self.is_active:
                    self.toggle()
                    print("Clicked outside market, closing...")             
                else:
                    self.get_container_drag_initiation(event, self.tab_index)
                    
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging_item:
                    self.place_item(event)

                                                
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos) and self.is_active:
                    for btn in self.tab_btns:
                        if btn.rect.collidepoint(event.pos):
                            if self.focused_btn and self.focused_btn != btn:
                                self.focused_btn.current_color = other.colors.tabs_color
                            self.focused_btn = btn
                            self.focused_btn.current_color = other.colors.tabs_focus_color
                            self.tab_index = self.tab_btns.index(btn)
                            break
                else:
                    if not self.market_is_pinned:
                        self.is_active = False

    def draw(self, screen):

        if self.is_animating:
            current_time = pygame.time.get_ticks() - self.start_time                          
            distance = -self.rect.width                                   
            self.rect.x = self.screen.get_size()[0] - self.rect.width + other.formulas.ease_out_expo(current_time, self.rect.width, distance, 750)                   
            
                                                
            if current_time >= 750:                                        
                self.is_animating = False                      
                
        if self.is_active:
            self.update_buttons()                           
            if not self.is_ghost_active:
                pygame.draw.rect(screen, self.color, self.rect)
                for container_index in range(len(self.get_filtered_defenses(self.tab_index))):
                    container_rect = self.get_container_rect(container_index)
                    pygame.draw.rect(screen, (15, 15, 15), container_rect, border_radius=12)
                for btn in self.tab_btns:
                    btn.draw(self.screen)
                if self.tab_btns:
                    self.focused_btn.current_color = other.colors.tabs_focus_color

                self.update_pin_button()

                focused_tab_index = self.tab_btns.index(self.focused_btn)
                self.tab_type = self.defense_types[focused_tab_index]          
                self.get_filtered_defenses(focused_tab_index)
                self.draw_content_for_tab(self.get_filtered_defenses(focused_tab_index))
                
                   
            if self.dragging_item:
                self.handle_dragging(self.dragging_item)

                                           
            self.economy_flash_inst.update()
            self.economy_flash_inst.draw()
            self.placement_flash_inst.update()
            self.placement_flash_inst.draw()

            print(self.placed_defenses)
            
def make_market(
        screen,
        screen_width,
        screen_height,
        margin=0,
        xpos=None,                                   
        ypos=0,
        width=helper.get_screen_size(False, True) / 8,
        height=helper.get_screen_size(True, False) / 6,
        text="Items...",
        color=None,                                           
        text_color=(255, 255, 255),
        defense_types=None,                                                      
        defense_list=None,                  
        num_rows = 5,
        num_cols = 2,
        vertical_offset = helper.get_screen_size(False, True) / 37,
        container_size = helper.get_screen_size(True, False) / 37,
        container_spacing=None,

    ):

    if xpos is None:
        xpos = screen_width - width                   

                                               
    if color is None:
        color = other.colors.market_color
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
        num_rows,
        num_cols,
        vertical_offset,
        container_size,
        container_spacing,
    ) 

def update_market(event_list, market_instance, button_instance):
    if button_instance.handle_event(event_list) and market_instance.btn_is_active:
        market_instance.toggle()                                            

                                                                    
        event_list = [e for e in event_list if e.type != pygame.MOUSEBUTTONDOWN]

    return event_list

