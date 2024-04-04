from sword_powerup import SwordPowerup
from bow_powerup import BowPowerup
from energy_powerup import EnergyPowerup
from life_powerup import LifePowerup


class PowerupFactory:
    def create(self, powerup_name, **kwargs):
        image = kwargs["image"]
        position = kwargs["position"]
        groups = kwargs["groups"]
        game_state = kwargs["game_state"]
        powerup_volume = kwargs["powerup_volume"]

        if powerup_name == 'sword':
            return SwordPowerup(image, position, groups, game_state)
        elif powerup_name == 'bow':
            return BowPowerup(image, position, groups, game_state, powerup_volume)
        elif powerup_name == 'energy':
            return EnergyPowerup(image, position, groups, game_state, powerup_volume)
        elif powerup_name == 'life':
            return LifePowerup(image, position, groups, game_state)
