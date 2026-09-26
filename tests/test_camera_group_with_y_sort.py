import pygame
import pytest

from src.camera_group_with_y_sort import CameraGroupWithYSort
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


def create_camera_group():
    game_surface = pygame.Surface((100, 80))
    camera_group = CameraGroupWithYSort(game_surface, (50, 50))
    camera_group.debugger.enabled = False
    return camera_group


class TestCustomDraw:
    def test_only_visible_sprites_are_drawn(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        visible_sprite = RecordingSprite([camera_group], pygame.Rect(10, 10, 20, 20), drawn_sprites)
        RecordingSprite([camera_group], pygame.Rect(500, 500, 20, 20), drawn_sprites)
        camera_group.custom_draw(None)
        assert drawn_sprites == [visible_sprite]

    def test_visible_sprites_are_drawn_in_y_order(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        lower_sprite = RecordingSprite([camera_group], pygame.Rect(10, 50, 20, 20), drawn_sprites)
        RecordingSprite([camera_group], pygame.Rect(10, 300, 20, 20), drawn_sprites)
        upper_sprite = RecordingSprite([camera_group], pygame.Rect(40, 5, 20, 20), drawn_sprites)
        middle_sprite = RecordingSprite([camera_group], pygame.Rect(70, 30, 20, 20), drawn_sprites)
        camera_group.custom_draw(None)
        assert drawn_sprites == [upper_sprite, middle_sprite, lower_sprite]

    def test_all_sprites_are_drawn_in_debug_mode(self):
        camera_group = create_camera_group()
        drawn_sprites = []
        visible_sprite = RecordingSprite([camera_group], pygame.Rect(10, 10, 20, 20), drawn_sprites)
        hidden_sprite = RecordingSprite([camera_group], pygame.Rect(500, 500, 20, 20), drawn_sprites)
        camera_group.debugger.enabled = True
        camera_group.custom_draw(None)
        camera_group.debugger.enabled = False
        assert drawn_sprites == [visible_sprite, hidden_sprite]
