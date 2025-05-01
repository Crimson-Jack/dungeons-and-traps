from src.sprites.powerup import Powerup


class LifePowerup(Powerup):
    def __init__(self, image, position, groups, game_manager):
        super().__init__(image, position, groups, game_manager)

    def collect(self):
        self.game_manager.collect_life_powerup()
        super().kill()
