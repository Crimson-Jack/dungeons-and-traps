import pygame

import enemy
import settings


class CameraGroup(pygame.sprite.Group):
    def __init__(self, game_surface):
        super().__init__()
        self.game_surface = game_surface
        self.half_width = self.game_surface.get_size()[0] // 2
        self.half_height = self.game_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def set_map_offset(self, player):
        # The maximum width (x) for the whole map
        max_width = settings.TILE_SIZE * len(settings.WORLD_MAP[0])
        # The maximum height (y) for the whole map
        max_height = settings.TILE_SIZE * len(settings.WORLD_MAP)

        if player.rect.centerx < self.half_width or max_width - player.rect.centerx < self.half_width:
            settings.debugger.add_info('Scroll in x: NO')
        else:
            settings.debugger.add_info(f'Scroll in x: YES, offset = {self.offset}')
            self.offset.x = self.half_width - player.rect.centerx

        if player.rect.centery < self.half_height or max_height - player.rect.centery < self.half_height:
            settings.debugger.add_info('Scroll in y: NO')
        else:
            settings.debugger.add_info(f'Scroll in y: YES, offset = {self.offset}')
            self.offset.y = self.half_height - player.rect.centery

    def custom_draw(self, player):
        # Calculate map offset
        self.set_map_offset(player)

        # Draw extra effects for enemies
        for sprite in self.sprites():
            if isinstance(sprite, enemy.Enemy):
                sprite.custom_draw(self.game_surface, self.offset)

        # Draw each tile with an offset on game_surface
        for sprite in self.sprites():
            offset_position = sprite.rect.topleft + self.offset
            self.game_surface.blit(sprite.image, offset_position)

