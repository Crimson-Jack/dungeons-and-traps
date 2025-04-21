import pygame

class SpriteCostume:
    def __init__(self, image: pygame.Surface, number_of_frames: int):
        self._image = image
        self._number_of_frames = number_of_frames

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @image.setter
    def image(self, value: pygame.Surface):
        self._image = value

    @property
    def number_of_frames(self) -> int:
        return self._number_of_frames
