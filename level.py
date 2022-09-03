import pygame
import settings
from wall import Wall
from ground import Ground
from diamond import Diamond
from spider_enemy import SpiderEnemy
from player import Player
from camera_group import CameraGroup
from y_sort_camera_group import YSortCameraGroup


class Level:
    def __init__(self, screen, game_surface, game_state):
        # Set screen and game_surface
        self.screen = screen
        self.game_surface = game_surface

        # Set up sprite groups
        self.background_sprites = CameraGroup(game_surface)
        self.visible_sprites = YSortCameraGroup(game_surface)
        self.enemy_sprites = CameraGroup(game_surface)
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
                if col.find('s') >= 0:
                    # TODO: Improve parsing process
                    # Add tile to enemy sprites group
                    SpiderEnemy((x, y), [self.enemy_sprites], int(col[1]), int(col[2]))
                if col == 'p':
                    # Add player to visible group
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites, self.collectable_sprites, self.enemy_sprites, self.game_state)

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
        basic_font = pygame.font.Font('freesansbold.ttf', 50)

        game_over = basic_font.render('GAME OVER', True, accent_color, background_color)
        game_over_size = game_over.get_size()
        self.screen.blit(game_over, (half_width - game_over_size[0] // 2, half_height - game_over_size[1] // 2))
