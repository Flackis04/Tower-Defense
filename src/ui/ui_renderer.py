def draw_ui(screen, event_list, market_instance, market_btn, balance_display, hp_font, player_hp):
    """
    Draw UI elements including defenses, market, balance display, and HP.
    """
    market_instance.draw_defenses(event_list)
    if market_instance.is_active:
        market_instance.draw(screen)
    if market_instance.btn_is_active:
        market_btn.draw(screen)
    balance_display.update()
    balance_display.draw()
    hp_text = hp_font.render(f"HP: {player_hp}", True, (255, 255, 255))
    screen.blit(hp_text, (10, 50))