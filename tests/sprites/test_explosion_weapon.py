from unittest.mock import Mock

import pygame
import pytest

import src.sprites.explosion_weapon
from src.enums.direction import Direction
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
