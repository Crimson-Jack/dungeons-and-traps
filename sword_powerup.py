from powerup import Powerup
from game_state import GameState


class SwordPowerup(Powerup):
    def __init__(self, image, position, groups, game_state):
        super().__init__(image, position, groups, game_state)

    def activate(self):
        self.game_state.collect_sword_powerup()
