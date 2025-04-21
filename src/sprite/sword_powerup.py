from src.sprite.powerup import Powerup


class SwordPowerup(Powerup):
    def __init__(self, image, position, groups, game_state):
        super().__init__(image, position, groups, game_state)

    def collect(self):
        self.game_state.collect_sword_powerup()
        super().kill()
