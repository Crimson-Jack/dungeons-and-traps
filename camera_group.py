import pygame
import custom_draw_sprite
import settings


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

        if player.rect.centerx < self.half_width or max_width - player.rect.centerx < self.half_width:
            pass
        else:
            self.offset.x = self.half_width - player.rect.centerx

        if player.rect.centery < self.half_height or max_height - player.rect.centery < self.half_height:
            pass
        else:
            self.offset.y = self.half_height - player.rect.centery

    def custom_draw_each_sprite(self):
        # Draw extra effects for enemies
        for sprite in self.sprites():
            if isinstance(sprite, custom_draw_sprite.CustomDrawSprite):
                sprite.custom_draw(self.game_surface, self.offset)

    def custom_draw(self, player):
        # Calculate map offset
        self.set_map_offset(player)

        # Custom draw of each sprite
        self.custom_draw_each_sprite()

        # Draw each tile with an offset on game_surface
        for sprite in self.sprites():
            offset_position = sprite.rect.topleft + self.offset
            self.game_surface.blit(sprite.image, offset_position)

            # Draw rectangles when debug is enabled
            if settings.debugger.enabled:
                new_rect = pygame.rect.Rect(sprite.rect)
                new_rect.topleft += self.offset
                pygame.draw.rect(self.game_surface, settings.debugger.text_color, new_rect, 1)