import pygame

import obstacle_map_refresh_sprite
import settings
import game_helper
from pytmx.util_pygame import load_pygame
from obstacle_map import ObstacleMap
from wall import Wall
from stone import Stone
from ground import Ground
from diamond import Diamond
from spider_enemy import SpiderEnemy
from ghost_enemy import GhostEnemy
from fire_flame_enemy_left import FireFlameEnemyLeft
from fire_flame_enemy_right import FireFlameEnemyRight
from player import Player
from exit_point import ExitPoint
from blast_effect import BlastEffect
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
        self.bottom_layer_regular_sprites = CameraGroup(game_surface, size_of_map)
        self.middle_layer_regular_sprites = CameraGroupWithYSort(game_surface, size_of_map)
        self.top_layer_sprites = CameraGroup(game_surface, size_of_map)

        # Set up functional groups
        self.exit_points = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.moving_obstacle_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.hostile_force_sprites = pygame.sprite.Group()

        # Set game state
        self.game_state = game_state

        # Create obstacle map and combine all layers with obstacles
        self.obstacle_map = ObstacleMap([
            self.tmx_data.get_layer_by_name('obstacle').data,
            self.tmx_data.get_layer_by_name('moving-obstacle').data
        ])

        # Create sprites
        self.create_sprites()
        # Create player
        self.player = self.create_player()
        # Create exit point
        self.exit_point = self.create_exit_point()

        # Complete required diamonds parameter based on current level data
        self.game_state.set_number_of_required_diamonds(len(self.collectable_sprites))

        # Set blast effect details
        self.blast_effect = BlastEffect(self.game_surface, self.game_surface.get_width(),
                                        self.game_surface.get_height(), 8, 'White')

    def create_player(self):
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
            return Player((x, y), [self.middle_layer_regular_sprites], [self.top_layer_sprites],
                          speed, self.exit_points, self.obstacle_sprites, self.moving_obstacle_sprites,
                          self.collectable_sprites, self.enemy_sprites, self.hostile_force_sprites,
                          self.game_state)

    def create_exit_point(self):
        exit_object = self.tmx_data.get_object_by_name('exit-point')

        if exit_object.visible:
            tile_x = int(exit_object.x // self.tmx_data.tilewidth)
            tile_y = int(exit_object.y // self.tmx_data.tileheight)
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE

            # Add exit point to visible group
            return ExitPoint(exit_object.image, (x, y), [self.bottom_layer_background_sprites, self.exit_points], False)

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

        moving_obstacle_layer = self.tmx_data.get_layer_by_name('moving-obstacle')
        for tile_x, tile_y, image in moving_obstacle_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Create collision sprites list for moving obstacles
            collision_sprites = [self.enemy_sprites, self.obstacle_sprites, self.moving_obstacle_sprites, self.collectable_sprites]
            # Add tile to visible and obstacle sprites group
            # Note: stone can be moved, so the list instead of tuple for position is used
            Stone(image, [x, y], [self.middle_layer_regular_sprites, self.moving_obstacle_sprites],
                  self.obstacle_map.items, collision_sprites, self.game_state)

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
                    speed = float(game_helper.calculate_ratio(enemy_spider_layer.properties.get('speed')))
                else:
                    speed = float(game_helper.calculate_ratio(enemy_spider.properties.get('speed')))

                if enemy_spider.properties.get('net_length') is None:
                    net_length = int(enemy_spider_layer.properties.get('net_length'))
                else:
                    net_length = int(enemy_spider.properties.get('net_length'))

                if enemy_spider.properties.get('motion_schedule') is None:
                    motion_schedule = enemy_spider_layer.properties.get('motion_schedule')
                else:
                    motion_schedule = enemy_spider.properties.get('motion_schedule')
                # Convert string to tuple
                motion_schedule = tuple(map(int, motion_schedule.split(',')))

                SpiderEnemy(enemy_spider.image, (x, y), [self.top_layer_sprites, self.enemy_sprites],
                            speed, net_length, motion_schedule, self.moving_obstacle_sprites)

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

                GhostEnemy(enemy_ghost.image, (x, y), [self.top_layer_sprites, self.enemy_sprites],
                           speed, self.obstacle_map.items)

        enemy_fire_flame_layer = self.tmx_data.get_layer_by_name('enemy-fire-flame')
        for enemy_fire_flame in enemy_fire_flame_layer:
            if enemy_fire_flame.visible:
                tile_x = int(enemy_fire_flame.x // self.tmx_data.tilewidth)
                tile_y = int(enemy_fire_flame.y // self.tmx_data.tileheight)
                x = tile_x * settings.TILE_SIZE
                y = tile_y * settings.TILE_SIZE

                if enemy_fire_flame.properties.get('speed') is None:
                    speed = float(game_helper.calculate_ratio(enemy_fire_flame_layer.properties.get('speed')))
                else:
                    speed = float(game_helper.calculate_ratio(enemy_fire_flame.properties.get('speed')))

                if enemy_fire_flame.properties.get('fire_length') is None:
                    fire_length = int(enemy_fire_flame_layer.properties.get('fire_length'))
                else:
                    fire_length = int(enemy_fire_flame.properties.get('fire_length'))

                if enemy_fire_flame.properties.get('motion_schedule') is None:
                    motion_schedule = enemy_fire_flame_layer.properties.get('motion_schedule')
                else:
                    motion_schedule = enemy_fire_flame.properties.get('motion_schedule')
                # Convert string to tuple
                motion_schedule = tuple(map(int, motion_schedule.split(',')))

                # Get all sprites
                sprites = []
                frames = enemy_fire_flame.properties.get('frames')
                if frames is not None:
                    for frame in frames:
                        sprites.append(self.tmx_data.get_tile_image_by_gid(frame.gid))

                if enemy_fire_flame.properties.get('direction') is None:
                    direction = enemy_fire_flame_layer.properties.get('direction')
                else:
                    direction = enemy_fire_flame.properties.get('direction')

                if direction == 'left':
                    FireFlameEnemyLeft(sprites, (x, y), [self.bottom_layer_regular_sprites, self.hostile_force_sprites],
                                       speed, fire_length, motion_schedule, self.moving_obstacle_sprites)
                elif direction == 'right':
                    FireFlameEnemyRight(sprites, (x, y), [self.bottom_layer_regular_sprites, self.hostile_force_sprites],
                                        speed, fire_length, motion_schedule, self.moving_obstacle_sprites)

    def run(self):
        # Run an update method foreach sprite from the group
        # NOTE: bottom_layer_background_sprites is static
        self.bottom_layer_regular_sprites.update()
        self.middle_layer_regular_sprites.update()
        self.top_layer_sprites.update()
        # Run an update method for effects
        self.blast_effect.update()

        # Draw all visible sprites
        self.bottom_layer_background_sprites.custom_draw(self.player)
        self.bottom_layer_regular_sprites.custom_draw(self.player)
        self.middle_layer_regular_sprites.custom_draw(self.player)
        self.top_layer_sprites.custom_draw(self.player)
        # Draw effects
        self.blast_effect.draw()

        # Blit game_surface on the main screen
        self.screen.blit(self.game_surface, (0, 0))

        # Read inputs and display variables if debugger is enabled
        settings.debugger.input()
        settings.debugger.show()

    def refresh_obstacle_map(self):
        # Refresh obstacle map if is required
        for sprite in self.enemy_sprites.sprites():
            if isinstance(sprite, obstacle_map_refresh_sprite.ObstacleMapRefreshSprite):
                sprite.refresh_obstacle_map()
        for sprite in self.hostile_force_sprites.sprites():
            if isinstance(sprite, obstacle_map_refresh_sprite.ObstacleMapRefreshSprite):
                sprite.refresh_obstacle_map()

    def show_exit_point(self):
        self.blast_effect.run()
        self.exit_point.visible = True

    def next_level(self):
        # Show message
        half_width = self.screen.get_size()[0] // 2
        half_height = self.screen.get_size()[1] // 2

        accent_color = (255, 255, 255)
        background_color = (100, 100, 100)
        basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 50)

        text_layer = basic_font.render('YOU WIN!', True, accent_color, background_color)
        text_layer_size = text_layer.get_size()
        self.screen.blit(text_layer, (half_width - text_layer_size[0] // 2, half_height - text_layer_size[1] // 2))

    def game_over(self):
        # Show message
        half_width = self.screen.get_size()[0] // 2
        half_height = self.screen.get_size()[1] // 2

        accent_color = (255, 255, 255)
        background_color = (100, 100, 100)
        basic_font = pygame.font.Font('font/silkscreen/silkscreen-regular.ttf', 50)

        game_over = basic_font.render('GAME OVER', True, accent_color, background_color)
        game_over_size = game_over.get_size()
        self.screen.blit(game_over, (half_width - game_over_size[0] // 2, half_height - game_over_size[1] // 2))
