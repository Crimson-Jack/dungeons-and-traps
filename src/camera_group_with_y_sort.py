import pygame
from src.sprite.custom_draw_sprite import CustomDrawSprite
import game_helper
import settings
from src.sprite.player import Player
from src.camera_group import CameraGroup


class CameraGroupWithYSort(CameraGroup):
    def __init__(self, game_surface, size_of_map):
        super().__init__(game_surface, size_of_map)

    def custom_draw(self, player):
        # Calculate map offset
        super().set_map_offset(player)

        # Draw each tile with an offset on game_surface keeping Y order
        for sprite in sorted(self.sprites(), key=lambda item: item.rect.centery):
            if isinstance(sprite, CustomDrawSprite):
                sprite.custom_draw(self.game_surface, self.offset)
            else:
                offset_position = sprite.rect.topleft + self.offset
                self.game_surface.blit(sprite.image, offset_position)

            # Draw rectangles when debug is enabled
            if settings.debugger.enabled:
                new_rect = pygame.rect.Rect(sprite.rect)
                new_rect.topleft += self.offset
                pygame.draw.rect(self.game_surface, settings.debugger.text_color, new_rect, 1)

                # Draw a tile where the player exists
                if isinstance(sprite, Player):
                    x_tile, y_tile = game_helper.get_tile_by_point(sprite.get_center_point())
                    new_rect = pygame.rect.Rect(x_tile*settings.TILE_SIZE, y_tile*settings.TILE_SIZE, settings.TILE_SIZE, settings.TILE_SIZE)
                    new_rect.topleft += self.offset
                    pygame.draw.rect(self.game_surface, settings.debugger.text_color, new_rect, 3)
