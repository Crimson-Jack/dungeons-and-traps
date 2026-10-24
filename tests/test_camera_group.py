from unittest.mock import MagicMock

import pygame
import pytest

from settings import Settings
from src.camera_group import CameraGroup
from src.sprites.custom_draw_sprite import CustomDrawSprite

# The camera at the top left corner of the map keeps the map offset at (0, 0)
CAMERA_TARGET_AT_TOP_LEFT = (0, 0)
# Map of 50 x 50 tiles shown on a game surface of 100 x 80 pixels
MAP_SIZE_IN_PIXELS = 50 * Settings.TILE_SIZE


# Initialise and shut down Pygame around every test so that Surface, Vector2 and Rect behave correctly.
@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


class RecordingSprite(CustomDrawSprite):
    def __init__(self, groups, rect, drawn_sprites):
        super().__init__(groups)
        self.rect = rect
        self.drawn_sprites = drawn_sprites

    def custom_draw(self, game_surface, offset):
        self.drawn_sprites.append(self)


class WideCullingRectSprite(RecordingSprite):
    def __init__(self, groups, rect, culling_rect, drawn_sprites):
        super().__init__(groups, rect, drawn_sprites)
        self.culling_rect = culling_rect

    def get_culling_rect(self):
        return self.culling_rect


def create_camera_group(game_surface=None):
    return CameraGroup(game_surface or pygame.Surface((100, 80)), (50, 50))


class TestCustomDraw:
    def test_sprite_inside_visible_area_is_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = RecordingSprite([camera_group], pygame.Rect(10, 10, 20, 20), drawn_sprites)
        camera_group.custom_draw(CAMERA_TARGET_AT_TOP_LEFT)
        assert drawn_sprites == [sprite]

    def test_sprite_outside_visible_area_is_not_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        RecordingSprite([camera_group], pygame.Rect(500, 500, 20, 20), drawn_sprites)
        camera_group.custom_draw(CAMERA_TARGET_AT_TOP_LEFT)
        assert drawn_sprites == []

    def test_only_visible_sprites_are_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        visible_sprite = RecordingSprite([camera_group], pygame.Rect(10, 10, 20, 20), drawn_sprites)
        RecordingSprite([camera_group], pygame.Rect(500, 500, 20, 20), drawn_sprites)
        camera_group.custom_draw(CAMERA_TARGET_AT_TOP_LEFT)
        assert drawn_sprites == [visible_sprite]

    def test_sprite_partially_inside_visible_area_is_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = RecordingSprite([camera_group], pygame.Rect(90, 70, 20, 20), drawn_sprites)
        camera_group.custom_draw(CAMERA_TARGET_AT_TOP_LEFT)
        assert drawn_sprites == [sprite]

    def test_sprite_touching_visible_area_edge_is_not_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        RecordingSprite([camera_group], pygame.Rect(100, 0, 20, 20), drawn_sprites)
        camera_group.custom_draw(CAMERA_TARGET_AT_TOP_LEFT)
        assert drawn_sprites == []

    def test_camera_target_moves_visible_area(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = RecordingSprite([camera_group], pygame.Rect(500, 500, 20, 20), drawn_sprites)
        camera_group.custom_draw(sprite.rect.center)
        assert drawn_sprites == [sprite]

    def test_additional_offset_moves_visible_area(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = RecordingSprite([camera_group], pygame.Rect(110, 10, 20, 20), drawn_sprites)
        camera_group.custom_draw(CAMERA_TARGET_AT_TOP_LEFT, pygame.math.Vector2(-20, 0))
        assert drawn_sprites == [sprite]

    def test_additional_offset_is_removed_after_drawing(self):
        camera_group = create_camera_group()
        camera_group.custom_draw(CAMERA_TARGET_AT_TOP_LEFT, pygame.math.Vector2(-20, 5))
        assert camera_group.get_map_offset() == pygame.math.Vector2(0, 0)

    def test_custom_culling_rect_is_used_for_custom_draw_sprite(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = WideCullingRectSprite([camera_group], pygame.Rect(10, 200, 20, 20),
                                       pygame.Rect(10, 50, 20, 170), drawn_sprites)
        camera_group.custom_draw(CAMERA_TARGET_AT_TOP_LEFT)
        assert drawn_sprites == [sprite]

    def test_plain_sprite_uses_its_rect(self):
        # Plain sprites are blitted directly on game_surface, so record the blit calls
        game_surface = MagicMock()
        game_surface.get_size.return_value = (100, 80)
        camera_group = create_camera_group(game_surface)
        visible_sprite = pygame.sprite.Sprite(camera_group)
        visible_sprite.image = pygame.Surface((20, 20))
        visible_sprite.rect = pygame.Rect(10, 10, 20, 20)
        hidden_sprite = pygame.sprite.Sprite(camera_group)
        hidden_sprite.image = pygame.Surface((20, 20))
        hidden_sprite.rect = pygame.Rect(500, 500, 20, 20)
        camera_group.custom_draw(CAMERA_TARGET_AT_TOP_LEFT)
        blitted_images = [call.args[0] for call in game_surface.blit.call_args_list]
        assert blitted_images == [visible_sprite.image]


class TestMapOffset:
    def test_camera_target_is_centered(self):
        camera_group = create_camera_group()
        camera_group.custom_draw((1000, 1000))
        assert camera_group.get_map_offset() == pygame.math.Vector2(50 - 1000, 40 - 1000)

    def test_map_is_aligned_to_top_left_near_top_left_edge(self):
        camera_group = create_camera_group()
        camera_group.custom_draw((10, 10))
        assert camera_group.get_map_offset() == pygame.math.Vector2(0, 0)

    def test_map_is_aligned_to_bottom_right_near_bottom_right_edge(self):
        camera_group = create_camera_group()
        camera_group.custom_draw((MAP_SIZE_IN_PIXELS - 10, MAP_SIZE_IN_PIXELS - 10))
        assert camera_group.get_map_offset() == pygame.math.Vector2(100 - MAP_SIZE_IN_PIXELS,
                                                                    80 - MAP_SIZE_IN_PIXELS)

    def test_map_smaller_than_game_surface_does_not_scroll(self):
        camera_group = CameraGroup(pygame.Surface((Settings.TILE_SIZE * 2, Settings.TILE_SIZE * 2)), (1, 1))
        camera_group.custom_draw((1000, 1000))
        assert camera_group.get_map_offset() == pygame.math.Vector2(0, 0)
