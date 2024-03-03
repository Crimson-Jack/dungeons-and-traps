from sword_powerup import SwordPowerup
from bow_powerup import BowPowerup


class PowerupFactory:
    def create(self, image, position, groups, game_state, powerup_name, powerup_volume):
        if powerup_name == 'sword':
            return SwordPowerup(image, position, groups, game_state)
        elif powerup_name == 'bow':
            return BowPowerup(image, position, groups, game_state, powerup_volume)
