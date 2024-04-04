from powerup import Powerup


class LifePowerup(Powerup):
    def __init__(self, image, position, groups, game_state):
        super().__init__(image, position, groups, game_state)

    def activate(self):
        self.game_state.collect_life_powerup()
