from unittest.mock import Mock

import pygame
import pytest

import src.sprites.arrow
from src.enums.direction import Direction
from src.sprite_helper import SpriteHelper
from src.sprites.arrow import Arrow

# Row of the arrow image for each direction in img/arrow.png
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


# Arrow loads real images with convert_alpha(), so a display mode must be set around every test.
@pytest.fixture(autouse=True)
def pygame_display(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setattr(src.sprites.arrow, 'SoundManager', Mock())
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def image_bytes(image):
    return pygame.image.tobytes(image, 'RGBA')


class TestImage:
    @pytest.mark.parametrize('direction', list(Direction))
    def test_shows_arrow_image_of_its_direction(self, direction):
        arrow = Arrow((0, 0), (), [], [], [], direction)

        expected_image = SpriteHelper.get_tile_image('arrow', ROW_BY_DIRECTION[direction], 0)
        assert image_bytes(arrow.image) == image_bytes(expected_image)
