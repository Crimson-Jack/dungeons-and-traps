from unittest.mock import MagicMock

import pygame
import pytest

from src.camera_group import CameraGroup
from src.sprites.custom_draw_sprite import CustomDrawSprite


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


def create_camera_group():
    game_surface = pygame.Surface((100, 80))
    camera_group = CameraGroup(game_surface, (50, 50))
    camera_group.debugger.enabled = False
    return camera_group


class TestCustomDraw:
    def test_sprite_inside_visible_area_is_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = RecordingSprite([camera_group], pygame.Rect(10, 10, 20, 20), drawn_sprites)
        camera_group.custom_draw(None)
        assert drawn_sprites == [sprite]

    def test_sprite_outside_visible_area_is_not_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        RecordingSprite([camera_group], pygame.Rect(500, 500, 20, 20), drawn_sprites)
        camera_group.custom_draw(None)
        assert drawn_sprites == []

    def test_only_visible_sprites_are_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        visible_sprite = RecordingSprite([camera_group], pygame.Rect(10, 10, 20, 20), drawn_sprites)
        RecordingSprite([camera_group], pygame.Rect(500, 500, 20, 20), drawn_sprites)
        camera_group.custom_draw(None)
        assert drawn_sprites == [visible_sprite]

    def test_sprite_partially_inside_visible_area_is_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = RecordingSprite([camera_group], pygame.Rect(90, 70, 20, 20), drawn_sprites)
        camera_group.custom_draw(None)
        assert drawn_sprites == [sprite]

    def test_sprite_touching_visible_area_edge_is_not_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        RecordingSprite([camera_group], pygame.Rect(100, 0, 20, 20), drawn_sprites)
        camera_group.custom_draw(None)
        assert drawn_sprites == []

    def test_offset_moves_visible_area(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = RecordingSprite([camera_group], pygame.Rect(500, 500, 20, 20), drawn_sprites)
        camera_group.offset = pygame.math.Vector2(-450, -450)
        camera_group.custom_draw(None)
        assert drawn_sprites == [sprite]

    def test_additional_offset_moves_visible_area(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = RecordingSprite([camera_group], pygame.Rect(110, 10, 20, 20), drawn_sprites)
        camera_group.custom_draw(None, pygame.math.Vector2(-20, 0))
        assert drawn_sprites == [sprite]

    def test_additional_offset_is_removed_after_drawing(self):
        camera_group = create_camera_group()
        camera_group.custom_draw(None, pygame.math.Vector2(-20, 5))
        assert camera_group.offset == pygame.math.Vector2(0, 0)

    def test_custom_culling_rect_is_used_for_custom_draw_sprite(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        sprite = WideCullingRectSprite([camera_group], pygame.Rect(10, 200, 20, 20),
                                       pygame.Rect(10, 50, 20, 170), drawn_sprites)
        camera_group.custom_draw(None)
        assert drawn_sprites == [sprite]

    def test_plain_sprite_uses_its_rect(self):
        camera_group = create_camera_group()
        # Plain sprites are blitted directly on game_surface, so record the blit calls
        camera_group.game_surface = MagicMock()
        visible_sprite = pygame.sprite.Sprite(camera_group)
        visible_sprite.image = pygame.Surface((20, 20))
        visible_sprite.rect = pygame.Rect(10, 10, 20, 20)
        hidden_sprite = pygame.sprite.Sprite(camera_group)
        hidden_sprite.image = pygame.Surface((20, 20))
        hidden_sprite.rect = pygame.Rect(500, 500, 20, 20)
        camera_group.custom_draw(None)
        blitted_images = [call.args[0] for call in camera_group.game_surface.blit.call_args_list]
        assert blitted_images == [visible_sprite.image]

    def test_all_sprites_are_drawn_in_debug_mode(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        visible_sprite = RecordingSprite([camera_group], pygame.Rect(10, 10, 20, 20), drawn_sprites)
        hidden_sprite = RecordingSprite([camera_group], pygame.Rect(500, 500, 20, 20), drawn_sprites)
        camera_group.debugger.enabled = True
        camera_group.custom_draw(None)
        camera_group.debugger.enabled = False
        assert drawn_sprites == [visible_sprite, hidden_sprite]
