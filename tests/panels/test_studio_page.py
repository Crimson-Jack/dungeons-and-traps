import pygame
import pytest

from settings import Settings
from src.panels.studio_page import StudioPage


# StudioPage converts its image in the constructor, so a display mode must be set around every test.
@pytest.fixture(autouse=True)
def pygame_display(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture
def screen():
    return pygame.Surface((Settings.WIDTH, Settings.HEIGHT))


class TestStudioPage:
    def test_scales_image_to_final_size(self, screen):
        studio_page = StudioPage(screen)

        assert studio_page.background_image.get_size() == StudioPage.IMAGE_SIZE

    def test_centers_image_on_screen(self, screen):
        studio_page = StudioPage(screen)

        assert studio_page.image_position == (
            (Settings.WIDTH - StudioPage.IMAGE_SIZE[0]) // 2,
            (Settings.HEIGHT - StudioPage.IMAGE_SIZE[1]) // 2,
        )

    def test_draw_blits_image_at_its_position(self, screen):
        studio_page = StudioPage(screen)
        screen.fill((0, 0, 0))
        studio_page.background_image.fill((255, 0, 0))

        studio_page.draw()

        image_center = (studio_page.image_position[0] + StudioPage.IMAGE_SIZE[0] // 2,
                        studio_page.image_position[1] + StudioPage.IMAGE_SIZE[1] // 2)
        assert screen.get_at(image_center)[:3] == (255, 0, 0)
