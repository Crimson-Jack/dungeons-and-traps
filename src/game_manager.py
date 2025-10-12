import pygame

from settings import Settings
from src.enums.direction import Direction
from src.enums.game_status import GameStatus
from src.enums.lighting_status import LightingStatus
from src.enums.weapon_type import WeaponType
from src.sprites.diamond import Diamond
from src.sprites.key import Key


class GameManager:
    def __init__(self):
        self.LEVELS = [
            # 'basic.tmx',
            # 'basic_arena.tmx',
            # 'basic_open_arena.tmx',
            # 's01_level_01.tmx',
            # 's01_level_02.tmx',
            # 's01_level_03.tmx',
            # 's01_level_04.tmx',
            # 's01_level_05.tmx',
            # 's01_level_06.tmx',
            # 's01_level_07.tmx',
            # 's01_level_08.tmx',
            's01_level_09.tmx',
        ]

        self.game_status = GameStatus.FIRST_PAGE
        self.lighting_status = LightingStatus.LIGHT_ON

        self.level = 0
        self.lives = 2
        self.score = 0

        self.weapon_type = WeaponType.NONE
        self.collected_weapons = [self.weapon_type]
        self.number_of_arrows = 0
        self.sword_max_energy = 100
        self.number_of_explosions = 0
        self.number_of_sword_thresholds = 5
        self.sword_energy = self.sword_max_energy

        self.diamonds = list()
        self.collected_diamonds = list()
        self.keys = list()
        self.collected_keys = list()

        self.player_max_energy = 800
        self.player_energy = self.player_max_energy
        self.player_tile_position = (0, 0)
        self.player_movement_vector = pygame.Vector2()
        self.player_movement_direction = Direction.RIGHT
        self.player_is_using_weapon = False

        self.check_point_position = None

    def clear_settings_for_first_level(self):
        self.lighting_status = LightingStatus.LIGHT_ON

        self.level = 0
        self.lives = 2
        self.score = 0

        self.weapon_type = WeaponType.NONE
        self.collected_weapons = [self.weapon_type]
        self.number_of_arrows = 0
        self.sword_energy = self.sword_max_energy

        self.diamonds.clear()
        self.collected_diamonds.clear()
        self.keys.clear()
        self.collected_keys.clear()

        self.set_player_max_energy()
        self.reset_player_direction()

        self.check_point_position = None

    def clear_settings_for_next_level(self):
        self.level += 1

        self.diamonds.clear()
        self.collected_diamonds.clear()
        self.keys.clear()
        self.collected_keys.clear()

        self.reset_player_direction()

        self.check_point_position = None

    def clear_settings_for_current_level(self):
        self.lighting_status = LightingStatus.LIGHT_ON

        self.diamonds.clear()
        self.collected_diamonds.clear()
        self.keys.clear()
        self.collected_keys.clear()

        self.set_player_max_energy()
        self.reset_player_direction()

        self.check_point_position = None

    def set_first_page(self):
        self.game_status = GameStatus.FIRST_PAGE

    def set_next_level(self):
        self.game_status = GameStatus.NEXT_LEVEL

    def set_game_is_running(self):
        self.game_status = GameStatus.GAME_IS_RUNNING

    def set_level_completed(self):
        self.game_status = GameStatus.LEVEL_COMPLETED

    def set_game_over(self):
        self.game_status = GameStatus.GAME_OVER

    def switch_pause_state(self):
        if self.game_status == GameStatus.GAME_IS_PAUSED:
            self.game_status = GameStatus.GAME_IS_RUNNING
        else:
            self.game_status = GameStatus.GAME_IS_PAUSED

    def switch_escape_state(self):
        if self.game_status == GameStatus.OPTIONS:
            self.game_status = GameStatus.GAME_IS_RUNNING
        else:
            self.game_status = GameStatus.OPTIONS

    def get_level_filename(self):
        return self.LEVELS[self.level]

    def check_is_last_level(self):
        return self.level == len(self.LEVELS) - 1

    def load_next_level(self):
        if len(self.collected_diamonds) == len(self.diamonds):
            if self.check_is_last_level():
                self.game_status = GameStatus.GAME_OVER
                pygame.event.post(pygame.event.Event(Settings.GAME_OVER_EVENT))
            else:
                pygame.event.post(pygame.event.Event(Settings.NEXT_LEVEL_EVENT))

    def life_lost(self):
        self.lives -= 1
        if self.lives > 0:
            self.set_player_max_energy()
            self.reset_player_direction()
            pygame.event.post(pygame.event.Event(Settings.PLAYER_LOST_LIFE_EVENT))
        else:
            pygame.event.post(pygame.event.Event(Settings.GAME_OVER_EVENT))

    def decrease_number_of_lives(self):
        self.lives -= 1

    def increase_score(self, value):
        self.score += value
        pygame.event.post(pygame.event.Event(Settings.CHANGE_SCORE_EVENT))

    def collect_sword_powerup(self):
        self.add_weapon(WeaponType.SWORD)
        self.sword_energy = self.sword_max_energy
        self.remove_weapon(WeaponType.NONE)
        self.weapon_type = WeaponType.SWORD
        pygame.event.post(pygame.event.Event(Settings.CHANGE_WEAPON_EVENT))

    def collect_bow_powerup(self, number_of_arrows):
        self.add_weapon(WeaponType.BOW)
        self.number_of_arrows += number_of_arrows
        self.remove_weapon(WeaponType.NONE)
        self.weapon_type = WeaponType.BOW
        pygame.event.post(pygame.event.Event(Settings.CHANGE_WEAPON_EVENT))

    def collect_explosion_powerup(self, number_of_explosions):
        self.add_weapon(WeaponType.EXPLOSION)
        self.number_of_explosions += number_of_explosions
        self.remove_weapon(WeaponType.NONE)
        self.weapon_type = WeaponType.EXPLOSION
        pygame.event.post(pygame.event.Event(Settings.CHANGE_WEAPON_EVENT))

    def add_weapon(self, weapon):
        if weapon not in self.collected_weapons:
            self.collected_weapons.append(weapon)

    def remove_weapon(self, weapon):
        if weapon in self.collected_weapons:
            self.collected_weapons.remove(weapon)

    def set_next_weapon(self):
        self.weapon_type = self.weapon_type.next()
        while self.weapon_type not in self.collected_weapons:
            self.weapon_type = self.weapon_type.next()
        pygame.event.post(pygame.event.Event(Settings.CHANGE_WEAPON_EVENT))

    def set_previous_weapon(self):
        self.weapon_type = self.weapon_type.previous()
        while self.weapon_type not in self.collected_weapons:
            self.weapon_type = self.weapon_type.previous()
        pygame.event.post(pygame.event.Event(Settings.CHANGE_WEAPON_EVENT))

    def decrease_sword_energy(self):
        if self.sword_energy > 0:
            self.sword_energy -= 1

        if self.sword_energy <= 0:
            self.remove_weapon(WeaponType.SWORD)
            if len(self.collected_weapons) == 0:
                self.add_weapon(WeaponType.NONE)
            self.set_next_weapon()
        else:
            pygame.event.post(pygame.event.Event(Settings.CHANGE_WEAPON_CAPACITY_EVENT))

    def get_sword_capacity(self):
        threshold = self.sword_max_energy // self.number_of_sword_thresholds
        capacity = self.number_of_sword_thresholds - (self.sword_energy // threshold) - 1
        if capacity < 0:
            capacity = 0
        return capacity

    def decrease_number_of_arrows(self):
        if self.number_of_arrows > 0:
            self.number_of_arrows -= 1

        if self.number_of_arrows <= 0:
            self.remove_weapon(WeaponType.BOW)
            if len(self.collected_weapons) == 0:
                self.add_weapon(WeaponType.NONE)
            self.set_next_weapon()
        else:
            pygame.event.post(pygame.event.Event(Settings.CHANGE_WEAPON_CAPACITY_EVENT))

    def decrease_number_of_explosions(self):
        if self.number_of_explosions > 0:
            self.number_of_explosions -= 1

        if self.number_of_explosions <= 0:
            self.remove_weapon(WeaponType.EXPLOSION)
            if len(self.collected_weapons) == 0:
                self.add_weapon(WeaponType.NONE)
            self.set_next_weapon()
        else:
            pygame.event.post(pygame.event.Event(Settings.CHANGE_WEAPON_CAPACITY_EVENT))

    def add_diamond(self, diamond: Diamond):
        self.diamonds.append(diamond)

    def collect_diamond(self, diamond: Diamond):
        self.collected_diamonds.append(diamond)
        self.score += diamond.score
        pygame.event.post(pygame.event.Event(Settings.COLLECT_DIAMOND_EVENT))
        if len(self.collected_diamonds) == len(self.diamonds):
            pygame.event.post(pygame.event.Event(Settings.EXIT_POINT_IS_OPEN_EVENT))

    def add_key(self, key: Key):
        self.keys.append(key)

    def collect_key(self, key: Key):
        self.collected_keys.append(key)
        self.score += key.score
        pygame.event.post(pygame.event.Event(Settings.COLLECT_KEY_EVENT))

    def check_is_key_collected(self, key_name):
        count = sum(map(lambda item: item.key_name == key_name, self.collected_keys))
        return count

    def collect_life_powerup(self):
        self.lives += 1
        pygame.event.post(pygame.event.Event(Settings.COLLECT_LIFE_EVENT))

    def decrease_player_energy(self, damage_power=1):
        if self.player_energy > 0:
            self.player_energy -= damage_power
            if self.player_energy <= 0:
                self.life_lost()
            else:
                pygame.event.post(pygame.event.Event(Settings.CHANGE_ENERGY_EVENT))

    def increase_player_energy(self, volume, is_percentage=True):
        if is_percentage:
            self.player_energy += volume * self.player_max_energy / 100
        else:
            self.player_energy += volume
        if self.player_energy > self.player_max_energy:
            self.player_energy = self.player_max_energy
        pygame.event.post(pygame.event.Event(Settings.CHANGE_ENERGY_EVENT))

    def set_player_max_energy(self):
        self.player_energy = self.player_max_energy

    def set_player_movement(self, x, y):
        # Set vector
        self.player_movement_vector.x += x
        self.player_movement_vector.y += y

        # Set direction
        if self.player_movement_vector.y == 0 and self.player_movement_vector.x > 0:
            self.player_movement_direction = Direction.RIGHT
        elif self.player_movement_vector.y > 0 and self.player_movement_vector.x > 0:
            self.player_movement_direction = Direction.RIGHT_DOWN
        elif self.player_movement_vector.y > 0 and self.player_movement_vector.x == 0:
            self.player_movement_direction = Direction.DOWN
        elif self.player_movement_vector.y > 0 and self.player_movement_vector.x < 0:
            self.player_movement_direction = Direction.LEFT_DOWN
        elif self.player_movement_vector.y == 0 and self.player_movement_vector.x < 0:
            self.player_movement_direction = Direction.LEFT
        elif self.player_movement_vector.y < 0 and self.player_movement_vector.x < 0:
            self.player_movement_direction = Direction.LEFT_UP
        elif self.player_movement_vector.y < 0 and self.player_movement_vector.x == 0:
            self.player_movement_direction = Direction.UP
        elif self.player_movement_vector.y < 0 and self.player_movement_vector.x > 0:
            self.player_movement_direction = Direction.RIGHT_UP

    def reset_player_direction(self):
        self.player_movement_direction = Direction.RIGHT

    def set_player_is_using_weapon(self, status):
        self.player_is_using_weapon = status

    def set_player_tile_position(self, position):
        self.player_tile_position = position

    def collect_check_point(self, position):
        self.check_point_position = position

    def get_check_point_position(self):
        return self.check_point_position

    def set_lighting_spell(self, lighting_status: LightingStatus):
        self.lighting_status = lighting_status
