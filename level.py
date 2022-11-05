import pygame
import settings
import game_helper
from pytmx.util_pygame import load_pygame
from wall import Wall
from ground import Ground
from diamond import Diamond
from spider_enemy import SpiderEnemy
from ghost_enemy import GhostEnemy
from player import Player
from camera_group import CameraGroup
from camera_group_with_y_sort import CameraGroupWithYSort


class Level:
    def __init__(self, screen, game_surface, game_state):
        # Set screen and game_surface
        self.screen = screen
        self.game_surface = game_surface

        # Load tmx data - world map
        self.tmx_data = load_pygame('data/tmx/basic.tmx')
        size_of_map = (self.tmx_data.width, self.tmx_data.height)

        # Set up visible groups
        self.bottom_layer_background_sprites = CameraGroup(game_surface, size_of_map)
        self.middle_layer_regular_sprites = CameraGroupWithYSort(game_surface, size_of_map)
        self.top_layer_enemy_sprites = CameraGroup(game_surface, size_of_map)

        # Set up functional groups
        self.obstacle_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()

        # Set game state
        self.game_state = game_state

        # Set obstacle map
        self.obstacle_map = self.tmx_data.get_layer_by_name('obstacle').data

        # Create sprites
        self.create_sprites()

        # Get player
        self.player = self.get_player()

    def get_player(self):
        player_object = self.tmx_data.get_object_by_name('player')

        if player_object.visible:
            tile_x = int(player_object.x // self.tmx_data.tilewidth)
            tile_y = int(player_object.y // self.tmx_data.tileheight)
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE

            if player_object.properties.get('speed') is None:
                # Default player speed
                speed = game_helper.calculate_ratio(7)
            else:
                speed = game_helper.calculate_ratio(player_object.properties.get('speed'))

            # Add player to visible group
            return Player(player_object.image, (x, y), [self.middle_layer_regular_sprites], speed, self.obstacle_sprites,
                          self.collectable_sprites,
                          self.top_layer_enemy_sprites, self.game_state)

    def create_sprites(self):
        ground_layer = self.tmx_data.get_layer_by_name('ground')
        for tile_x, tile_y, image in ground_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to background sprites group
            Ground(image, (x, y), [self.bottom_layer_background_sprites])

        obstacle_layer = self.tmx_data.get_layer_by_name('obstacle')
        for tile_x, tile_y, image in obstacle_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to visible and obstacle sprites group
            Wall(image, (x, y), [self.middle_layer_regular_sprites, self.obstacle_sprites])

        collectable_diamond_layer = self.tmx_data.get_layer_by_name('collectable-diamond')
        for tile_x, tile_y, image in collectable_diamond_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to visible and collectable sprites group
            Diamond(image, (x, y), [self.middle_layer_regular_sprites, self.collectable_sprites])

        enemy_spider_layer = self.tmx_data.get_layer_by_name('enemy-spider')
        for enemy_spider in enemy_spider_layer:
            if enemy_spider.visible:
                tile_x = int(enemy_spider.x // self.tmx_data.tilewidth)
                tile_y = int(enemy_spider.y // self.tmx_data.tileheight)
                x = tile_x * settings.TILE_SIZE
                y = tile_y * settings.TILE_SIZE

                if enemy_spider.properties.get('speed') is None:
                    speed = game_helper.calculate_ratio(enemy_spider_layer.properties.get('speed'))
                else:
                    speed = game_helper.calculate_ratio(enemy_spider.properties.get('speed'))

                if enemy_spider.properties.get('net_length') is None:
                    net_length = enemy_spider_layer.properties.get('net_length')
                else:
                    net_length = enemy_spider.properties.get('net_length')

                SpiderEnemy(enemy_spider.image, (x, y), [self.top_layer_enemy_sprites], speed, net_length)

        enemy_ghost_layer = self.tmx_data.get_layer_by_name('enemy-ghost')
        for enemy_ghost in enemy_ghost_layer:
            if enemy_ghost.visible:
                tile_x = int(enemy_ghost.x // self.tmx_data.tilewidth)
                tile_y = int(enemy_ghost.y // self.tmx_data.tileheight)
                x = tile_x * settings.TILE_SIZE
                y = tile_y * settings.TILE_SIZE

                if enemy_ghost.properties.get('speed') is None:
                    speed = game_helper.calculate_ratio(enemy_ghost_layer.properties.get('speed'))
                else:
                    speed = game_helper.calculate_ratio(enemy_ghost.properties.get('speed'))

                GhostEnemy(enemy_ghost.image, (x, y), [self.top_layer_enemy_sprites], speed, self.obstacle_map, (tile_x, tile_y))

    def run(self):
        # Run an update method foreach sprite from the group
        self.middle_layer_regular_sprites.update()
        self.top_layer_enemy_sprites.update()

        # Draw all visible sprites
        self.bottom_layer_background_sprites.custom_draw(self.player)
        self.middle_layer_regular_sprites.custom_draw(self.player)
        self.top_layer_enemy_sprites.custom_draw(self.player)

        # Blit game_surface on the main screen
        self.screen.blit(self.game_surface, (0, 0))

        # Read inputs and display variables if debugger is enabled
        settings.debugger.input()
        settings.debugger.show()

    def game_over(self):
        half_width = self.screen.get_size()[0] // 2
        half_height = self.screen.get_size()[1] // 2

        accent_color = (255, 255, 255)
        background_color = (100, 100, 100)
        basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 50)

        game_over = basic_font.render('GAME OVER', True, accent_color, background_color)
        game_over_size = game_over.get_size()
        self.screen.blit(game_over, (half_width - game_over_size[0] // 2, half_height - game_over_size[1] // 2))
