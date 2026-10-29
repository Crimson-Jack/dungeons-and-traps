from unittest.mock import Mock

import pygame
import pytest

import src.sprites.bow_weapon
import src.sprites.explosion_weapon
import src.sprites.player
import src.sprites.sword_weapon
from src.enums.direction import Direction
from src.sprite_helper import SpriteHelper
from src.sprites.player import Player

# Rows of the standing and walking images for each direction in img/player.png; the sheet has no diagonal rows,
# so diagonal directions show the up and down images
STANDING_ROW_BY_DIRECTION = {
    Direction.RIGHT: 0,
    Direction.LEFT: 2,
    Direction.UP: 4,
    Direction.DOWN: 6,
    Direction.RIGHT_UP: 4,
    Direction.LEFT_UP: 4,
    Direction.RIGHT_DOWN: 6,
    Direction.LEFT_DOWN: 6,
}
WALKING_ROW_BY_DIRECTION = {direction: row + 1 for direction, row in STANDING_ROW_BY_DIRECTION.items()}
NUMBER_OF_WALKING_FRAMES = 4


# Player and its weapons load real images with convert_alpha(), so a display mode must be set around every test.
@pytest.fixture(autouse=True)
def pygame_display(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    for module in [src.sprites.player, src.sprites.sword_weapon, src.sprites.bow_weapon,
                   src.sprites.explosion_weapon]:
        monkeypatch.setattr(module, 'SoundManager', Mock())
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def image_bytes(image):
    return pygame.image.tobytes(image, 'RGBA')


# Collision groups and the game manager are irrelevant for the costume
def create_player():
    return Player((0, 0), (), (), 1, [], [], [], [], [], [], [], [], Mock())


# Costume index 0 is the standing image, indexes 1 to NUMBER_OF_WALKING_FRAMES are the walking images
def expected_player_image(direction, costume_index):
    if costume_index == 0:
        return SpriteHelper.get_tile_image('player', STANDING_ROW_BY_DIRECTION[direction], 0)
    return SpriteHelper.get_tile_image('player', WALKING_ROW_BY_DIRECTION[direction], costume_index - 1)


class TestSetCostume:
    def test_starts_with_standing_right_image(self):
        player = create_player()

        assert image_bytes(player.image) == image_bytes(expected_player_image(Direction.RIGHT, 0))

    @pytest.mark.parametrize('direction', list(Direction))
    @pytest.mark.parametrize('costume_index', range(NUMBER_OF_WALKING_FRAMES + 1))
    def test_shows_player_image_of_direction_and_costume_index(self, direction, costume_index):
        player = create_player()

        player.set_costume(direction, costume_index)

        assert image_bytes(player.image) == image_bytes(expected_player_image(direction, costume_index))
