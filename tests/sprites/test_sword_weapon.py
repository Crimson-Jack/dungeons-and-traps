from unittest.mock import Mock

import pygame
import pytest

import src.sprites.sword_weapon
from src.enums.direction import Direction
from src.sprite_helper import SpriteHelper
from src.sprites.sword_weapon import SwordWeapon

# Row of the sword strike for each direction in img/sword.png; the sheet has no diagonal rows,
# so diagonal directions show the up and down strikes
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
# Cell of the sword strike for each costume index; the last cell is repeated to keep the sword extended
CELL_BY_COSTUME_INDEX = [0, 1, 2, 3, 3, 3, 3, 3]


# SwordWeapon loads real images with convert_alpha(), so a display mode must be set around every test.
@pytest.fixture(autouse=True)
def pygame_display(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setattr(src.sprites.sword_weapon, 'SoundManager', Mock())
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def image_bytes(image):
    return pygame.image.tobytes(image, 'RGBA')


def create_sword_weapon():
    return SwordWeapon((0, 0), (), Mock(), [], [], [])


class TestSetCostume:
    def test_starts_with_first_right_image(self):
        sword_weapon = create_sword_weapon()

        expected_image = SpriteHelper.get_tile_image('sword', ROW_BY_DIRECTION[Direction.RIGHT], 0)
        assert image_bytes(sword_weapon.image) == image_bytes(expected_image)

    @pytest.mark.parametrize('direction', list(Direction))
    @pytest.mark.parametrize('costume_index', range(len(CELL_BY_COSTUME_INDEX)))
    def test_shows_sword_strike_image_of_new_direction_and_costume_index(self, direction, costume_index):
        sword_weapon = create_sword_weapon()

        sword_weapon.set_costume(direction, costume_index)

        expected_image = SpriteHelper.get_tile_image('sword', ROW_BY_DIRECTION[direction],
                                                     CELL_BY_COSTUME_INDEX[costume_index])
        assert sword_weapon.direction == direction
        assert image_bytes(sword_weapon.image) == image_bytes(expected_image)
