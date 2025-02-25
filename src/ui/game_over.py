import pygame

def show_game_over(screen, width, height, clock):
    """
    Display a game over screen with a blurred background and a "Try Again" button.
    Clicking the button will restart the game.
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        # Create a blurred version of the current screen.
        blurred = pygame.transform.smoothscale(screen, (width // 10, height // 10))
        blurred = pygame.transform.smoothscale(blurred, (width, height))
        screen.blit(blurred, (0, 0))
        # Draw the GAME OVER text.
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 40))
        screen.blit(game_over_text, game_over_rect)
        # Draw the Try Again button.
        button_font = pygame.font.SysFont(None, 36)
        try_again_text = button_font.render("Try Again", True, (255, 255, 255))
        try_again_rect = try_again_text.get_rect(center=(width // 2, height // 2 + 40))
        button_background = try_again_rect.inflate(20, 10)
        pygame.draw.rect(screen, (50, 50, 50), button_background)
        pygame.draw.rect(screen, (255, 255, 255), button_background, 2)
        screen.blit(try_again_text, try_again_rect)
        # Check for click on the Try Again button.
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if button_background.collidepoint(mouse_pos):
                os.execl(sys.executable, sys.executable, *sys.argv)
        pygame.display.flip()
        clock.tick(60)