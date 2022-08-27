import pygame
import settings
from wall import Wall
from ground import Ground
from diamond import Diamond
from player import Player


class Level:
    def __init__(self, screen, game_surface):
        # Set up sprite groups
        self.background_sprites = CameraGroup(screen, game_surface)
        self.visible_sprites = YSortCameraGroup(screen, game_surface)
        self.obstacle_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()

        # Build the map
        self.create_map()

    def create_map(self):
        for row_index, row in enumerate(settings.WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * settings.TILE_SIZE
                y = row_index * settings.TILE_SIZE
                if col == 'x':
                    # Add tile to visible and obstacle sprites group
                    Wall((x, y), [self.visible_sprites, self.obstacle_sprites])
                if col == 'g':
                    # Add tile to background sprites group
                    Ground((x, y), [self.background_sprites])
                if col == 'd':
                    # Add tile to visible and collectable sprites group
                    Diamond((x, y), [self.visible_sprites, self.collectable_sprites])
                if col == 'p':
                    # Add player to visible group
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites, self.collectable_sprites)

    def run(self):
        # Draw all visible sprites
        self.background_sprites.custom_draw(self.player)
        self.visible_sprites.custom_draw(self.player)

        # Read inputs and display variables if debugger is enabled
        settings.debugger.input()
        settings.debugger.show()

        # Run Update method foreach sprite from the group
        self.visible_sprites.update()


class CameraGroup(pygame.sprite.Group):
    def __init__(self, screen, game_surface):
        super().__init__()

        self.screen = screen
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

        # Draw each tile with an offset on game_surface
        for sprite in self.sprites():
            offset_position = sprite.rect.topleft + self.offset
            self.game_surface.blit(sprite.image, offset_position)

        self.screen.blit(self.game_surface, (0,0))

class YSortCameraGroup(CameraGroup):
    def __init__(self, screen, game_surface):
        super().__init__(screen, game_surface)

    def custom_draw(self, player):
        # Calculate map offset
        super().set_map_offset(player)

        # Draw each tile with an offset on game_surface keeping Y order
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft + self.offset
            self.game_surface.blit(sprite.image, offset_position)

        self.screen.blit(self.game_surface, (0, 0))