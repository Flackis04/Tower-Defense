import enemies.enemies as enemies

class Black(enemies.Enemy):
    def __init__(self, screen, path_points, tier=6, color=enemies.Enemy.tier_to_color[6], radius=15, speed=75, reward=10):
        super().__init__(screen, path_points, tier=tier, color=color, radius=radius, speed=speed, reward=reward)
        
                                                                  
        self.ability = "Stealth"                                      
