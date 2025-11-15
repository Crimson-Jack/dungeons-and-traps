import pygame

from settings import Settings
from src.camera_group import CameraGroup
from src.game_helper import GameHelper
from src.sprites.custom_draw_sprite import CustomDrawSprite
from src.sprites.player import Player


class CameraGroupWithYSort(CameraGroup):
    def __init__(self, game_surface, size_of_map):
        super().__init__(game_surface, size_of_map)

    def custom_draw(self, player, additional_offset = None):
        # Calculate map offset
        super().set_map_offset(player)
        # Add additional offset
        if additional_offset is not None:
            self.offset += additional_offset

        # Draw each tile with an offset on game_surface keeping Y order
        for sprite in sorted(self.sprites(), key=lambda item: item.rect.centery):
            if isinstance(sprite, CustomDrawSprite):
                sprite.custom_draw(self.game_surface, self.offset)
            else:
                offset_position = sprite.rect.topleft + self.offset
                self.game_surface.blit(sprite.image, offset_position)

            # Draw grid
            if self.debugger.enabled:
                self.draw_grid(sprite)

    def draw_grid(self, sprite):
        # Draw grid for each tile that uses CameraGroupWithYSort class for rendering
        new_rect = pygame.rect.Rect(sprite.rect)
        new_rect.topleft += self.offset
        pygame.draw.rect(self.game_surface, self.debugger.alternative_grid_color, new_rect, 1)

        # Draw a tile where the player exists
        if isinstance(sprite, Player):
            x_tile, y_tile = GameHelper.get_tile_by_point(sprite.get_center_point())
            new_rect = pygame.rect.Rect(x_tile * Settings.TILE_SIZE, y_tile * Settings.TILE_SIZE, Settings.TILE_SIZE,
                                        Settings.TILE_SIZE)
            new_rect.topleft += self.offset
            pygame.draw.rect(self.game_surface, self.debugger.text_color, new_rect, 3)
