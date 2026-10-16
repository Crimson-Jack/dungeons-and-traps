import pygame

from src.enums.lighting_status import LightingStatus


class DarknessEffect:
    """Covers the game surface with darkness, leaving a lit circle around the player."""

    # Circles of light for each darkness status: (radius, alpha), from the largest circle to the smallest,
    # so each smaller circle is drawn on top
    LIGHT_CIRCLES = {
        LightingStatus.TWILIGHT: ((100, 150),),
        LightingStatus.TORCHLIGHT: ((280, 200), (260, 150), (240, 100), (220, 50), (200, 0)),
    }

    def __init__(self, size: tuple[int, int]) -> None:
        """
        Create the darkness surface once; it is reused in every frame.

        :param size: size of the visible part of the game surface
        """
        self._dark_surface = pygame.Surface(size, pygame.SRCALPHA)

    def draw(self, screen: pygame.Surface, position: list[int], lighting_status: LightingStatus,
             light_center: tuple[float, float]) -> None:
        """
        Draw the darkness on the screen. Nothing is drawn when the light is on.

        :param screen: main display surface
        :param position: position of the game surface on the screen
        :param lighting_status: current lighting status
        :param light_center: center of the lit circle on the game surface (the player)
        """
        if lighting_status == LightingStatus.LIGHT_ON:
            return

        self._dark_surface.fill((0, 0, 0))
        for radius, alpha in self.LIGHT_CIRCLES[lighting_status]:
            pygame.draw.circle(self._dark_surface, (0, 0, 0, alpha), light_center, radius)

        screen.blit(self._dark_surface, position)
