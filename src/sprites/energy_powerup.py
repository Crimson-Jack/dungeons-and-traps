from src.sprites.powerup import Powerup


class EnergyPowerup(Powerup):
    def __init__(self, image, position, groups, game_manager, powerup_volume):
        super().__init__(image, position, groups, game_manager)
        self.volume = powerup_volume

    def activate(self):
        self.game_manager.increase_player_energy(self.volume)
        super().kill()
