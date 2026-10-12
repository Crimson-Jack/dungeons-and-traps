from unittest.mock import Mock

import pygame

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
