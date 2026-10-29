import pygame
import pytest

from settings import Settings
from src.enums.direction import Direction
from src.enums.enemy_type import EnemyType
from src.sprite_costume import SpriteCostume
from src.sprite_helper import SpriteHelper

TILE_SIZE = (Settings.TILE_SIZE, Settings.TILE_SIZE)
BOSS_SIZE = (Settings.TILE_SIZE * 3, Settings.TILE_SIZE * 3)
ICON_SIZE = (64, 64)
DIAGONAL_AND_VERTICAL_DIRECTIONS = [
    (Direction.RIGHT_DOWN, Direction.DOWN),
    (Direction.LEFT_DOWN, Direction.DOWN),
    (Direction.RIGHT_UP, Direction.UP),
    (Direction.LEFT_UP, Direction.UP),
]


# SpriteHelper loads real images from img/ with convert_alpha(), so a display mode must be set around every test.
@pytest.fixture(autouse=True)
def pygame_display(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def image_bytes(image):
    return pygame.image.tobytes(image, 'RGBA')


def sizes(images):
    return {image.get_size() for image in images}


class TestSingleImages:
    def test_tile_image_is_scaled_to_tile_size(self):
        assert SpriteHelper.get_tile_image('monster-enemy-blue', 1, 0).get_size() == TILE_SIZE

    def test_multi_tile_image_is_scaled_to_number_of_tiles(self):
        assert SpriteHelper.get_multi_tile_image('octopus-enemy', 1, 0, 3).get_size() == BOSS_SIZE

    @pytest.mark.parametrize('get_icon', [
        SpriteHelper.get_life_dashboard_icon,
        SpriteHelper.get_bow_header_icon,
        SpriteHelper.get_explosion_header_icon,
    ])
    def test_panel_icon_has_icon_size(self, get_icon):
        assert get_icon().get_size() == ICON_SIZE

    @pytest.mark.parametrize('enemy_type', list(EnemyType))
    def test_enemy_icon_is_scaled_to_given_size(self, enemy_type):
        assert SpriteHelper.get_enemy_icon(enemy_type, (32, 32)).get_size() == (32, 32)

    @pytest.mark.parametrize('get_image', [
        SpriteHelper.get_game_over_lose_image,
        SpriteHelper.get_game_over_win_image,
    ])
    def test_game_over_image_is_scaled_to_given_size(self, get_image):
        assert get_image((100, 100)).get_size() == (100, 100)


class TestFrameLists:
    @pytest.mark.parametrize('get_frames, number_of_frames, frame_size', [
        (SpriteHelper.get_tombstone_frames, 4, TILE_SIZE),
        (SpriteHelper.get_boss_tombstone_frames, 18, BOSS_SIZE),
        (SpriteHelper.get_vanishing_point_frames, 8, TILE_SIZE),
        (SpriteHelper.get_fire_ball_frames, 4, TILE_SIZE),
        (SpriteHelper.get_egg_frames, 4, TILE_SIZE),
        (SpriteHelper.get_sword_header_icons, 5, ICON_SIZE),
    ])
    def test_returns_frames_of_expected_number_and_size(self, get_frames, number_of_frames, frame_size):
        frames = get_frames()

        assert len(frames) == number_of_frames
        assert sizes(frames) == {frame_size}

    def test_monster_frames_are_four_tile_size_frames(self):
        frames = SpriteHelper.get_monster_frames('monster-enemy-blue')

        assert len(frames) == 4
        assert sizes(frames) == {TILE_SIZE}

    def test_octopus_frames_are_sixteen_boss_size_frames(self):
        frames = SpriteHelper.get_octopus_frames('octopus-enemy')

        assert len(frames) == 16
        assert sizes(frames) == {BOSS_SIZE}


class TestSpriteCostumesMatrix:
    # spider-enemy-small.png has 4 cells and 5 rows
    def test_returns_costume_of_every_row_for_each_cell(self):
        sprite_costumes = [SpriteCostume(pygame.Surface((1, 1)), number_of_frames)
                           for number_of_frames in [2, 4, 6, 8]]

        sprite_costumes_matrix = SpriteHelper.get_costumes_matrix('spider-enemy-small', sprite_costumes)

        assert len(sprite_costumes_matrix) == 4
        assert [len(cell_costumes) for cell_costumes in sprite_costumes_matrix] == [5, 5, 5, 5]

    def test_costumes_of_cell_take_number_of_frames_from_cell_costume(self):
        sprite_costumes = [SpriteCostume(pygame.Surface((1, 1)), number_of_frames)
                           for number_of_frames in [2, 4, 6, 8]]

        sprite_costumes_matrix = SpriteHelper.get_costumes_matrix('spider-enemy-small', sprite_costumes)

        assert [{sprite_costume.number_of_frames for sprite_costume in cell_costumes}
                for cell_costumes in sprite_costumes_matrix] == [{2}, {4}, {6}, {8}]


class TestImagesByDirection:
    def test_player_has_standing_and_walking_images_for_every_direction(self):
        player_frames = SpriteHelper.get_player_frames_by_direction(4)

        assert set(player_frames) == set(Direction)
        assert {len(frames) for frames in player_frames.values()} == {5}
        assert sizes(frame for frames in player_frames.values() for frame in frames) == {TILE_SIZE}

    @pytest.mark.parametrize('diagonal_direction, vertical_direction', DIAGONAL_AND_VERTICAL_DIRECTIONS)
    def test_player_diagonal_direction_uses_vertical_images(self, diagonal_direction, vertical_direction):
        player_frames = SpriteHelper.get_player_frames_by_direction(4)

        assert ([image_bytes(frame) for frame in player_frames[diagonal_direction]]
                == [image_bytes(frame) for frame in player_frames[vertical_direction]])

    @pytest.mark.parametrize('get_image_by_direction', [
        SpriteHelper.get_arrow_image_by_direction,
        SpriteHelper.get_bow_image_by_direction,
        SpriteHelper.get_explosion_image_by_direction,
    ])
    def test_returns_one_tile_size_image_for_every_direction(self, get_image_by_direction):
        image_by_direction = get_image_by_direction()

        assert set(image_by_direction) == set(Direction)
        assert sizes(image_by_direction.values()) == {TILE_SIZE}

    @pytest.mark.parametrize('diagonal_direction, vertical_direction', DIAGONAL_AND_VERTICAL_DIRECTIONS)
    def test_explosion_diagonal_direction_uses_vertical_image(self, diagonal_direction, vertical_direction):
        image_by_direction = SpriteHelper.get_explosion_image_by_direction()

        assert image_by_direction[diagonal_direction] is image_by_direction[vertical_direction]

    def test_sword_has_eight_frames_for_every_direction(self):
        sword_frames = SpriteHelper.get_sword_frames_by_direction()

        assert set(sword_frames) == set(Direction)
        assert {len(frames) for frames in sword_frames.values()} == {8}
        assert sizes(frame for frames in sword_frames.values() for frame in frames) == {TILE_SIZE}

    @pytest.mark.parametrize('diagonal_direction, vertical_direction', DIAGONAL_AND_VERTICAL_DIRECTIONS)
    def test_sword_diagonal_direction_uses_vertical_frames(self, diagonal_direction, vertical_direction):
        sword_frames = SpriteHelper.get_sword_frames_by_direction()

        assert sword_frames[diagonal_direction] is sword_frames[vertical_direction]

    def test_sword_repeats_its_fourth_frame_until_the_end(self):
        for frames in SpriteHelper.get_sword_frames_by_direction().values():
            assert len({image_bytes(frame) for frame in frames[3:]}) == 1
