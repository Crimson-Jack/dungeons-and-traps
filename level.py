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
from door import Door
from powerup_factory import PowerupFactory
from key import Key
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
from tombstone import Tombstone
from particle_effect import ParticleEffect


class Level:
    def __init__(self, screen, game_surface, game_state):
        # Factories
        self.powerup_factory = PowerupFactory()

        # Set screen and game_surface
        self.screen = screen
        self.game_surface = game_surface

        # Set game state
        self.game_state = game_state

        # Load tmx data - world map
        self.tmx_data = load_pygame(f'data/tmx/{self.game_state.get_level()}')
        size_of_map = (self.tmx_data.width, self.tmx_data.height)

        # Calculate game surface position
        map_rect = pygame.Rect(0, 0, size_of_map[0] * settings.TILE_SIZE, size_of_map[1] * settings.TILE_SIZE)
        self.game_surface_position = [0, 0]

        if map_rect.width < self.game_surface.get_width():
            self.game_surface_position[0] = (self.game_surface.get_width() - map_rect.width) // 2
        if map_rect.height < self.game_surface.get_height():
            self.game_surface_position[1] = (self.game_surface.get_height() - map_rect.height) // 2

        self.game_surface_position[1] += settings.HEADER_HEIGHT

        # Calculate game surface rectangle
        self.game_surface_rect = self.game_surface.get_rect()

        if self.game_surface_rect.width > map_rect.width:
            self.game_surface_rect.width = map_rect.width
        if self.game_surface_rect.height > map_rect.height:
            self.game_surface_rect.height = map_rect.height

        # Set up visible groups
        self.bottom_background_layer = CameraGroup(game_surface, size_of_map)
        self.bottom_sprites_layer = CameraGroup(game_surface, size_of_map)
        self.middle_sprites_layer = CameraGroupWithYSort(game_surface, size_of_map)
        self.top_sprites_layer = CameraGroup(game_surface, size_of_map)

        # Set up functional groups
        self.exit_points = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.moving_obstacle_sprites = pygame.sprite.Group()
        self.passage_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.hostile_force_sprites = pygame.sprite.Group()

        # Create obstacle map and combine all layers with obstacles
        self.obstacle_map = ObstacleMap([
            self.tmx_data.get_layer_by_name('obstacle').data,
            self.tmx_data.get_layer_by_name('moving-obstacle').data,
            tmx_helper.get_object_group_data_map(self.tmx_data.get_layer_by_name('door'), size_of_map,
                                                 self.tmx_data.tilewidth, self.tmx_data.tileheight)
        ])

        # Create sprites
        self.create_sprites()
        # Create player
        self.player = self.create_player()
        # Create exit point
        self.exit_point = self.create_exit_point()

        # Set blast effect details
        self.blast_effect = BlastEffect(self.game_surface, self.game_surface_rect, 8, 'White')
        # Tombstones
        self.tombstones = list()
        # Particle effects
        self.particle_effects = list()

    def create_player(self):
        player_object = self.tmx_data.get_object_by_name('player')

        if player_object.visible:
            x, y = tmx_helper.convert_position(player_object.x, player_object.y, self.tmx_data.tilewidth,
                                               self.tmx_data.tileheight)
            speed = game_helper.multiply_by_tile_size_ratio(tmx_helper.get_property('speed', 7, player_object, None))
            return Player((x, y), (self.middle_sprites_layer,), [self.middle_sprites_layer],
                          speed, self.exit_points, self.obstacle_sprites, self.moving_obstacle_sprites,
                          self.passage_sprites, self.collectable_sprites, self.enemy_sprites,
                          self.hostile_force_sprites, self.game_state)

    def create_exit_point(self):
        exit_object = self.tmx_data.get_object_by_name('exit-point')

        if exit_object.visible:
            tile_x = int(exit_object.x // self.tmx_data.tilewidth)
            tile_y = int(exit_object.y // self.tmx_data.tileheight)
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE

            # Add exit point to visible group
            return ExitPoint(exit_object.image, (x, y), (self.bottom_background_layer, self.exit_points), False)

    def create_sprites(self):
        self.create_sprites_from_layer('ground')
        self.create_sprites_from_layer('diamond')
        self.create_sprites_from_layer('obstacle')
        self.create_sprites_from_layer('moving-obstacle')
        self.create_sprites_from_object_layer('powerup')
        self.create_sprites_from_object_layer('key')
        self.create_sprites_from_object_layer('fire-flame-enemy')
        self.create_sprites_from_object_layer('door')
        self.create_sprites_from_object_layer('monster-enemy')
        self.create_sprites_from_object_layer('spider-enemy')
        self.create_sprites_from_object_layer('ghost-enemy')

    def create_sprites_from_layer(self, layer_name):
        layer = self.tmx_data.get_layer_by_name(layer_name)
        if layer.visible:
            for tile_x, tile_y, image in layer.tiles():
                x = tile_x * settings.TILE_SIZE
                y = tile_y * settings.TILE_SIZE

                if layer_name == 'ground':
                    groups = (self.bottom_background_layer,)
                    Ground(image, (x, y), groups)

                elif layer_name == 'diamond':
                    groups = (self.bottom_sprites_layer, self.collectable_sprites)
                    self.game_state.add_diamond(Diamond(image, (x, y), groups))

                elif layer_name == 'obstacle':
                    groups = (self.middle_sprites_layer, self.obstacle_sprites)
                    Wall(image, (x, y), groups)

                elif layer_name == 'moving-obstacle':
                    groups = (self.middle_sprites_layer, self.moving_obstacle_sprites)
                    collision_sprites = [self.enemy_sprites, self.obstacle_sprites, self.moving_obstacle_sprites,
                                         self.collectable_sprites]
                    # Note: stone can be moved, so the list instead of tuple for position is used
                    Stone(image, [x, y], groups, self.obstacle_map.items, collision_sprites, self.game_state)

    def create_sprites_from_object_layer(self, layer_name):
        layer = self.tmx_data.get_layer_by_name(layer_name)
        if layer.visible:
            for item in layer:
                if item.visible:
                    x, y = tmx_helper.convert_position(item.x, item.y, self.tmx_data.tilewidth, self.tmx_data.tileheight)

                    if layer_name == 'powerup':
                        groups = (self.bottom_sprites_layer, self.collectable_sprites)
                        powerup_name = tmx_helper.get_property('powerup_name', '', item, layer)
                        powerup_volume = tmx_helper.get_property('powerup_volume', 0, item, layer)
                        self.powerup_factory.create(powerup_name, image=item.image, position=(x, y), groups=groups,
                                                    game_state=self.game_state, powerup_volume=powerup_volume)

                    if layer_name == 'key':
                        groups = (self.bottom_sprites_layer, self.collectable_sprites)
                        key_name = tmx_helper.get_property('key_name', '', item, layer)
                        self.game_state.add_key(Key(item.image, (x, y), groups, key_name))

                    elif layer_name == 'fire-flame-enemy':
                        groups = (self.bottom_sprites_layer, self.hostile_force_sprites)
                        direction = tmx_helper.get_property('direction', 'right', item, layer)
                        fire_length = int(tmx_helper.get_property('fire_length', 1, item, layer))
                        speed = game_helper.multiply_by_tile_size_ratio(
                            tmx_helper.get_property('speed', 1, item, layer))
                        motion_schedule = game_helper.convert_string_to_tuple(
                            tmx_helper.get_property('motion_schedule', '', item, layer))

                        # Get all sprites
                        sprites = []
                        frames = item.properties.get('frames')
                        if frames is not None:
                            for frame in frames:
                                sprites.append(self.tmx_data.get_tile_image_by_gid(frame.gid))

                        if direction == 'left':
                            FireFlameEnemyLeft(sprites, (x, y), groups, speed, fire_length, motion_schedule,
                                               self.moving_obstacle_sprites)
                        elif direction == 'right':
                            FireFlameEnemyRight(sprites, (x, y), groups, speed, fire_length, motion_schedule,
                                                self.moving_obstacle_sprites)

                    elif layer_name == 'door':
                        groups = (self.middle_sprites_layer, self.obstacle_sprites, self.passage_sprites)
                        key_name = tmx_helper.get_property('key_name', '', item, layer)
                        Door(item.image, (x, y), groups, key_name, self.obstacle_map.items)

                    elif layer_name == 'monster-enemy':
                        groups = (self.top_sprites_layer, self.enemy_sprites)
                        speed = game_helper.multiply_by_tile_size_ratio(
                            tmx_helper.get_property('speed', 1, item, layer))
                        start_delay = tmx_helper.get_property('start_delay', 10, item, layer)
                        frames = tmx_helper.get_frames(self.tmx_data, item)
                        MonsterEnemy(frames, (x, y), groups, item.name, speed, start_delay, self.obstacle_map.items,
                                     self.game_state, self.moving_obstacle_sprites)

                    elif layer_name == 'spider-enemy':
                        groups = (self.top_sprites_layer, self.enemy_sprites)
                        net_length = int(tmx_helper.get_property('net_length', 1, item, layer))
                        speed = game_helper.multiply_by_tile_size_ratio(
                            tmx_helper.get_property('speed', 1, item, layer))
                        motion_schedule = game_helper.convert_string_to_tuple(
                            tmx_helper.get_property('motion_schedule', '', item, layer))
                        frames = tmx_helper.get_frames(self.tmx_data, item)
                        SpiderEnemy(frames, (x, y), groups, item.name, speed, net_length, motion_schedule,
                                    self.moving_obstacle_sprites)

                    elif layer_name == 'ghost-enemy':
                        groups = (self.top_sprites_layer, self.enemy_sprites)
                        speed = game_helper.multiply_by_tile_size_ratio(
                            tmx_helper.get_property('speed', 1, item, layer))
                        frames = tmx_helper.get_frames(self.tmx_data, item)
                        GhostEnemy(frames, (x, y), groups, speed, self.obstacle_map.items, self.moving_obstacle_sprites)

    def run(self):
        self.clean_up()

        # Run an update method foreach sprite from the group
        # NOTE: bottom_layer_background_sprites is static
        self.bottom_sprites_layer.update()
        self.middle_sprites_layer.update()
        self.top_sprites_layer.update()
        # Run an update method for effects
        self.update_particle_effects()
        self.blast_effect.update()

        # Draw all visible sprites
        self.bottom_background_layer.custom_draw(self.player)
        self.bottom_sprites_layer.custom_draw(self.player)
        self.middle_sprites_layer.custom_draw(self.player)
        self.top_sprites_layer.custom_draw(self.player)
        # Draw effects
        self.draw_particle_effects()
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

    def add_tombstone(self, position):
        self.tombstones.append(Tombstone(position, self.bottom_sprites_layer))

    def add_particle_effect(self, position, number_of_sparks, colors):
        self.particle_effects.append(
            ParticleEffect(self.game_surface, position, colors, number_of_sparks,
                           game_helper.get_tile_size_ratio()))

    def update_particle_effects(self):
        map_offset = self.top_sprites_layer.get_map_offset()
        for particle_effect in self.particle_effects:
            if not particle_effect.is_expired():
                particle_effect.update(map_offset)

    def draw_particle_effects(self):
        for particle_effect in self.particle_effects:
            particle_effect.draw()

    def add_spark_to_particle_effect(self):
        for particle_effect in self.particle_effects:
            particle_effect.add_spark()

    def show_player_tombstone(self):
        self.player.show_tombstone()

    def respawn_player(self):
        self.player.respawn()

    def clean_up(self):
        # Remove unnecessary items
        for tombstone in self.tombstones:
            if tombstone.is_expired():
                self.tombstones.remove(tombstone)
                tombstone.kill()
        for particle_effect in self.particle_effects:
            if particle_effect.is_expired():
                self.particle_effects.remove(particle_effect)
