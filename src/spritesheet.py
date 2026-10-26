import pygame


class SpriteSheet:
    """
    Image divided into a grid of cells of the same size; cuts out a single cell as a scaled image.
    The transparency of the cut-out cell comes from the alpha channel of the sheet image.
    """

    def __init__(self, sheet_image: pygame.Surface, cell_width: int, cell_height: int,
                 scaled_size: tuple[float, float]) -> None:
        """
        Store the sheet image and count its cells and rows.

        :param sheet_image: whole sprite sheet image with an alpha channel (loaded with convert_alpha())
        :param cell_width: width of a single cell in the sheet image
        :param cell_height: height of a single cell in the sheet image
        :param scaled_size: size the cut-out cell is scaled to
        """
        self._sheet_image = sheet_image
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._scaled_size = scaled_size

        # Calculate cells and rows count
        self._number_of_cells = self._sheet_image.get_width() // self._cell_width
        self._number_of_rows = self._sheet_image.get_height() // self._cell_height

    @property
    def number_of_cells(self) -> int:
        """Number of cells in a row of the sheet image."""
        return self._number_of_cells

    @property
    def number_of_rows(self) -> int:
        """Number of rows in the sheet image."""
        return self._number_of_rows

    def get_image(self, row: int, cell: int) -> pygame.Surface:
        """
        Cut out the cell from the sheet image and scale it to the scaled size.

        :param row: row of the cell, counted from 0 at the top
        :param cell: cell in the row, counted from 0 at the left
        :return: scaled image of the cell
        :raises IndexError: when the row or the cell is outside the sheet image
        """
        if not (0 <= row < self._number_of_rows and 0 <= cell < self._number_of_cells):
            raise IndexError(f'Cell (row {row}, cell {cell}) is outside the sprite sheet '
                             f'of {self._number_of_rows} rows and {self._number_of_cells} cells')

        cell_rectangle = pygame.Rect(cell * self._cell_width, row * self._cell_height,
                                     self._cell_width, self._cell_height)

        return pygame.transform.scale(self._sheet_image.subsurface(cell_rectangle), self._scaled_size)
