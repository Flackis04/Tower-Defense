import pygame

class Economy_flash:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.is_active = False
        self.start_time = 0
        self.duration = 750

    def trigger(self):
        self.is_active = True
        self.start_time = pygame.time.get_ticks()

    def stop(self):
        self.is_active = False
        self.alpha = 0

    def update(self):
        if self.is_active:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.start_time

                                                              
            if elapsed_time >= self.duration:
                self.is_active = False

    def draw(self):
        if self.is_active:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time

            if elapsed < self.duration:
                alpha = 30 * (self.duration - elapsed) / self.duration
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)                                 
                overlay.fill((255, 0, 0))                 
                overlay.set_alpha(int(alpha))                       
                self.screen.blit(overlay, (0, 0))                    
            else:
                self.is_active = False

class placement_flash:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.is_active = False
        self.start_time = 0
        self.fade_duration = 250                            
        self.alpha = 0
        self.is_dragging = False

    def trigger(self):
        if not self.is_active:
            self.is_active = True
            self.start_time = pygame.time.get_ticks()
            self.alpha = 0
            self.is_dragging = True

    def stop(self):
        self.is_active = False
        self.is_dragging = False
        self.alpha = 0

    def update(self):
        if self.is_active:
            current_time = pygame.time.get_ticks()
            
            if self.is_dragging:
                                                                 
                self.fadeout_start_time = None
                elapsed_time = current_time - self.start_time
                if elapsed_time < self.fade_duration:
                    self.alpha = int(60 * (elapsed_time / self.fade_duration))
                else:
                    self.alpha = 60
            else:
                self.stop()

    def draw(self):
        if self.is_active and self.is_dragging:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((255, 0, 0))                 
            overlay.set_alpha(self.alpha)
            self.screen.blit(overlay, (0, 0))