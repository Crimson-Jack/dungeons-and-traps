import pygame
import settings
from wall import Wall
from ground import Ground
from diamond import Diamond
from player import Player
from camera_group import CameraGroup
from y_sort_camera_group import YSortCameraGroup


class Level:
    def __init__(self, screen, game_surface, game_state):
        # Set up sprite groups
        self.background_sprites = CameraGroup(screen, game_surface)
        self.visible_sprites = YSortCameraGroup(screen, game_surface)
        self.obstacle_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()

        # Set game state
        self.game_state = game_state

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
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites, self.collectable_sprites, self.game_state)

    def run(self):
        # Run Update method foreach sprite from the group
        self.visible_sprites.update()

        # Draw all visible sprites
        self.background_sprites.custom_draw(self.player)
        self.visible_sprites.custom_draw(self.player)

        # Read inputs and display variables if debugger is enabled
        settings.debugger.input()
        settings.debugger.show()
