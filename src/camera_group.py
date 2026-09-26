import pygame

from settings import Settings
from src.sprites.bat_enemy import BatEnemy
from src.sprites.custom_draw_sprite import CustomDrawSprite
from src.sprites.monster_enemy import MonsterEnemy
from src.sprites.octopus_enemy import OctopusEnemy
from src.utilities.debug import Debug


class CameraGroup(pygame.sprite.Group):
    def __init__(self, game_surface, size_of_map):
        super().__init__()
        self.game_surface = game_surface
        self.game_surface_width = self.game_surface.get_size()[0]
        self.game_surface_height = self.game_surface.get_size()[1]
        self.game_surface_half_width = self.game_surface_width // 2
        self.game_surface_half_height = self.game_surface_height // 2
        self.offset = pygame.math.Vector2()
        self.size_of_map = size_of_map
        self.map_width = Settings.TILE_SIZE * self.size_of_map[0]
        self.map_height = Settings.TILE_SIZE * self.size_of_map[1]

        # Create debugger
        self.debugger = Debug()

    def _set_map_offset(self, player):
        # Offset shifts map coordinates to game_surface coordinates so that the player stays centered
        if player is None:
            return

        # Scroll horizontally only when the map is wider than game_surface
        if self.map_width > self.game_surface_width:
            # Player near the left edge of the map - keep the map aligned to the left
            if player.rect.centerx < self.game_surface_half_width:
                self.offset.x = 0
            # Player near the right edge of the map - keep the map aligned to the right
            elif self.map_width - player.rect.centerx < self.game_surface_half_width:
                self.offset.x = self.game_surface.get_size()[0] - self.map_width
            # Otherwise center the view on the player
            else:
                self.offset.x = self.game_surface_half_width - player.rect.centerx

        # Scroll vertically only when the map is taller than game_surface
        if self.map_height > self.game_surface_height:
            # Player near the top edge of the map - keep the map aligned to the top
            if player.rect.centery < self.game_surface_half_height:
                self.offset.y = 0
            # Player near the bottom edge of the map - keep the map aligned to the bottom
            elif self.map_height - player.rect.centery < self.game_surface_half_height:
                self.offset.y = self.game_surface.get_size()[1] - self.map_height
            # Otherwise center the view on the player
            else:
                self.offset.y = self.game_surface_half_height - player.rect.centery

    def get_map_offset(self):
        return self.offset

    def custom_draw(self, player, additional_offset = None):
        # Calculate map offset
        self._set_map_offset(player)

        # Add additional offset
        if additional_offset is not None:
            self.offset += additional_offset

        # Draw each visible tile with an offset on game_surface
        for sprite in self._get_visible_sprites():
            if isinstance(sprite, CustomDrawSprite):
                sprite.custom_draw(self.game_surface, self.offset)
            else:
                offset_position = sprite.rect.topleft + self.offset
                self.game_surface.blit(sprite.image, offset_position)

            # Draw grid
            if self.debugger.enabled:
                self._draw_grid(sprite)

        # Remove additional offset
        if additional_offset is not None:
            self.offset -= additional_offset

    def _get_visible_sprites(self):
        # Debug overlay draws pathfinding paths far beyond the sprite rectangle, so culling is disabled
        if self.debugger.enabled:
            return self.sprites()

        # The map area currently shown on game_surface, including any additional offset
        visible_rect = pygame.rect.Rect(-self.offset.x, -self.offset.y,
                                        self.game_surface_width, self.game_surface_height)

        # Keep only sprites whose drawn area overlaps the visible map area
        visible_sprites = []
        for sprite in self.sprites():
            culling_rect = self._get_sprite_culling_rect(sprite)
            if visible_rect.colliderect(culling_rect):
                visible_sprites.append(sprite)

        return visible_sprites

    @staticmethod
    def _get_sprite_culling_rect(sprite):
        if isinstance(sprite, CustomDrawSprite):
            return sprite.get_culling_rect()
        return sprite.rect

    def _draw_grid(self, sprite):
        # Draw grid for each tile that uses CameraGroup class for rendering
        new_rect = pygame.rect.Rect(sprite.rect)
        new_rect.topleft += self.offset
        pygame.draw.rect(self.game_surface, self.debugger.main_grid_color, new_rect, 1)

        # Draw a path from the player to monster, bat or octopus enemy
        if isinstance(sprite, MonsterEnemy) or isinstance(sprite, OctopusEnemy) or isinstance(sprite, BatEnemy):
            if sprite.current_position_on_map:
                new_rect = pygame.rect.Rect(sprite.current_position_on_map[0] * Settings.TILE_SIZE,
                                            sprite.current_position_on_map[1] * Settings.TILE_SIZE,
                                            Settings.TILE_SIZE, Settings.TILE_SIZE)
                new_rect.topleft += self.offset
                pygame.draw.rect(self.game_surface, self.debugger.path_color, new_rect, 6)
            if sprite.path:
                for path_item in sprite.path:
                    new_rect = pygame.rect.Rect(path_item[0] * Settings.TILE_SIZE,
                                                path_item[1] * Settings.TILE_SIZE,
                                                Settings.TILE_SIZE, Settings.TILE_SIZE)
                    new_rect.topleft += self.offset
                    pygame.draw.rect(self.game_surface, self.debugger.path_color, new_rect, 2)
