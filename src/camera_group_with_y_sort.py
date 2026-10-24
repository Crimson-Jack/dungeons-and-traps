import pygame

from src.camera_group import CameraGroup


class CameraGroupWithYSort(CameraGroup):
    """Camera group that draws sprites in the order of their y position, so lower sprites cover higher ones."""

    def _get_visible_sprites(self) -> list[pygame.sprite.Sprite]:
        # Visible sprites sorted by the y position of their centers for the depth effect
        return sorted(super()._get_visible_sprites(), key=lambda item: item.rect.centery)
