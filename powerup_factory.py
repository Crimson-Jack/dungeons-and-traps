from powerup_tile_details import PowerupTileDetails
from sword_powerup import SwordPowerup
from bow_powerup import BowPowerup
from energy_powerup import EnergyPowerup
from life_powerup import LifePowerup


class PowerupFactory:
    def create(self, tile_details: PowerupTileDetails, **kwargs):
        image = kwargs["image"]
        position = kwargs["position"]
        groups = kwargs["groups"]
        game_state = kwargs["game_state"]

        if tile_details.powerup_name == 'sword':
            return SwordPowerup(image, position, groups, game_state)
        elif tile_details.powerup_name == 'bow':
            return BowPowerup(image, position, groups, game_state, tile_details.powerup_volume)
        elif tile_details.powerup_name == 'energy':
            return EnergyPowerup(image, position, groups, game_state, tile_details.powerup_volume)
        elif tile_details.powerup_name == 'life':
            return LifePowerup(image, position, groups, game_state)
