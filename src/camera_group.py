import pygame

from settings import Settings
from src.sprites.custom_draw_sprite import CustomDrawSprite


class CameraGroup(pygame.sprite.Group):
    """Sprite group drawn on the game surface with a camera that follows the player; only sprites in view are drawn."""

    def __init__(self, game_surface: pygame.Surface, size_of_map: tuple[int, int]) -> None:
        """
        Prepare the camera for a map of the given size shown on the game surface.

        :param game_surface: surface the sprites are drawn on
        :param size_of_map: map size in tiles
        """
        super().__init__()
        self._game_surface = game_surface
        self._game_surface_width, self._game_surface_height = self._game_surface.get_size()
        self._game_surface_half_width = self._game_surface_width // 2
        self._game_surface_half_height = self._game_surface_height // 2
        self._offset = pygame.math.Vector2()
        self._map_width = Settings.TILE_SIZE * size_of_map[0]
        self._map_height = Settings.TILE_SIZE * size_of_map[1]

    def get_map_offset(self) -> pygame.math.Vector2:
        """Return the offset that moves map coordinates to game surface coordinates."""
        return self._offset

    def custom_draw(self, camera_target: tuple[int, int],
                    additional_offset: pygame.math.Vector2 | None = None) -> None:
        """
        Move the camera to the target and draw the visible sprites on the game surface.

        :param camera_target: point on the map the camera keeps in the center, e.g. the center of the player
        :param additional_offset: offset added for this frame only, e.g. the tilt effect
        """
        # Calculate map offset
        self._set_map_offset(camera_target)

        # Add additional offset
        if additional_offset is not None:
            self._offset += additional_offset

        # Draw each visible tile with an offset on game_surface
        for sprite in self._get_visible_sprites():
            if isinstance(sprite, CustomDrawSprite):
                sprite.custom_draw(self._game_surface, self._offset)
            else:
                sprite_image = sprite.image
                sprite_rect = sprite.rect
                if sprite_image is not None and sprite_rect is not None:
                    offset_position = sprite_rect.topleft + self._offset
                    self._game_surface.blit(sprite_image, offset_position)

        # Remove additional offset
        if additional_offset is not None:
            self._offset -= additional_offset

    def _set_map_offset(self, camera_target: tuple[int, int]) -> None:
        # Offset shifts map coordinates to game_surface coordinates so that the camera target stays centered
        target_x, target_y = camera_target

        # Scroll horizontally only when the map is wider than game_surface
        if self._map_width > self._game_surface_width:
            # Target near the left edge of the map - keep the map aligned to the left
            if target_x < self._game_surface_half_width:
                self._offset.x = 0
            # Target near the right edge of the map - keep the map aligned to the right
            elif self._map_width - target_x < self._game_surface_half_width:
                self._offset.x = self._game_surface_width - self._map_width
            # Otherwise center the view on the target
            else:
                self._offset.x = self._game_surface_half_width - target_x

        # Scroll vertically only when the map is taller than game_surface
        if self._map_height > self._game_surface_height:
            # Target near the top edge of the map - keep the map aligned to the top
            if target_y < self._game_surface_half_height:
                self._offset.y = 0
            # Target near the bottom edge of the map - keep the map aligned to the bottom
            elif self._map_height - target_y < self._game_surface_half_height:
                self._offset.y = self._game_surface_height - self._map_height
            # Otherwise center the view on the target
            else:
                self._offset.y = self._game_surface_half_height - target_y

    def _get_visible_sprites(self) -> list[pygame.sprite.Sprite]:
        # The map area currently shown on game_surface, including any additional offset
        visible_rect = pygame.rect.Rect(-self._offset.x, -self._offset.y,
                                        self._game_surface_width, self._game_surface_height)

        # Keep only sprites whose drawn area overlaps the visible map area
        visible_sprites = []
        for sprite in self.sprites():
            culling_rect = self._get_sprite_culling_rect(sprite)
            if culling_rect is not None and visible_rect.colliderect(culling_rect):
                visible_sprites.append(sprite)

        return visible_sprites

    @staticmethod
    def _get_sprite_culling_rect(sprite: pygame.sprite.Sprite) -> pygame.Rect | pygame.FRect | None:
        # Area of the map the sprite draws on; larger than the sprite for custom drawn sprites
        if isinstance(sprite, CustomDrawSprite):
            return sprite.get_culling_rect()
        return sprite.rect
