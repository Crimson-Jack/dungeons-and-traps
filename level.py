import pygame
import settings
from wall import Wall
from player import Player


class Level:
    def __init__(self):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()
        # Sprite group set up
        self.visible_sprites = YSortCameraGroup()
        self.obstactle_sprites = pygame.sprite.Group()
        # Build the map
        self.create_map()

    def create_map(self):
        for row_index, row in enumerate(settings.WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * settings.TILE_SIZE
                y = row_index * settings.TILE_SIZE
                if col == 'x':
                    # Add tile to visible and obstacle sprites group
                    Wall((x, y), [self.visible_sprites, self.obstactle_sprites])
                if col == 'p':
                    # Add player to visible group
                    self.player = Player((x, y), [self.visible_sprites], self.obstactle_sprites)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        #self.visible_sprites.draw(self.display_surface)
        settings.debugger.input()
        settings.debugger.show()
        self.visible_sprites.update()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):

        # The maximum width (x) for the whole map
        max_width = settings.TILE_SIZE * len(settings.WORLD_MAP[0])
        # The maximum height (y) for the whole map
        max_height = settings.TILE_SIZE * len(settings.WORLD_MAP)

        settings.debugger.add_info(f'1/2 window width = {self.half_width}')
        settings.debugger.add_info(f'1/2 window height = {self.half_height}')
        settings.debugger.add_info(f'Player left = {player.rect.left}, right = {player.rect.right}')
        settings.debugger.add_info(f'Player top = {player.rect.top}, bottom = {player.rect.bottom}')
        settings.debugger.add_info(f'Max map width = {max_width}')
        settings.debugger.add_info(f'Max map height = {max_height}')
        settings.debugger.add_info(f'Distance x left from player center = {max_width - player.rect.centerx}')
        settings.debugger.add_info(f'Distance y left from player center = {max_height - player.rect.centery}')

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

        #for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_position)

