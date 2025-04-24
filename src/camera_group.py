import pygame

from settings import Settings
from src.sprite.bat_enemy import BatEnemy
from src.sprite.custom_draw_sprite import CustomDrawSprite
from src.sprite.monster_enemy import MonsterEnemy
from src.sprite.octopus_enemy import OctopusEnemy
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

    def set_map_offset(self, player):
        if player is None:
            return

        if self.map_width > self.game_surface_width:
            if player.rect.centerx < self.game_surface_half_width:
                self.offset.x = 0
            elif self.map_width - player.rect.centerx < self.game_surface_half_width:
                self.offset.x = self.game_surface.get_size()[0] - self.map_width
            else:
                self.offset.x = self.game_surface_half_width - player.rect.centerx

        if self.map_height > self.game_surface_height:
            if player.rect.centery < self.game_surface_half_height:
                self.offset.y = 0
            elif self.map_height - player.rect.centery < self.game_surface_half_height:
                self.offset.y = self.game_surface.get_size()[1] - self.map_height
            else:
                self.offset.y = self.game_surface_half_height - player.rect.centery

    def get_map_offset(self):
        return self.offset

    def custom_draw(self, player):
        # Calculate map offset
        self.set_map_offset(player)

        # Draw each tile with an offset on game_surface
        for sprite in self.sprites():
            if isinstance(sprite, CustomDrawSprite):
                sprite.custom_draw(self.game_surface, self.offset)
            else:
                offset_position = sprite.rect.topleft + self.offset
                self.game_surface.blit(sprite.image, offset_position)

            # Draw grid
            if self.debugger.enabled:
                self.draw_grid(sprite)

    def draw_grid(self, sprite):
        # Draw grid for each tile that uses CameraGroup class for rendering
        new_rect = pygame.rect.Rect(sprite.rect)
        new_rect.topleft += self.offset
        pygame.draw.rect(self.game_surface, self.debugger.main_grid_color, new_rect, 1)

        # Draw a path from the player to monster, bat or octopus enemy
        if isinstance(sprite, MonsterEnemy) or isinstance(sprite, OctopusEnemy) or isinstance(sprite, BatEnemy):
            if sprite.path:
                for path_item in sprite.path:
                    new_rect = pygame.rect.Rect(path_item[0] * Settings.TILE_SIZE,
                                                path_item[1] * Settings.TILE_SIZE,
                                                Settings.TILE_SIZE, Settings.TILE_SIZE)
                    new_rect.topleft += self.offset
                    pygame.draw.rect(self.game_surface, self.debugger.path_color, new_rect, 2)
