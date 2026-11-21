from unittest.mock import Mock

import pygame
import pytest

import src.sprites.explosion_weapon
from settings import Settings
from src.abstract_classes.damageable_enemy import DamageableEnemy
from src.enums.direction import Direction
from src.events import Events
from src.sprite_helper import SpriteHelper
from src.sprites.explosion_weapon import ExplosionWeapon

# Row of the TNT image for each direction in img/tnt.png; the sheet has no diagonal images,
# so diagonal directions show the up and down images
ROW_BY_DIRECTION = {
    Direction.RIGHT: 0,
    Direction.LEFT: 1,
    Direction.UP: 2,
    Direction.DOWN: 3,
    Direction.RIGHT_UP: 2,
    Direction.LEFT_UP: 2,
    Direction.RIGHT_DOWN: 3,
    Direction.LEFT_DOWN: 3,
}


# ExplosionWeapon loads real images with convert_alpha(), so a display mode must be set around every test.
@pytest.fixture(autouse=True)
def pygame_display(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setattr(src.sprites.explosion_weapon, 'SoundManager', Mock())
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def image_bytes(image):
    return pygame.image.tobytes(image, 'RGBA')


def create_enemy_at(center):
    enemy = Mock(spec=DamageableEnemy)
    enemy.rect = pygame.Rect(0, 0, 10, 10)
    enemy.rect.center = center
    return enemy


def run_until_explosion(explosion_weapon):
    for step_number in range(Settings.NUMBER_OF_EXPLOSION_STEPS + 1):
        explosion_weapon.update()


class TestSetCostume:
    def test_starts_with_right_image(self):
        explosion_weapon = ExplosionWeapon((0, 0), (), [])

        expected_image = SpriteHelper.get_tile_image('tnt', ROW_BY_DIRECTION[Direction.RIGHT], 0)
        assert image_bytes(explosion_weapon.image) == image_bytes(expected_image)

    @pytest.mark.parametrize('direction', list(Direction))
    def test_shows_tnt_image_of_new_direction(self, direction):
        explosion_weapon = ExplosionWeapon((0, 0), (), [])

        explosion_weapon.set_costume(direction)

        expected_image = SpriteHelper.get_tile_image('tnt', ROW_BY_DIRECTION[direction], 0)
        assert explosion_weapon.direction == direction
        assert image_bytes(explosion_weapon.image) == image_bytes(expected_image)


class TestFire:
    FIRE_POSITION = (100, 100)
    # Far beyond the explosion range from FIRE_POSITION
    FAR_POSITION = (10000, 10000)

    def test_unarmed_weapon_does_not_fire(self):
        explosion_weapon = ExplosionWeapon(self.FIRE_POSITION, (), [])
        pygame.event.clear()

        assert explosion_weapon.fire() is False
        assert pygame.event.get(Events.CREATE_EXPLODE_EFFECT_EVENT) == []

    def test_armed_weapon_posts_explode_effect_at_its_center_on_map(self):
        explosion_weapon = ExplosionWeapon(self.FIRE_POSITION, (), [])
        explosion_weapon.arm_weapon()
        pygame.event.clear()

        assert explosion_weapon.fire() is True

        posted_events = pygame.event.get(Events.CREATE_EXPLODE_EFFECT_EVENT)
        assert len(posted_events) == 1
        assert posted_events[0].position == explosion_weapon.rect.center

    def test_damages_enemy_at_explosion_center_after_weapon_moved(self):
        enemies = []
        explosion_weapon = ExplosionWeapon(self.FIRE_POSITION, (), enemies)
        enemy = create_enemy_at(explosion_weapon.rect.center)
        enemies.append(enemy)
        explosion_weapon.arm_weapon()
        explosion_weapon.fire()

        explosion_weapon.set_position(self.FAR_POSITION)
        run_until_explosion(explosion_weapon)

        enemy.decrease_energy.assert_called_once_with(explosion_weapon.damage_power)

    def test_does_not_damage_enemy_near_new_weapon_position(self):
        enemies = []
        explosion_weapon = ExplosionWeapon(self.FIRE_POSITION, (), enemies)
        explosion_weapon.arm_weapon()
        explosion_weapon.fire()

        explosion_weapon.set_position(self.FAR_POSITION)
        enemy = create_enemy_at(explosion_weapon.rect.center)
        enemies.append(enemy)
        run_until_explosion(explosion_weapon)

        enemy.decrease_energy.assert_not_called()
