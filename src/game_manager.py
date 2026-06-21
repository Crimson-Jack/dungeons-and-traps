import pygame


from src.events import Events
from src.enemy_kill_record import EnemyKillRecord
from src.enums.direction import Direction
from src.enums.enemy_type import EnemyType
from src.enums.game_status import GameStatus
from src.bonus_record import BonusRecord
from src.collectable_record import CollectableRecord
from src.level_stats import LevelStats
from src.enums.sound_effect import SoundEffect
from src.level_details import LevelDetails
from src.enums.lighting_status import LightingStatus
from src.enums.weapon_type import WeaponType
from src.sound_manager import SoundManager
from src.sprites.diamond import Diamond
from src.sprites.key import Key


class GameManager:
    def __init__(self):
        self.LEVELS = [
            LevelDetails(
                's01_level_01.tmx',
                'c1',
                "Top of the Tower",
                "The catapult hurled you to the very top of the Count's cursed tower. Collect keys and open doors. Gather diamonds to reveal the secret passage below."),
            LevelDetails(
                's01_level_02.tmx',
                'c2',
                "Chamber of Spirits",
                "Spirits have claimed these chambers — they cannot be slain, so run. Find the sword and cut down Bluemantles and Lurkers. Drink a potion to restore your strength."),
            LevelDetails(
                's01_level_03.tmx',
                'c3',
                "Floor of Stone Secrets",
                "Boulders can be pushed to block the passages. Reach for the bow when enemies are in range. Descend from the tower into the courtyard."),
            LevelDetails(
                's01_level_04.tmx',
                'c4',
                "The Forsaken Courtyard",
                "The Count's manor stands empty and forsaken. Cross the abandoned courtyard and pass the graveyard. Hellfire devours all living things — stay away."),
            LevelDetails(
                's01_level_05.tmx',
                'c5',
                "Cellars of Nightmares",
                "Duskwings and bloodthirsty Webmasters lurk in every shadow. Bloodclaws are lightning-fast and hear your every step. The green spirits haunting this level are terrifyingly fast."),
            LevelDetails(
                's01_level_06.tmx',
                'c6',
                "The Portal Labyrinth",
                "The Count's dark magic raises monsters and tears open portals of teleportation. Traverse the chambers and collect diamonds guarded by spirits and goblins. Step through the portals to reach chambers otherwise inaccessible."),
            LevelDetails(
                's01_level_07.tmx',
                'c7',
                "Dungeons of Eternal Night",
                "Thick darkness engulfs the dungeons — your lantern is your only hope. Webmasters lurk around every corner. Not all walls are what they seem."),
            LevelDetails(
                's01_level_08.tmx',
                'c8',
                "The Antechamber of Hell",
                "You'll find the magic of Explosion — it destroys monsters even through walls. Hidden alcoves are scattered throughout — explore every corner. Hordes of frenzied Duskwings stand guard at every portal."),
            LevelDetails(
                's01_level_09.tmx',
                'c9',
                "The Count's Infernal Keep",
                "Collect all diamonds — the walls will crack. Claim the weapons and face the fire-breathing octopus. Beware its goblin spawn — each fireball hatches a new foe.",
                False,
                True),

            # Tests
            LevelDetails('basic.tmx', 'a1'),
            LevelDetails('basic_arena.tmx', 'a2', exit_point_enabled=False),
            LevelDetails('basic_open_arena.tmx', 'a3'),
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

        self.is_boss_visible = False
        self.boss_max_energy = 0
        self.boss_energy = self.boss_max_energy

        self.check_point_position = None

        # Level stats — one entry per level, persists until game over
        self.level_stats: list[LevelStats] = [LevelStats()]

        # Sound
        self.sound_manager = SoundManager()

    def clear_settings_for_first_level(self, level_number:int = 0):
        self.lighting_status = LightingStatus.LIGHT_ON

        self.level = level_number
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

        self.is_boss_visible = False

        self.check_point_position = None

        self.level_stats = [LevelStats()]

    def clear_settings_for_next_level(self):
        self.level += 1

        self.diamonds.clear()
        self.collected_diamonds.clear()
        self.keys.clear()
        self.collected_keys.clear()

        self.reset_player_direction()

        self.is_boss_visible = False

        self.check_point_position = None

        self.level_stats.append(LevelStats())

    def clear_settings_for_current_level(self):
        self.lighting_status = LightingStatus.LIGHT_ON

        self.diamonds.clear()
        self.collected_diamonds.clear()
        self.keys.clear()
        self.collected_keys.clear()

        self.set_player_max_energy()
        self.reset_player_direction()

        self.is_boss_visible = False

        self.check_point_position = None

        self.level_stats[-1].reset()

    def set_studio_page(self):
        self.game_status = GameStatus.STUDIO_PAGE

    def set_first_page(self):
        self.game_status = GameStatus.FIRST_PAGE

    def set_secret_code(self):
        self.game_status = GameStatus.SECRET_CODE

    def set_secret_code_is_valid(self):
        self.game_status = GameStatus.SECRET_CODE_IS_VALID

    def set_next_level(self):
        self.game_status = GameStatus.NEXT_LEVEL

    def set_game_is_running(self):
        self.game_status = GameStatus.GAME_IS_RUNNING

    def set_level_completed(self):
        self.game_status = GameStatus.LEVEL_COMPLETED

    def set_game_over(self):
        self.game_status = GameStatus.GAME_OVER

    def set_you_win(self):
        self.game_status = GameStatus.YOU_WIN

    def set_summary(self):
        self.game_status = GameStatus.SUMMARY

    def get_aggregate_collectable_stats(self) -> tuple[CollectableRecord, CollectableRecord, BonusRecord]:
        diamond_totals = CollectableRecord()
        key_totals = CollectableRecord()
        bonus_totals = BonusRecord()
        for stats in self.level_stats:
            diamond_record = stats.get_diamond_record()
            diamond_totals.count += diamond_record.count
            diamond_totals.collected += diamond_record.collected
            diamond_totals.score += diamond_record.score
            key_record = stats.get_key_record()
            key_totals.count += key_record.count
            key_totals.collected += key_record.collected
            key_totals.score += key_record.score
            bonus_record = stats.get_bonus_record()
            bonus_totals.awarded += bonus_record.awarded
            bonus_totals.score += bonus_record.score
        return diamond_totals, key_totals, bonus_totals

    def get_aggregate_kill_stats(self) -> dict:
        totals = {enemy_type: EnemyKillRecord() for enemy_type in EnemyType}
        for stats in self.level_stats:
            for enemy_type in EnemyType:
                level_record = stats.get_enemy_record(enemy_type)
                totals[enemy_type].count += level_record.count
                totals[enemy_type].killed += level_record.killed
                totals[enemy_type].score += level_record.score
        return totals

    def switch_pause_state(self):
        if self.game_status == GameStatus.GAME_IS_PAUSED:
            self.game_status = GameStatus.GAME_IS_RUNNING
        else:
            self.game_status = GameStatus.GAME_IS_PAUSED

    def get_level_filename(self):
        return self.LEVELS[self.level].source_file

    def load_next_level(self):
        if self.LEVELS[self.level].is_final_level or self.level == len(self.LEVELS) - 1:
            pygame.event.post(pygame.event.Event(Events.YOU_WIN_EVENT))
        else:
            pygame.event.post(pygame.event.Event(Events.NEXT_LEVEL_EVENT))

    def life_lost(self):
        self.lives -= 1
        if self.lives > 0:
            self.set_player_max_energy()
            self.reset_player_direction()
            pygame.event.post(pygame.event.Event(Events.PLAYER_LOST_LIFE_EVENT))
        else:
            pygame.event.post(pygame.event.Event(Events.GAME_OVER_EVENT))

    def decrease_number_of_lives(self):
        self.lives -= 1

    def increase_score(self, value):
        self.score += value
        pygame.event.post(pygame.event.Event(Events.CHANGE_SCORE_EVENT))

    def collect_sword_powerup(self):
        self.add_weapon(WeaponType.SWORD)
        self.sword_energy = self.sword_max_energy
        self.remove_weapon(WeaponType.NONE)
        self.weapon_type = WeaponType.SWORD
        pygame.event.post(pygame.event.Event(Events.CHANGE_WEAPON_EVENT))

    def collect_bow_powerup(self, number_of_arrows):
        self.add_weapon(WeaponType.BOW)
        self.number_of_arrows += number_of_arrows
        self.remove_weapon(WeaponType.NONE)
        self.weapon_type = WeaponType.BOW
        pygame.event.post(pygame.event.Event(Events.CHANGE_WEAPON_EVENT))

    def collect_explosion_powerup(self, number_of_explosions):
        self.add_weapon(WeaponType.EXPLOSION)
        self.number_of_explosions += number_of_explosions
        self.remove_weapon(WeaponType.NONE)
        self.weapon_type = WeaponType.EXPLOSION
        pygame.event.post(pygame.event.Event(Events.CHANGE_WEAPON_EVENT))

    def add_weapon(self, weapon):
        if weapon not in self.collected_weapons:
            self.collected_weapons.append(weapon)

    def remove_weapon(self, weapon):
        if weapon in self.collected_weapons:
            self.collected_weapons.remove(weapon)

    def set_next_weapon(self):
        current_weapon_type = self.weapon_type
        self.weapon_type = self.weapon_type.next()
        while self.weapon_type not in self.collected_weapons:
            self.weapon_type = self.weapon_type.next()
        if current_weapon_type != self.weapon_type:
            self.sound_manager.play_sfx(SoundEffect.CHANGE_WEAPON)
            pygame.event.post(pygame.event.Event(Events.CHANGE_WEAPON_EVENT))

    def set_previous_weapon(self):
        current_weapon_type = self.weapon_type
        self.weapon_type = self.weapon_type.previous()
        while self.weapon_type not in self.collected_weapons:
            self.weapon_type = self.weapon_type.previous()
        if current_weapon_type != self.weapon_type:
            self.sound_manager.play_sfx(SoundEffect.CHANGE_WEAPON)
            pygame.event.post(pygame.event.Event(Events.CHANGE_WEAPON_EVENT))

    def decrease_sword_energy(self):
        if self.sword_energy > 0:
            self.sword_energy -= 1

        if self.sword_energy <= 0:
            self.remove_weapon(WeaponType.SWORD)
            if len(self.collected_weapons) == 0:
                self.add_weapon(WeaponType.NONE)
            self.set_next_weapon()
        else:
            pygame.event.post(pygame.event.Event(Events.CHANGE_WEAPON_CAPACITY_EVENT))

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
            pygame.event.post(pygame.event.Event(Events.CHANGE_WEAPON_CAPACITY_EVENT))

    def decrease_number_of_explosions(self):
        if self.number_of_explosions > 0:
            self.number_of_explosions -= 1

        if self.number_of_explosions <= 0:
            self.remove_weapon(WeaponType.EXPLOSION)
            if len(self.collected_weapons) == 0:
                self.add_weapon(WeaponType.NONE)
            self.set_next_weapon()
        else:
            pygame.event.post(pygame.event.Event(Events.CHANGE_WEAPON_CAPACITY_EVENT))

    def add_diamond(self, diamond: Diamond):
        self.diamonds.append(diamond)
        self.level_stats[-1].record_diamond_placed()

    def collect_diamond(self, diamond: Diamond):
        self.collected_diamonds.append(diamond)
        self.score += diamond.score
        self.level_stats[-1].record_diamond_collected(diamond.score)
        pygame.event.post(pygame.event.Event(Events.COLLECT_DIAMOND_EVENT))
        if len(self.collected_diamonds) == len(self.diamonds):
            if self.LEVELS[self.level].exit_point_enabled:
                pygame.event.post(pygame.event.Event(Events.EXIT_POINT_IS_OPEN_EVENT))
            else:
                pygame.event.post(pygame.event.Event(Events.REMOVE_OBSTACLES_EVENT))
                pygame.event.post(pygame.event.Event(Events.CREATE_BOSS_OCTOPUS_EVENT))

    def add_key(self, key: Key):
        self.keys.append(key)
        self.level_stats[-1].record_key_placed()

    def collect_key(self, key: Key):
        self.collected_keys.append(key)
        self.score += key.score
        self.level_stats[-1].record_key_collected(key.score)
        pygame.event.post(pygame.event.Event(Events.COLLECT_KEY_EVENT))

    def award_completion_bonus(self, score: int):
        self.increase_score(score)
        self.level_stats[-1].record_bonus_awarded(score)

    def check_is_key_collected(self, key_name):
        count = sum(map(lambda item: item.key_name == key_name, self.collected_keys))
        return count

    def collect_life_powerup(self):
        self.lives += 1
        pygame.event.post(pygame.event.Event(Events.COLLECT_LIFE_EVENT))

    def decrease_player_energy(self, damage_power=1):
        if self.player_energy > 0:
            self.player_energy -= damage_power
            if self.player_energy <= 0:
                self.life_lost()
            else:
                pygame.event.post(pygame.event.Event(Events.CHANGE_ENERGY_EVENT))

    def increase_player_energy(self, volume, is_percentage=True):
        if is_percentage:
            self.player_energy += volume * self.player_max_energy / 100
        else:
            self.player_energy += volume
        if self.player_energy > self.player_max_energy:
            self.player_energy = self.player_max_energy
        pygame.event.post(pygame.event.Event(Events.CHANGE_ENERGY_EVENT))

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

    def reset_player_movement(self):
        self.player_movement_vector.x = 0
        self.player_movement_vector.y = 0

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

    def validate_secret_code(self, code):
        for item in self.LEVELS:
            if item.secret_code is not None and item.secret_code == code:
                return self.LEVELS.index(item)

        return None

    def get_secret_code(self):
        return self.LEVELS[self.level].secret_code

    def get_level_name(self):
        return self.LEVELS[self.level].name

    def get_level_description(self):
        return self.LEVELS[self.level].description
