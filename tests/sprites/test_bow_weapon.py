from unittest.mock import Mock

import pygame
import pytest

import src.sprites.bow_weapon
from src.enums.direction import Direction
from src.sprite_helper import SpriteHelper
from src.sprites.bow_weapon import BowWeapon

# Row of the bow image for each direction in img/bow.png
ROW_BY_DIRECTION = {
    Direction.RIGHT: 0,
    Direction.LEFT: 1,
    Direction.UP: 2,
    Direction.DOWN: 3,
    Direction.RIGHT_UP: 4,
    Direction.LEFT_UP: 5,
    Direction.RIGHT_DOWN: 6,
    Direction.LEFT_DOWN: 7,
}


# BowWeapon loads real images with convert_alpha(), so a display mode must be set around every test.
@pytest.fixture(autouse=True)
def pygame_display(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setattr(src.sprites.bow_weapon, 'SoundManager', Mock())
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def image_bytes(image):
    return pygame.image.tobytes(image, 'RGBA')


class TestSetCostume:
    def test_starts_with_right_image(self):
        bow_weapon = BowWeapon((0, 0), (), [], [], [])

        expected_image = SpriteHelper.get_tile_image('bow', ROW_BY_DIRECTION[Direction.RIGHT], 0)
        assert image_bytes(bow_weapon.image) == image_bytes(expected_image)

    @pytest.mark.parametrize('direction', list(Direction))
    def test_shows_bow_image_of_new_direction(self, direction):
        bow_weapon = BowWeapon((0, 0), (), [], [], [])

        bow_weapon.set_costume(direction)

        expected_image = SpriteHelper.get_tile_image('bow', ROW_BY_DIRECTION[direction], 0)
        assert bow_weapon.direction == direction
        assert image_bytes(bow_weapon.image) == image_bytes(expected_image)
