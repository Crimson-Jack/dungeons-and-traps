import pygame
import enemy_with_brain
import obstacle_map_refresh_sprite
import settings
import game_helper
import tmx_helper
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
from monster_enemy import MonsterEnemy
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

        # Calculate game surface position
        map_rect = pygame.Rect(0, 0, size_of_map[0] * settings.TILE_SIZE, size_of_map[1] * settings.TILE_SIZE)
        self.game_surface_position = game_helper.calculate_game_surface_position(self.game_surface.get_width(),
                                                                                 self.game_surface.get_height(),
                                                                                 map_rect.width,
                                                                                 map_rect.height)
        # Set game surface rect
        self.game_surface_rect = self.game_surface.get_rect()

        if self.game_surface_rect.width > map_rect.width:
            self.game_surface_rect.width = map_rect.width
        if self.game_surface_rect.height > map_rect.height:
            self.game_surface_rect.height = map_rect.height

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

        # Set blast effect details
        self.blast_effect = BlastEffect(self.game_surface, self.game_surface_rect, 8, 'White')

    def create_player(self):
        player_object = self.tmx_data.get_object_by_name('player')

        if player_object.visible:
            # Position
            x, y = tmx_helper.convert_position(player_object.x, player_object.y, self.tmx_data.tilewidth,
                                               self.tmx_data.tileheight)
            # Custom properties
            speed = game_helper.convert_to_tile_size_ratio_decorator(tmx_helper.get_property)('speed', 7, player_object,
                                                                                              None)

            # Add player to visible group
            return Player((x, y), (self.middle_layer_regular_sprites,), [self.middle_layer_regular_sprites],
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
            return ExitPoint(exit_object.image, (x, y), (self.bottom_layer_background_sprites, self.exit_points), False)

    def create_sprites(self):
        ground_layer = self.tmx_data.get_layer_by_name('ground')
        for tile_x, tile_y, image in ground_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to background sprites group
            Ground(image, (x, y), (self.bottom_layer_background_sprites,))

        obstacle_layer = self.tmx_data.get_layer_by_name('obstacle')
        for tile_x, tile_y, image in obstacle_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to visible and obstacle sprites group
            Wall(image, (x, y), (self.middle_layer_regular_sprites, self.obstacle_sprites))

        moving_obstacle_layer = self.tmx_data.get_layer_by_name('moving-obstacle')
        for tile_x, tile_y, image in moving_obstacle_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Create collision sprites list for moving obstacles
            collision_sprites = [self.enemy_sprites, self.obstacle_sprites, self.moving_obstacle_sprites,
                                 self.collectable_sprites]
            # Add tile to visible and obstacle sprites group
            # Note: stone can be moved, so the list instead of tuple for position is used
            Stone(image, [x, y], (self.middle_layer_regular_sprites, self.moving_obstacle_sprites),
                  self.obstacle_map.items, collision_sprites, self.game_state)

        collectable_diamond_layer = self.tmx_data.get_layer_by_name('collectable-diamond')
        for tile_x, tile_y, image in collectable_diamond_layer.tiles():
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            # Add tile to visible and collectable sprites group
            diamond = Diamond(image, (x, y), (self.middle_layer_regular_sprites, self.collectable_sprites))
            self.game_state.add_diamond(diamond)

        spider_layer = self.tmx_data.get_layer_by_name('spider-enemy')
        for spider_item in spider_layer:
            if spider_item.visible:
                # Position
                x, y = tmx_helper.convert_position(spider_item.x, spider_item.y, self.tmx_data.tilewidth,
                                                   self.tmx_data.tileheight)
                # Custom properties
                net_length = int(tmx_helper.get_property('net_length', 1, spider_item, spider_layer))
                speed = game_helper.convert_to_tile_size_ratio_decorator(tmx_helper.get_property)('speed', 1,
                                                                                                  spider_item,
                                                                                                  spider_layer)
                motion_schedule = game_helper.convert_to_tuple_decorator(tmx_helper.get_property)('motion_schedule', '',
                                                                                                  spider_item,
                                                                                                  spider_layer)

                SpiderEnemy(spider_item.image, (x, y), (self.top_layer_sprites, self.enemy_sprites),
                            speed, net_length, motion_schedule, self.moving_obstacle_sprites)

        ghost_layer = self.tmx_data.get_layer_by_name('enemy-ghost')
        for ghost_item in ghost_layer:
            if ghost_item.visible:
                # Position
                x, y = tmx_helper.convert_position(ghost_item.x, ghost_item.y, self.tmx_data.tilewidth,
                                                   self.tmx_data.tileheight)
                # Custom properties
                speed = game_helper.convert_to_tile_size_ratio_decorator(tmx_helper.get_property)('speed', 1,
                                                                                                  ghost_item,
                                                                                                  ghost_layer)
                # Get all sprites with duration (frames)
                frames = tmx_helper.get_frames(self.tmx_data, ghost_item)

                GhostEnemy(frames, (x, y), (self.top_layer_sprites, self.enemy_sprites),
                           speed, self.obstacle_map.items, self.moving_obstacle_sprites)

        fire_flame_layer = self.tmx_data.get_layer_by_name('enemy-fire-flame')
        for fire_flame_item in fire_flame_layer:
            if fire_flame_item.visible:
                # Position
                x, y = tmx_helper.convert_position(fire_flame_item.x, fire_flame_item.y, self.tmx_data.tilewidth,
                                                   self.tmx_data.tileheight)
                # Custom properties
                direction = tmx_helper.get_property('direction', 'right', fire_flame_item, fire_flame_layer)
                fire_length = int(tmx_helper.get_property('fire_length', 1, fire_flame_item, fire_flame_layer))
                speed = game_helper.convert_to_tile_size_ratio_decorator(tmx_helper.get_property)('speed', 1,
                                                                                                  fire_flame_item,
                                                                                                  fire_flame_layer)
                motion_schedule = game_helper.convert_to_tuple_decorator(tmx_helper.get_property)('motion_schedule', '',
                                                                                                  fire_flame_item,
                                                                                                  fire_flame_layer)

                # Get all sprites
                sprites = []
                frames = fire_flame_item.properties.get('frames')
                if frames is not None:
                    for frame in frames:
                        sprites.append(self.tmx_data.get_tile_image_by_gid(frame.gid))

                if direction == 'left':
                    FireFlameEnemyLeft(sprites, (x, y), (self.bottom_layer_regular_sprites, self.hostile_force_sprites),
                                       speed, fire_length, motion_schedule, self.moving_obstacle_sprites)
                elif direction == 'right':
                    FireFlameEnemyRight(sprites, (x, y),
                                        (self.bottom_layer_regular_sprites, self.hostile_force_sprites),
                                        speed, fire_length, motion_schedule, self.moving_obstacle_sprites)

        monster_layer = self.tmx_data.get_layer_by_name('monster-enemy')
        for monster_item in monster_layer:
            if monster_item.visible:
                # Position
                x, y = tmx_helper.convert_position(monster_item.x, monster_item.y, self.tmx_data.tilewidth,
                                                   self.tmx_data.tileheight)
                # Custom properties
                speed = game_helper.convert_to_tile_size_ratio_decorator(tmx_helper.get_property)('speed', 1,
                                                                                                  monster_item,
                                                                                                  monster_layer)
                # Get all sprites with duration (frames)
                frames = tmx_helper.get_frames(self.tmx_data, monster_item)

                MonsterEnemy(frames, (x, y), (self.bottom_layer_regular_sprites, self.enemy_sprites),
                             monster_item.name, speed, self.obstacle_map.items, self.game_state, self.moving_obstacle_sprites)

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
        self.screen.blit(self.game_surface, self.game_surface_position, self.game_surface_rect)

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

    def inform_about_player_tile_position(self):
        for sprite in self.enemy_sprites.sprites():
            if isinstance(sprite, enemy_with_brain.EnemyWithBrain):
                sprite.set_player_tile_position()

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
