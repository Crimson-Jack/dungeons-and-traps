import math
import pygame


class ExplodeEffect:
    """Rings of an explosion that grow from a position until they reach the maximum size, then disappear."""

    # Rings drawn inside the explosion rectangle: (inflate_x, inflate_y, line_width)
    RINGS = ((-5, -25, 1), (-25, -5, 1), (-30, -65, 3), (-65, -30, 3), (-70, -100, 5), (-100, -70, 5))

    def __init__(self, game_surface: pygame.Surface, steps: int, color: tuple[int, int, int],
                 max_size: tuple[int, int]) -> None:
        """
        Create a hidden explode effect; it is started with run().

        :param game_surface: game surface the rings are drawn on
        :param steps: number of updates the rings need to reach the maximum size
        :param color: color of the rings
        :param max_size: maximum size of the explosion rectangle
        """
        self._game_surface = game_surface
        self._width = max_size[0]
        self._height = max_size[1]
        self._step_x = self._width / steps
        self._step_y = self._height / steps
        self._color = color
        self._visible = False
        self._base_rectangle = pygame.rect.Rect(0, 0, 0, 0)
        self._rectangle = pygame.rect.Rect(0, 0, 0, 0)
        self._counter = 1

    def run(self, position: tuple[int, int]) -> None:
        """
        Start the explosion from the smallest rings centered at the position.

        :param position: center of the explosion on the game surface
        """
        self._reset(position)
        self._visible = True

    def update(self) -> None:
        """Grow the rings by one step; hide the effect once they reach the maximum size."""
        if self._visible:
            if self._rectangle.width < self._width and self._rectangle.height < self._height:
                self._rectangle = self._base_rectangle.inflate(self._step_x * self._counter,
                                                               self._step_y * self._counter)
                self._counter += 1
            else:
                self._stop()

    def draw(self) -> None:
        """Draw the rings while the effect is visible."""
        if self._visible:
            for inflate_x, inflate_y, line_width in self.RINGS:
                pygame.draw.arc(self._game_surface, self._color, self._rectangle.inflate(inflate_x, inflate_y),
                                0, 2 * math.pi, line_width)

    def _reset(self, position: tuple[int, int]) -> None:
        self._counter = 1

        # Set base rectangle properties
        self._base_rectangle.width = int(self._step_x)
        self._base_rectangle.height = int(self._step_y)
        top_left_x = int(position[0] - self._step_x / 2)
        top_left_y = int(position[1] - self._step_y / 2)
        self._base_rectangle.topleft = top_left_x, top_left_y

        # Create a copy
        self._rectangle = pygame.rect.Rect(self._base_rectangle)

    def _stop(self) -> None:
        self._visible = False
