from powerup import Powerup


class BowPowerup(Powerup):
    def __init__(self, image, position, groups, game_state, powerup_volume):
        super().__init__(image, position, groups, game_state)
        self.number_of_arrows = powerup_volume

    def activate(self):
        self.game_state.collect_bow_powerup(self.number_of_arrows)
