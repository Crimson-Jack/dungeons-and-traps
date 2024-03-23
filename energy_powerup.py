from powerup import Powerup


class EnergyPowerup(Powerup):
    def __init__(self, image, position, groups, game_state, powerup_volume):
        super().__init__(image, position, groups, game_state)
        self.volume = powerup_volume

    def activate(self):
        self.game_state.increase_energy(self.volume)
