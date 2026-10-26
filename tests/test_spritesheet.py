import pygame
import pytest

from src.spritesheet import SpriteSheet

CELL_SIZE = 4
SCALED_SIZE = (8, 8)
NUMBER_OF_ROWS = 2
NUMBER_OF_CELLS = 3
BACKGROUND_COLOR = (255, 255, 255)


def cell_color(row, cell):
    return 50 + row * 100, 40 + cell * 80, 200


# Sheet of NUMBER_OF_ROWS x NUMBER_OF_CELLS cells, each filled with its own cell_color.
# SRCALPHA gives the sheet an alpha channel, like a PNG loaded with convert_alpha().
def create_sheet_image():
    sheet_image = pygame.Surface((NUMBER_OF_CELLS * CELL_SIZE, NUMBER_OF_ROWS * CELL_SIZE), pygame.SRCALPHA)
    for row in range(NUMBER_OF_ROWS):
        for cell in range(NUMBER_OF_CELLS):
            sheet_image.fill(cell_color(row, cell), (cell * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    return sheet_image


def create_single_cell_sheet_image(color):
    sheet_image = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    sheet_image.fill(color)
    return sheet_image


def create_sprite_sheet(sheet_image=None):
    if sheet_image is None:
        sheet_image = create_sheet_image()
    return SpriteSheet(sheet_image, CELL_SIZE, CELL_SIZE, SCALED_SIZE)


def center_color(image):
    return tuple(image.get_at((image.get_width() // 2, image.get_height() // 2)))[:3]


# Draws the image on a white background, so transparent pixels show the background color
def color_on_background(image):
    background = pygame.Surface(image.get_size())
    background.fill(BACKGROUND_COLOR)
    background.blit(image, (0, 0))
    return center_color(background)


class TestSpriteSheetGrid:
    def test_number_of_rows_is_counted_from_sheet_height(self):
        assert create_sprite_sheet().number_of_rows == NUMBER_OF_ROWS

    def test_number_of_cells_is_counted_from_sheet_width(self):
        assert create_sprite_sheet().number_of_cells == NUMBER_OF_CELLS


class TestSpriteSheetGetImage:
    def test_image_is_scaled_to_scaled_size(self):
        assert create_sprite_sheet().get_image(0, 0).get_size() == SCALED_SIZE

    @pytest.mark.parametrize('row, cell', [(0, 0), (0, 2), (1, 1)])
    def test_image_shows_selected_cell(self, row, cell):
        assert center_color(create_sprite_sheet().get_image(row, cell)) == cell_color(row, cell)

    def test_transparent_pixel_stays_transparent(self):
        sheet_image = create_single_cell_sheet_image((255, 0, 0, 0))
        image = create_sprite_sheet(sheet_image).get_image(0, 0)
        assert color_on_background(image) == BACKGROUND_COLOR

    def test_opaque_black_pixel_stays_visible(self):
        sheet_image = create_single_cell_sheet_image((0, 0, 0, 255))
        image = create_sprite_sheet(sheet_image).get_image(0, 0)
        assert color_on_background(image) == (0, 0, 0)

    def test_half_transparent_pixel_keeps_its_transparency(self):
        sheet_image = create_single_cell_sheet_image((255, 0, 0, 128))
        image = create_sprite_sheet(sheet_image).get_image(0, 0)
        assert tuple(image.get_at((0, 0))) == (255, 0, 0, 128)

    @pytest.mark.parametrize('row, cell', [(NUMBER_OF_ROWS, 0), (0, NUMBER_OF_CELLS), (-1, 0), (0, -1)])
    def test_cell_outside_sheet_raises_index_error(self, row, cell):
        with pytest.raises(IndexError):
            create_sprite_sheet().get_image(row, cell)
