import pygame
import settings
import direction
import weapon_type
from diamond import Diamond


class GameState:
    def __init__(self):
        self.game_over = False
        self.level = 0
        self.lives = 2
        self.score = 0

        self.weapon_type = weapon_type.WeaponType.NONE
        self.collected_weapons = [self.weapon_type]
        self.number_of_arrows = 0
        self.diamonds = list()
        self.collected_diamonds = list()
        self.keys = list()
        self.collected_keys = list()

        self.player_max_energy = 800
        self.player_energy = self.player_max_energy
        self.player_tile_position = (0, 0)
        self.player_movement_vector = pygame.Vector2()
        self.player_movement_direction = direction.Direction.RIGHT
        self.player_is_using_weapon = False

    def get_level(self):
        return settings.LEVELS[self.level]

    def check_is_last_level(self):
        return self.level == len(settings.LEVELS) - 1

    def set_next_level(self):
        self.level += 1
        self.diamonds.clear()
        self.collected_diamonds.clear()
        self.keys.clear()
        self.collected_keys.clear()
        self.reset_player_direction()

    def level_completed(self):
        if len(self.collected_diamonds) == len(self.diamonds):
            if self.check_is_last_level():
                # Note: Only for temporary solution
                self.game_over = True
                pygame.event.post(pygame.event.Event(settings.GAME_OVER_EVENT))
            else:
                pygame.event.post(pygame.event.Event(settings.NEXT_LEVEL_EVENT))

    def life_lost(self):
        self.lives -= 1
        if self.lives > 0:
            self.reset_player_direction()
            pygame.event.post(pygame.event.Event(settings.PLAYER_LOST_LIFE_EVENT))
        else:
            pygame.event.post(pygame.event.Event(settings.GAME_OVER_EVENT))

    def collect_sword_powerup(self):
        self.collected_weapons.append(weapon_type.WeaponType.SWORD)
        self.remove_none_weapon()
        if not (self.weapon_type == weapon_type.WeaponType.BOW and self.number_of_arrows > 0):
            self.weapon_type = weapon_type.WeaponType.SWORD
            pygame.event.post(pygame.event.Event(settings.CHANGE_WEAPON_EVENT))

    def collect_bow_powerup(self, number_of_arrows):
        self.number_of_arrows += number_of_arrows
        self.collected_weapons.append(weapon_type.WeaponType.BOW)
        self.remove_none_weapon()
        self.weapon_type = weapon_type.WeaponType.BOW
        pygame.event.post(pygame.event.Event(settings.CHANGE_WEAPON_EVENT))

    def remove_none_weapon(self):
        if weapon_type.WeaponType.NONE in self.collected_weapons:
            self.collected_weapons.remove(weapon_type.WeaponType.NONE)

    def set_next_weapon(self):
        self.weapon_type = self.weapon_type.next()
        while self.weapon_type not in self.collected_weapons:
            self.weapon_type = self.weapon_type.next()
        pygame.event.post(pygame.event.Event(settings.CHANGE_WEAPON_EVENT))

    def set_previous_weapon(self):
        self.weapon_type = self.weapon_type.previous()
        while self.weapon_type not in self.collected_weapons:
            self.weapon_type = self.weapon_type.previous()
        pygame.event.post(pygame.event.Event(settings.CHANGE_WEAPON_EVENT))

    def decrease_number_of_arrows(self):
        self.number_of_arrows -= 1
        pygame.event.post(pygame.event.Event(settings.DECREASE_NUMBER_OF_ARROWS_EVENT))
        if self.number_of_arrows == 0:
            self.set_next_weapon()

    def add_diamond(self, diamond):
        self.diamonds.append(diamond)

    def collect_diamond(self, diamond: Diamond):
        self.collected_diamonds.append(diamond)
        self.score += diamond.score
        pygame.event.post(pygame.event.Event(settings.COLLECT_DIAMOND_EVENT))
        if len(self.collected_diamonds) == len(self.diamonds):
            pygame.event.post(pygame.event.Event(settings.EXIT_POINT_IS_OPEN_EVENT))

    def add_key(self, key):
        self.keys.append(key)

    def collect_key(self, key):
        self.collected_keys.append(key)
        pygame.event.post(pygame.event.Event(settings.COLLECT_KEY_EVENT))

    def check_is_key_collected(self, key_name):
        count = sum(map(lambda item: item.key_name == key_name, self.collected_keys))
        return count

    def collect_life_powerup(self):
        self.lives += 1
        pygame.event.post(pygame.event.Event(settings.COLLECT_LIFE_EVENT))

    def decrease_player_energy(self, damage_power=1):
        if self.player_energy > 0:
            self.player_energy -= damage_power
            if self.player_energy <= 0:
                self.life_lost()
            else:
                pygame.event.post(pygame.event.Event(settings.CHANGE_ENERGY_EVENT))

    def increase_player_energy(self, volume, is_percentage=True):
        if is_percentage:
            self.player_energy += volume * self.player_max_energy / 100
        else:
            self.player_energy += volume
        if self.player_energy > self.player_max_energy:
            self.player_energy = self.player_max_energy
        pygame.event.post(pygame.event.Event(settings.CHANGE_ENERGY_EVENT))

    def set_player_max_energy(self):
        self.player_energy = self.player_max_energy

    def set_player_movement(self, x, y):
        # Set vector
        self.player_movement_vector.x += x
        self.player_movement_vector.y += y

        # Set direction
        if self.player_movement_vector.y == 0 and self.player_movement_vector.x > 0:
            self.player_movement_direction = direction.Direction.RIGHT
        elif self.player_movement_vector.y > 0 and self.player_movement_vector.x > 0:
            self.player_movement_direction = direction.Direction.RIGHT_DOWN
        elif self.player_movement_vector.y > 0 and self.player_movement_vector.x == 0:
            self.player_movement_direction = direction.Direction.DOWN
        elif self.player_movement_vector.y > 0 and self.player_movement_vector.x < 0:
            self.player_movement_direction = direction.Direction.LEFT_DOWN
        elif self.player_movement_vector.y == 0 and self.player_movement_vector.x < 0:
            self.player_movement_direction = direction.Direction.LEFT
        elif self.player_movement_vector.y < 0 and self.player_movement_vector.x < 0:
            self.player_movement_direction = direction.Direction.LEFT_UP
        elif self.player_movement_vector.y < 0 and self.player_movement_vector.x == 0:
            self.player_movement_direction = direction.Direction.UP
        elif self.player_movement_vector.y < 0 and self.player_movement_vector.x > 0:
            self.player_movement_direction = direction.Direction.RIGHT_UP

    def reset_player_direction(self):
        self.player_movement_direction = direction.Direction.RIGHT

    def set_player_is_using_weapon(self, status):
        self.player_is_using_weapon = status

    def set_player_tile_position(self, position):
        self.player_tile_position = position
