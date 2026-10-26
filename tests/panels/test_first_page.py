import pygame
import pytest

from settings import Settings
from src.panels.first_page import FirstPage


# FirstPage converts its image in the constructor, so a display mode must be set around every test.
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


class TestFirstPage:
    def test_scales_image_to_final_size(self, screen):
        first_page = FirstPage(screen)

        assert first_page.background_image.get_size() == FirstPage.IMAGE_SIZE

    def test_centers_image_on_screen(self, screen):
        first_page = FirstPage(screen)

        assert first_page.image_position == (
            (Settings.WIDTH - FirstPage.IMAGE_SIZE[0]) // 2,
            (Settings.HEIGHT - FirstPage.IMAGE_SIZE[1]) // 2,
        )

    def test_draw_blits_image_at_its_position(self, screen):
        first_page = FirstPage(screen)
        screen.fill((0, 0, 0))
        first_page.background_image.fill((255, 0, 0))

        first_page.draw()

        image_center = (first_page.image_position[0] + FirstPage.IMAGE_SIZE[0] // 2,
                        first_page.image_position[1] + FirstPage.IMAGE_SIZE[1] // 2)
        assert screen.get_at(image_center)[:3] == (255, 0, 0)
