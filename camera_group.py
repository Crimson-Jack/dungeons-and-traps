import pygame
import custom_draw_sprite
import settings
import monster_enemy


class CameraGroup(pygame.sprite.Group):
    def __init__(self, game_surface, size_of_map):
        super().__init__()
        self.game_surface = game_surface
        self.half_width = self.game_surface.get_size()[0] // 2
        self.half_height = self.game_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self.size_of_map = size_of_map

    def set_map_offset(self, player):
        # The maximum width (x) for the whole map
        max_width = settings.TILE_SIZE * self.size_of_map[0]
        # The maximum height (y) for the whole map
        max_height = settings.TILE_SIZE * self.size_of_map[1]

        if player.rect.centerx < self.half_width:
            self.offset.x = 0
        elif max_width - player.rect.centerx < self.half_width:
            self.offset.y = self.game_surface.get_size()[0] - max_width
        else:
            self.offset.x = self.half_width - player.rect.centerx

        if player.rect.centery < self.half_height:
            self.offset.y = 0
        elif max_height - player.rect.centery < self.half_height:
            self.offset.y = self.game_surface.get_size()[1] - max_height
        else:
            self.offset.y = self.half_height - player.rect.centery

    def get_map_offset(self):
        return self.offset

    def custom_draw(self, player):
        # Calculate map offset
        self.set_map_offset(player)

        # Draw each tile with an offset on game_surface
        for sprite in self.sprites():
            if isinstance(sprite, custom_draw_sprite.CustomDrawSprite):
                sprite.custom_draw(self.game_surface, self.offset)
            else:
                offset_position = sprite.rect.topleft + self.offset
                self.game_surface.blit(sprite.image, offset_position)

            # Draw rectangles when debug is enabled
            if settings.debugger.enabled:
                new_rect = pygame.rect.Rect(sprite.rect)
                new_rect.topleft += self.offset
                pygame.draw.rect(self.game_surface, settings.debugger.text_color, new_rect, 1)

                # Draw a path from the player to monster enemy
                if isinstance(sprite, monster_enemy.MonsterEnemy):
                    if sprite.path:
                        for path_item in sprite.path:
                            new_rect = pygame.rect.Rect(path_item[0] * settings.TILE_SIZE, path_item[1] * settings.TILE_SIZE,
                                                        settings.TILE_SIZE, settings.TILE_SIZE)
                            new_rect.topleft += self.offset
                            pygame.draw.rect(self.game_surface, (0, 255, 255), new_rect, 2)
