import pygame

from src.enums.lighting_status import LightingStatus
from src.game_helper import GameHelper


class DarknessEffect:
    """Covers the game surface with darkness, leaving a lit circle around the player."""

    # Circles of light for each darkness status: (radius, alpha), from the largest circle to the smallest,
    # so each smaller circle is drawn on top
    LIGHT_CIRCLES = {
        LightingStatus.TWILIGHT: ((135, 150),),
        LightingStatus.TORCHLIGHT: ((370, 200), (345, 150), (320, 100), (295, 50), (270, 0)),
    }

    def __init__(self, screen: pygame.Surface, game_surface_position: list[int], size: tuple[int, int]) -> None:
        """
        Create the darkness surface once; it is reused in every frame.

        :param screen: main display surface the darkness is drawn on (over the already blitted game surface)
        :param game_surface_position: position of the game surface on the screen
        :param size: size of the visible part of the game surface
        """
        self._screen = screen
        self._game_surface_position = game_surface_position
        self._dark_surface = pygame.Surface(size, pygame.SRCALPHA)

    def draw(self, lighting_status: LightingStatus, light_center: tuple[float, float]) -> None:
        """
        Draw the darkness on the screen. Nothing is drawn when the light is on.

        :param lighting_status: current lighting status
        :param light_center: center of the lit circle on the game surface (the player)
        """
        if lighting_status == LightingStatus.LIGHT_ON:
            return

        self._dark_surface.fill((0, 0, 0))
        for radius, alpha in self.LIGHT_CIRCLES[lighting_status]:
            pygame.draw.circle(self._dark_surface, (0, 0, 0, alpha), light_center,
                               GameHelper.multiply_by_tile_size_ratio(radius))

        self._screen.blit(self._dark_surface, self._game_surface_position)
