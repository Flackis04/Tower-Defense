import pygame

class InsufficientFundsFlash:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.is_active = False
        self.start_time = 0
        self.duration = 750

    def trigger(self):
        self.is_active = True
        self.start_time = pygame.time.get_ticks()
        print("Triggering, is_active:", self.is_active)

    def stop(self):
        self.is_active = False
        self.alpha = 0

    def update(self):
        if self.is_active:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.start_time

            # If the duration has passed, deactivate the flash
            if elapsed_time >= self.duration:
                self.is_active = False
                print("Deactivating, is_active:", self.is_active)

    def draw(self):
        if self.is_active:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time

            if elapsed < self.duration:
                alpha = 30 * (self.duration - elapsed) / self.duration
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Use SRCALPHA for transparency
                overlay.fill((255, 0, 0))  # Fill with red
                overlay.set_alpha(int(alpha))  # Set the alpha value
                self.screen.blit(overlay, (0, 0))  # Draw the overlay
            else:
                self.is_active = False
# Create a single instance of InsufficientFundsFlash
flash_instance = None

def initialize_flash(screen):
    global flash_instance
    flash_instance = InsufficientFundsFlash(screen)

def get_flash_instance():
    global flash_instance
    if flash_instance is None:
        raise ValueError("Flash instance not initialized. Call initialize_flash() first.")
    return flash_instance

class InvalidPlacementFlash:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.is_active = False
        self.start_time = 0
        self.fade_duration = 250  # Time to fade to alpha=80
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
            elapsed_time = current_time - self.start_time

            if elapsed_time < self.fade_duration:
                self.alpha = int(60 * (elapsed_time / self.fade_duration))
            else:
                self.alpha = 60
            if self.is_active and not self.is_dragging:
                self.alpha = int(60 * (self.fade_duration / self.elapsed_time))  # Stop the flash if the item is placed down

    def draw(self):
        if self.is_active and self.is_dragging:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((255, 0, 0))  # Fill with red
            overlay.set_alpha(self.alpha)
            self.screen.blit(overlay, (0, 0))

invalid_placement_flash_instance = None

def initialize_invalid_placement_flash(screen):
    global invalid_placement_flash_instance
    invalid_placement_flash_instance = InvalidPlacementFlash(screen)

def get_invalid_placement_flash_instance():
    global invalid_placement_flash_instance
    if invalid_placement_flash_instance is None:
        raise ValueError("InvalidPlacementFlash instance not initialized. Call initialize_invalid_placement_flash() first.")
    return invalid_placement_flash_instance