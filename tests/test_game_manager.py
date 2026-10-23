from unittest.mock import Mock

import pytest

import src.game_manager
from src import level_catalog
from src.enums.direction import Direction
from src.enums.enemy_type import EnemyType
from src.game_manager import GameManager
from src.level_stats import LevelStats


# SoundManager loads sound files through pygame.mixer, which is irrelevant for the game state
@pytest.fixture
def game_manager(monkeypatch):
    monkeypatch.setattr(src.game_manager, 'SoundManager', Mock())
    return GameManager()


def create_key(key_name):
    return Mock(key_name=key_name)


class TestLevels:
    def test_uses_level_catalog(self, game_manager):
        assert game_manager.LEVELS is level_catalog.LEVELS


class TestCurrentLevelDetails:
    def test_returns_first_level_at_start(self, game_manager):
        assert game_manager.current_level_details is level_catalog.LEVELS[0]

    def test_returns_last_level_for_last_index(self, game_manager):
        game_manager.level = len(level_catalog.LEVELS) - 1

        assert game_manager.current_level_details is level_catalog.LEVELS[-1]

    def test_follows_level_change(self, game_manager):
        game_manager.level = 2

        assert game_manager.current_level_details is level_catalog.LEVELS[2]


class TestNumberOfUsedSwordThresholds:
    @pytest.mark.parametrize('sword_energy, expected_number_of_used_thresholds', [
        (100, 0),
        (81, 0),
        (80, 1),
        (61, 1),
        (60, 2),
        (40, 3),
        (21, 3),
        (20, 4),
        (1, 4),
    ])
    def test_returns_used_thresholds_for_sword_energy(self, game_manager, sword_energy, expected_number_of_used_thresholds):
        game_manager.sword_energy = sword_energy

        assert game_manager.number_of_used_sword_thresholds == expected_number_of_used_thresholds


class TestClearSettingsForFirstLevel:
    def test_resets_number_of_explosions(self, game_manager):
        game_manager.number_of_explosions = 3

        game_manager.clear_settings_for_first_level()

        assert game_manager.number_of_explosions == 0


class TestIsKeyCollected:
    def test_returns_false_when_no_key_is_collected(self, game_manager):
        assert game_manager.is_key_collected('red') is False

    def test_returns_true_when_key_with_given_name_is_collected(self, game_manager):
        game_manager.collected_keys = [create_key('blue'), create_key('red')]

        assert game_manager.is_key_collected('red') is True

    def test_returns_false_when_only_keys_with_other_names_are_collected(self, game_manager):
        game_manager.collected_keys = [create_key('blue'), create_key('green')]

        assert game_manager.is_key_collected('red') is False


class TestSetPlayerMovement:
    @pytest.mark.parametrize('delta_x, delta_y, expected_direction', [
        (1, 0, Direction.RIGHT),
        (1, 1, Direction.RIGHT_DOWN),
        (0, 1, Direction.DOWN),
        (-1, 1, Direction.LEFT_DOWN),
        (-1, 0, Direction.LEFT),
        (-1, -1, Direction.LEFT_UP),
        (0, -1, Direction.UP),
        (1, -1, Direction.RIGHT_UP),
    ])
    def test_sets_direction_matching_movement(self, game_manager, delta_x, delta_y, expected_direction):
        game_manager.set_player_movement(delta_x, delta_y)

        assert game_manager.player_movement_direction == expected_direction

    def test_zero_movement_keeps_previous_direction(self, game_manager):
        game_manager.player_movement_direction = Direction.LEFT_UP

        game_manager.set_player_movement(0, 0)

        assert game_manager.player_movement_direction == Direction.LEFT_UP

    def test_released_key_stops_player_and_keeps_direction(self, game_manager):
        game_manager.set_player_movement(0, 1)
        game_manager.set_player_movement(0, -1)

        assert game_manager.player_movement_vector == (0, 0)
        assert game_manager.player_movement_direction == Direction.DOWN

    def test_component_greater_than_one_keeps_direction(self, game_manager):
        game_manager.set_player_movement(0, 1)
        game_manager.set_player_movement(0, 1)

        assert game_manager.player_movement_vector == (0, 2)
        assert game_manager.player_movement_direction == Direction.DOWN

    def test_combined_movements_set_diagonal_direction(self, game_manager):
        game_manager.set_player_movement(1, 0)
        game_manager.set_player_movement(0, 1)

        assert game_manager.player_movement_vector == (1, 1)
        assert game_manager.player_movement_direction == Direction.RIGHT_DOWN


class TestGetAggregateCollectableStats:
    def test_sums_records_of_all_levels(self, game_manager):
        first_level_stats = LevelStats()
        for _ in range(5):
            first_level_stats.record_diamond_placed()
            first_level_stats.record_diamond_collected(10)
        first_level_stats.record_key_placed()
        first_level_stats.record_key_collected(30)
        first_level_stats.record_bonus_awarded(500)

        second_level_stats = LevelStats()
        for _ in range(3):
            second_level_stats.record_diamond_placed()
        second_level_stats.record_diamond_collected(10)
        second_level_stats.record_diamond_collected(10)
        second_level_stats.record_key_placed()

        game_manager.level_stats = [first_level_stats, second_level_stats]

        diamond_totals, key_totals, bonus_totals = game_manager.get_aggregate_collectable_stats()

        assert (diamond_totals.count, diamond_totals.collected, diamond_totals.score) == (8, 7, 70)
        assert (key_totals.count, key_totals.collected, key_totals.score) == (2, 1, 30)
        assert (bonus_totals.awarded, bonus_totals.score) == (1, 500)


class TestGetAggregateKillStats:
    def test_sums_records_of_all_levels(self, game_manager):
        first_level_stats = LevelStats()
        first_level_stats.record_enemy_spawn(EnemyType.BAT)
        first_level_stats.record_enemy_spawn(EnemyType.BAT)
        first_level_stats.record_enemy_kill(EnemyType.BAT, 20)

        second_level_stats = LevelStats()
        second_level_stats.record_enemy_spawn(EnemyType.BAT)
        second_level_stats.record_enemy_kill(EnemyType.BAT, 20)
        second_level_stats.record_enemy_spawn(EnemyType.SPIDER_SMALL)
        second_level_stats.record_enemy_kill(EnemyType.SPIDER_SMALL, 50)

        game_manager.level_stats = [first_level_stats, second_level_stats]

        totals = game_manager.get_aggregate_kill_stats()

        bat_totals = totals[EnemyType.BAT]
        spider_small_totals = totals[EnemyType.SPIDER_SMALL]
        assert (bat_totals.count, bat_totals.killed, bat_totals.score) == (3, 2, 40)
        assert (spider_small_totals.count, spider_small_totals.killed, spider_small_totals.score) == (1, 1, 50)

    def test_returns_zero_records_for_enemy_types_absent_in_all_levels(self, game_manager):
        game_manager.level_stats = [LevelStats(), LevelStats()]

        totals = game_manager.get_aggregate_kill_stats()

        assert set(totals) == set(EnemyType)
        assert all((record.count, record.killed, record.score) == (0, 0, 0) for record in totals.values())
