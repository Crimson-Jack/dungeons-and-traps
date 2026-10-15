from collections import Counter
from unittest.mock import Mock

import pygame
import pytest

from src.enums.enemy_type import EnemyType
from src.level import Level
from src.sprites.tombstone import Tombstone


def create_level_with_effects(tombstones=None, vanishing_points=None, particle_effects=None):
    # Full constructor loads a TMX map, which is irrelevant for removing expired effects
    level = object.__new__(Level)
    level.tombstones = tombstones or []
    level.vanishing_points = vanishing_points or []
    level.particle_effects = particle_effects or []
    return level


def create_tombstone(group, is_expired):
    last_slide_counter = -1 if is_expired else 10
    return Tombstone([pygame.Surface((1, 1))], (0, 0), (group,), last_slide_counter)


def create_effect(is_expired):
    effect = Mock()
    effect.is_expired.return_value = is_expired
    return effect


class TestRemoveUnnecessaryEffects:
    def test_removes_adjacent_expired_tombstones_in_one_call(self):
        group = pygame.sprite.Group()
        first_expired_tombstone = create_tombstone(group, is_expired=True)
        second_expired_tombstone = create_tombstone(group, is_expired=True)
        active_tombstone = create_tombstone(group, is_expired=False)
        level = create_level_with_effects(
            tombstones=[first_expired_tombstone, second_expired_tombstone, active_tombstone])

        level.remove_unnecessary_effects()

        assert level.tombstones == [active_tombstone]
        assert group.sprites() == [active_tombstone]

    def test_keeps_active_tombstones_in_order(self):
        group = pygame.sprite.Group()
        first_active_tombstone = create_tombstone(group, is_expired=False)
        expired_tombstone = create_tombstone(group, is_expired=True)
        second_active_tombstone = create_tombstone(group, is_expired=False)
        level = create_level_with_effects(
            tombstones=[first_active_tombstone, expired_tombstone, second_active_tombstone])

        level.remove_unnecessary_effects()

        assert level.tombstones == [first_active_tombstone, second_active_tombstone]

    def test_removes_and_kills_adjacent_expired_vanishing_points(self):
        first_expired_vanishing_point = create_effect(is_expired=True)
        second_expired_vanishing_point = create_effect(is_expired=True)
        active_vanishing_point = create_effect(is_expired=False)
        level = create_level_with_effects(
            vanishing_points=[first_expired_vanishing_point, second_expired_vanishing_point, active_vanishing_point])

        level.remove_unnecessary_effects()

        assert level.vanishing_points == [active_vanishing_point]
        first_expired_vanishing_point.kill.assert_called_once()
        second_expired_vanishing_point.kill.assert_called_once()
        active_vanishing_point.kill.assert_not_called()

    def test_removes_adjacent_expired_particle_effects(self):
        first_expired_particle_effect = create_effect(is_expired=True)
        second_expired_particle_effect = create_effect(is_expired=True)
        active_particle_effect = create_effect(is_expired=False)
        level = create_level_with_effects(
            particle_effects=[first_expired_particle_effect, second_expired_particle_effect, active_particle_effect])

        level.remove_unnecessary_effects()

        assert level.particle_effects == [active_particle_effect]


class TestShowExitPoint:
    def test_missing_exit_point_raises_value_error(self):
        # Full constructor loads a TMX map, which is irrelevant for showing the exit point
        level = object.__new__(Level)
        level.exit_point = None
        level.blast_effect = Mock()

        with pytest.raises(ValueError, match='exit-point'):
            level.show_exit_point()

        level.blast_effect.run.assert_not_called()

    def test_shows_exit_point_with_blast_effect(self):
        level = object.__new__(Level)
        level.exit_point = Mock()
        level.blast_effect = Mock()

        level.show_exit_point()

        level.blast_effect.run.assert_called_once()
        level.exit_point.show.assert_called_once()


class TestEnableTiltEffect:
    def test_passes_speed_to_tilt_effect(self):
        # Full constructor loads a TMX map, which is irrelevant for enabling the tilt effect
        level = object.__new__(Level)
        level.tilt_effect = Mock()

        level.enable_tilt_effect(0.5)

        level.tilt_effect.enable.assert_called_once_with(0.5)


