import pygame

import settings
from camera_group import CameraGroup


class YSortCameraGroup(CameraGroup):
    def __init__(self, game_surface):
        super().__init__(game_surface)

    def custom_draw(self, player):
        # Calculate map offset
        super().set_map_offset(player)

        # Draw each tile with an offset on game_surface keeping Y order
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft + self.offset
            self.game_surface.blit(sprite.image, offset_position)

            # Draw rectangles when debug is enabled
            if settings.debugger.enabled:
                new_rect = pygame.rect.Rect(sprite.rect)
                new_rect.topleft += self.offset
                pygame.draw.rect(self.game_surface, (255, 255, 255), new_rect, 1)