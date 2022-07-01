import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug

class Level:
    def __init__(self):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()
        # Sprite group set up
        self.visible_sprites = YSortCameraGroup()
        self.obstactle_sprites = pygame.sprite.Group()

        self.create_map()

    def create_map(self):
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE
                if col == 'x':
                    # Add tile to visible and obstacle sprites group
                    Tile((x, y), [self.visible_sprites, self.obstactle_sprites])
                if col == 'p':
                    # Add player to visible group
                    self.player = Player((x, y), [self.visible_sprites], self.obstactle_sprites)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):

        max_width = TILESIZE * len(WORLD_MAP[0])
        max_height = TILESIZE * len(WORLD_MAP)

        debug(self.half_width, 10, 10)
        debug(self.half_height, 10, 30)
        debug(str.format('{} {}', player.rect.left, player.rect.right), 10, 50)
        debug(max_width, 10, 70)
        debug(max_height, 10, 90)
        debug(max_width - player.rect.centerx, 10, 110)
        debug(max_height - player.rect.centery, 10, 130)

        if player.rect.centerx < self.half_width or max_width - player.rect.centerx < self.half_width:
            debug('YES', 10, 150)
        else:
            debug('NO', 10, 150)
            self.offset.x = self.half_width - player.rect.centerx

        if player.rect.centery < self.half_height or max_height - player.rect.centery < self.half_height:
            debug('YES', 10, 170)
        else:
            debug('NO', 10, 170)
            self.offset.y = self.half_height - player.rect.centery

        #self.offset.x = self.half_width - player.rect.centerx
        #self.offset.y = self.half_height - player.rect.centery

        for sprite in self.sprites():
            offset_position = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_position)

        debug(self.offset, 10, 190)

