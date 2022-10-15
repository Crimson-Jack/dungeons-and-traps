import pygame
import settings
from pytmx.util_pygame import load_pygame
from wall import Wall
from ground import Ground
from diamond import Diamond
from spider_enemy import SpiderEnemy
from ghost_enemy import GhostEnemy
from player import Player
from camera_group import CameraGroup
from y_sort_camera_group import YSortCameraGroup


class Level:
    def __init__(self, screen, game_surface, game_state):
        # Set screen and game_surface
        self.screen = screen
        self.game_surface = game_surface

        # Load tmx data - world map
        self.tmx_data = load_pygame('data/tmx/basic.tmx')
        size_of_map = (self.tmx_data.width, self.tmx_data.height)

        # Set up sprite groups
        self.background_sprites = CameraGroup(game_surface, size_of_map)
        self.visible_sprites = YSortCameraGroup(game_surface, size_of_map)
        self.enemy_sprites = CameraGroup(game_surface, size_of_map)
        self.obstacle_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()

        # Set game state
        self.game_state = game_state

        # Set obstacle map
        self.obstacle_map = self.get_obstacle_map()

        # Create sprites
        self.create_sprites()

        # Create player
        self.create_player()

    def create_player(self):
        player_layer = self.tmx_data.get_layer_by_name('player')
        for tile_x, tile_y, image in player_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add player to visible group
            self.player = Player(image, (x, y), [self.visible_sprites], self.obstacle_sprites, self.collectable_sprites,
                            self.enemy_sprites, self.game_state)

    def create_sprites(self):
        ground_layer = self.tmx_data.get_layer_by_name('ground')
        for tile_x, tile_y, image in ground_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to background sprites group
            Ground(image, (x, y), [self.background_sprites])

        obstacles_layer = self.tmx_data.get_layer_by_name('obstacle')
        for tile_x, tile_y, image in obstacles_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to visible and obstacle sprites group
            Wall(image, (x, y), [self.visible_sprites, self.obstacle_sprites])

        collectables_diamond_layer = self.tmx_data.get_layer_by_name('collectable-diamond')
        for tile_x, tile_y, image in collectables_diamond_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to visible and collectable sprites group
            Diamond(image, (x, y), [self.visible_sprites, self.collectable_sprites])

        enemies_spider_layer = self.tmx_data.get_layer_by_name('enemy-spider')
        enemies_spider_speed = enemies_spider_layer.properties['speed']
        enemies_spider_net_length = enemies_spider_layer.properties['net_length']
        for tile_x, tile_y, image in enemies_spider_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to enemy sprites group
            SpiderEnemy(image, (x, y), [self.enemy_sprites], enemies_spider_speed, enemies_spider_net_length)

        enemies_ghost_layer = self.tmx_data.get_layer_by_name('enemy-ghost')
        enemies_ghost_speed = enemies_ghost_layer.properties['speed']
        for tile_x, tile_y, image in enemies_ghost_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to enemy sprites group
            GhostEnemy(image, (x, y), [self.enemy_sprites], enemies_ghost_speed, self.obstacle_map, (tile_x, tile_y))

    def get_obstacle_map(self):
        obstacles_layer = self.tmx_data.get_layer_by_name('obstacle')
        return obstacles_layer.data

    def run(self):
        # Run Update method foreach sprite from the group
        self.visible_sprites.update()
        self.enemy_sprites.update()

        # Draw all visible sprites
        self.background_sprites.custom_draw(self.player)
        self.visible_sprites.custom_draw(self.player)
        self.enemy_sprites.custom_draw(self.player)

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
