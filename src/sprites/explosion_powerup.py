from src.sprites.powerup import Powerup


class ExplosionPowerup(Powerup):
    def __init__(self, image, position, groups, game_manager, powerup_volume):
        super().__init__(image, position, groups, game_manager)
        self.number_of_explosions = powerup_volume

    def activate(self):
        self.game_manager.collect_explosion_powerup(self.number_of_explosions)
        super().kill()