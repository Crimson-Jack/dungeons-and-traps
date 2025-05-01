from src.sprites.powerup import Powerup


class BowPowerup(Powerup):
    def __init__(self, image, position, groups, game_manager, powerup_volume):
        super().__init__(image, position, groups, game_manager)
        self.number_of_arrows = powerup_volume

    def collect(self):
        self.game_manager.collect_bow_powerup(self.number_of_arrows)
        super().kill()