def count_sprite_classes(group):
    return dict(Counter(type(sprite).__name__ for sprite in group))


# basic.tmx is the only map that contains all sprite layers
@pytest.fixture
def basic_level(game):
    level_filenames = [level_details.source_file for level_details in game.game_manager.LEVELS]
    game.game_manager.clear_settings_for_first_level(level_filenames.index('basic.tmx'))
    game.screen_manager.rebuild_level()
    return game.screen_manager.level


class TestCreateSpritesFromBasicMap:
    def test_bottom_background_layer(self, basic_level):
        assert count_sprite_classes(basic_level.level_sprite_groups.bottom_background_layer) == {
            'CheckPoint': 1, 'ExitPoint': 1, 'Ground': 600}

    def test_bottom_sprites_layer(self, basic_level):
        assert count_sprite_classes(basic_level.level_sprite_groups.bottom_sprites_layer) == {
            'BowPowerup': 5, 'Diamond': 1, 'EnergyPowerup': 3, 'ExplosionPowerup': 1, 'FireFlameEnemyLeft': 1,
            'FireFlameEnemyRight': 2, 'Key': 2, 'LifePowerup': 1, 'LightingSpell': 3, 'SwordPowerup': 2,
            'Teleport': 3}

    def test_middle_sprites_layer(self, basic_level):
        assert count_sprite_classes(basic_level.level_sprite_groups.middle_sprites_layer) == {
            'BowWeapon': 1, 'DemolishedWall': 18, 'Door': 2, 'ExplosionWeapon': 1, 'Player': 1, 'Stone': 39,
            'SwordWeapon': 1, 'Wall': 206}

    def test_top_sprites_layer(self, basic_level):
        assert count_sprite_classes(basic_level.level_sprite_groups.top_sprites_layer) == {
            'BatEnemy': 1, 'GhostEnemy': 3, 'MonsterEnemy': 3, 'SpiderEnemy': 3}

    def test_the_highest_sprites_layer(self, basic_level):
        assert count_sprite_classes(basic_level.level_sprite_groups.the_highest_sprites_layer) == {'OctopusEnemy': 1}

    def test_functional_groups(self, basic_level):
        assert {group_name: len(getattr(basic_level.level_sprite_groups, group_name)) for group_name in (
            'exit_points', 'obstacle_sprites', 'moving_obstacle_sprites', 'removable_obstacle_sprites',
            'passage_sprites', 'teleport_sprites', 'collectable_sprites', 'enemy_sprites',
            'hostile_force_sprites')} == {
            'exit_points': 1, 'obstacle_sprites': 226, 'moving_obstacle_sprites': 39,
            'removable_obstacle_sprites': 18, 'passage_sprites': 2, 'teleport_sprites': 3,
            'collectable_sprites': 19, 'enemy_sprites': 11, 'hostile_force_sprites': 3}

    def test_obstacle_map_merges_walls_stones_demolished_walls_and_doors(self, basic_level):
        obstacle_map_items = basic_level.obstacle_map.items
        assert (len(obstacle_map_items), len(obstacle_map_items[0])) == (20, 30)
        # 206 walls, 39 stones, 18 demolished walls and 2 doors
        assert sum(sum(row) for row in obstacle_map_items) == 265

    def test_registers_diamonds_and_keys_in_game_manager(self, game, basic_level):
        assert len(game.game_manager.diamonds) == 1
        assert len(game.game_manager.keys) == 2

    def test_records_enemy_spawns(self, game, basic_level):
        level_stats = game.game_manager.level_stats[-1]
        assert {enemy_type: level_stats.get_enemy_record(enemy_type).count for enemy_type in EnemyType
                if level_stats.get_enemy_record(enemy_type).count} == {
            EnemyType.SPIDER_SMALL: 1, EnemyType.SPIDER_MEDIUM: 1, EnemyType.SPIDER_BIG: 1,
            EnemyType.MONSTER_BLUE: 1, EnemyType.MONSTER_GREEN: 1, EnemyType.MONSTER_RED: 1, EnemyType.BAT: 1}
