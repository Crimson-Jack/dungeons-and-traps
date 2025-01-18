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
from diamond_tile_details import DiamondTileDetails
from door import Door
from key import Key
from key_and_door_tile_details import KeyAndDoorTileDetails
from teleport import Teleport
from teleport_tile_details import TeleportTileDetails
from spider_enemy import SpiderEnemy
from spider_tile_details import SpiderTileDetails
from ghost_enemy import GhostEnemy
from ghost_tile_details import GhostTileDetails
from fire_flame_enemy_left import FireFlameEnemyLeft
from fire_flame_enemy_right import FireFlameEnemyRight
from fire_flame_tile_details import FireFlameTileDetails
from monster_enemy import MonsterEnemy
from monster_tile_details import MonsterTileDetails
from bat_enemy import BatEnemy
from bat_tile_details import BatTileDetails
from player import Player
from check_point import CheckPoint
from exit_point import ExitPoint
from blast_effect import BlastEffect
from camera_group import CameraGroup
from camera_group_with_y_sort import CameraGroupWithYSort
from tombstone import Tombstone
from vanishing_point import VanishingPoint
from particle_effect import ParticleEffect
from powerup_factory import PowerupFactory
from powerup_tile_details import PowerupTileDetails
from lighting_status import LightingStatus
from spell_tile_details import SpellTileDetails
from lighting_spell import LightingSpell


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
        self.tmx_data = load_pygame(f'data/tmx/{self.game_state.get_level_filename()}')
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
        self.teleport_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.hostile_force_sprites = pygame.sprite.Group()

        # Create obstacle map
        self.obstacle_map = self.create_obstacle_map(size_of_map)

        # Create sprites
        self.create_sprites()
        # Create player
        self.player = self.create_player()
        # Create check point
        self.check_point = self.create_check_point()
        # Create exit point
        self.exit_point = self.create_exit_point()

        # Set blast effect details
        self.blast_effect = BlastEffect(self.game_surface, self.game_surface_rect, 8, 'White')
        # Tombstones
        self.tombstones = list()
        # Vanishing points
        self.vanishing_points = list()
        # Particle effects
        self.particle_effects = list()

    def create_obstacle_map(self, size_of_map):
        # Create obstacle map and combine all layers with obstacles
        obstacle_data = None
        moving_obstacle_data = None
        door_layer_data = None

        for layer in self.tmx_data.visible_layers:
            if layer.name == 'obstacle':
                obstacle_data = self.tmx_data.get_layer_by_name('obstacle').data
            if layer.name == 'moving-obstacle':
                moving_obstacle_data = self.tmx_data.get_layer_by_name('moving-obstacle').data
            if layer.name == 'door':
                door_layer_data = tmx_helper.get_object_group_data_map(self.tmx_data.get_layer_by_name('door'),
                                                                       size_of_map,
                                                                       self.tmx_data.tilewidth,
                                                                       self.tmx_data.tileheight)

        return ObstacleMap([
            obstacle_data,
            moving_obstacle_data,
            door_layer_data
        ])

    def create_player(self):
        try:
            player_object = self.tmx_data.get_object_by_name('player')
        except:
            player_object = None

        if player_object is not None and player_object.visible:
            x, y = tmx_helper.convert_position(player_object.x, player_object.y, self.tmx_data.tilewidth,
                                               self.tmx_data.tileheight)
            speed = game_helper.multiply_by_tile_size_ratio(tmx_helper.get_property('speed', 7, player_object, None))
            return Player((x, y),
                          (self.middle_sprites_layer,),
                          [self.middle_sprites_layer],
                          speed,
                          self.exit_points,
                          self.obstacle_sprites,
                          self.moving_obstacle_sprites,
                          self.passage_sprites,
                          self.teleport_sprites,
                          self.collectable_sprites,
                          self.enemy_sprites,
                          self.hostile_force_sprites,
                          self.game_state)

    def create_check_point(self):
        try:
            check_point = self.tmx_data.get_object_by_name('check-point')
        except:
            check_point = None

        if check_point is not None and check_point.visible:
            tile_x = int(check_point.x // self.tmx_data.tilewidth)
            tile_y = int(check_point.y // self.tmx_data.tileheight)
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            groups = (self.bottom_background_layer, self.collectable_sprites)

            return CheckPoint(check_point.image, (x, y), groups, self.game_state)

    def create_exit_point(self):
        try:
            exit_object = self.tmx_data.get_object_by_name('exit-point')
        except:
            exit_object = None

        if exit_object is not None and exit_object.visible:
            tile_x = int(exit_object.x // self.tmx_data.tilewidth)
            tile_y = int(exit_object.y // self.tmx_data.tileheight)
            x = tile_x * settings.TILE_SIZE
            y = tile_y * settings.TILE_SIZE
            groups = (self.bottom_background_layer, self.exit_points)

            return ExitPoint(exit_object.image, (x, y), groups, False)

    def create_sprites(self):
        self.create_sprites_from_layer('ground')
        self.create_sprites_from_layer('diamond')
        self.create_sprites_from_layer('obstacle')
        self.create_sprites_from_layer('moving-obstacle')
        self.create_sprites_from_object_layer('spell')
        self.create_sprites_from_object_layer('powerup')
        self.create_sprites_from_object_layer('key')
        self.create_sprites_from_object_layer('fire-flame-enemy')
        self.create_sprites_from_object_layer('door')
        self.create_sprites_from_object_layer('teleport')
        self.create_sprites_from_object_layer('monster-enemy')
        self.create_sprites_from_object_layer('spider-enemy')
        self.create_sprites_from_object_layer('ghost-enemy')
        self.create_sprites_from_object_layer('bat-enemy')

    def create_sprites_from_layer(self, layer_name):
        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
        except:
            layer = None

        if layer is not None and layer.visible:
            for tile_x, tile_y, image in layer.tiles():
                x = tile_x * settings.TILE_SIZE
                y = tile_y * settings.TILE_SIZE

                if layer_name == 'ground':
                    groups = (self.bottom_background_layer,)
                    Ground(image, (x, y), groups)

                elif layer_name == 'diamond':
                    groups = (self.bottom_sprites_layer, self.collectable_sprites)
                    tile_details = DiamondTileDetails(None, layer)
                    self.game_state.add_diamond(Diamond(image, (x, y), groups, self.game_state, tile_details))

                elif layer_name == 'obstacle':
                    groups = (self.middle_sprites_layer, self.obstacle_sprites)
                    Wall(image, (x, y), groups)

                elif layer_name == 'moving-obstacle':
                    groups = (self.middle_sprites_layer, self.moving_obstacle_sprites)
                    collision_sprites = [self.enemy_sprites,
                                         self.obstacle_sprites,
                                         self.moving_obstacle_sprites,
                                         self.collectable_sprites]
                    # Note: stone can be moved, so the list instead of tuple for position is used
                    Stone(image, [x, y], groups, self.game_state, self.obstacle_map.items, collision_sprites)

    def create_sprites_from_object_layer(self, layer_name):
        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
        except:
            layer = None

        if layer is not None and layer.visible:
            for item in layer:
                if item.visible:
                    x, y = tmx_helper.convert_position(item.x, item.y, self.tmx_data.tilewidth, self.tmx_data.tileheight)

                    if layer_name == 'spell':
                        groups = (self.bottom_sprites_layer, self.collectable_sprites)
                        tile_details = SpellTileDetails(item, layer)
                        LightingSpell(item.image, (x, y), groups, self.game_state, tile_details)

                    if layer_name == 'powerup':
                        groups = (self.bottom_sprites_layer, self.collectable_sprites)
                        tile_details = PowerupTileDetails(item, layer)
                        self.powerup_factory.create(tile_details,
                                                    image=item.image,
                                                    position=(x, y),
                                                    groups=groups,
                                                    game_state=self.game_state)

                    if layer_name == 'key':
                        groups = (self.bottom_sprites_layer, self.collectable_sprites)
                        tile_details = KeyAndDoorTileDetails(item, layer)
                        self.game_state.add_key(Key(item.image, (x, y), groups, self.game_state, tile_details))

                    elif layer_name == 'fire-flame-enemy':
                        frames = tmx_helper.get_frames(self.tmx_data, item)
                        groups = (self.bottom_sprites_layer, self.hostile_force_sprites)
                        tile_details = FireFlameTileDetails(item, layer)
                        if tile_details.direction == 'left':
                            FireFlameEnemyLeft(frames, (x, y), groups, tile_details, self.moving_obstacle_sprites)
                        elif tile_details.direction == 'right':
                            FireFlameEnemyRight(frames, (x, y), groups, tile_details, self.moving_obstacle_sprites)

                    elif layer_name == 'door':
                        groups = (self.middle_sprites_layer, self.obstacle_sprites, self.passage_sprites)
                        tile_details = KeyAndDoorTileDetails(item, layer)
                        Door(item.image, (x, y), groups, tile_details, self.obstacle_map.items)

                    elif layer_name == 'teleport':
                        groups = (self.bottom_sprites_layer, self.teleport_sprites)
                        tile_details = TeleportTileDetails(item, layer)
                        Teleport(item.image, (x, y), groups, tile_details)

                    elif layer_name == 'monster-enemy':
                        frames = tmx_helper.get_frames(self.tmx_data, item)
                        groups = (self.top_sprites_layer, self.enemy_sprites)
                        tile_details = MonsterTileDetails(item, layer)
                        MonsterEnemy(frames, (x, y), groups, self.game_state, tile_details, item.name,
                                     self.obstacle_map.items, self.moving_obstacle_sprites, self.hostile_force_sprites)

                    elif layer_name == 'spider-enemy':
                        frames = tmx_helper.get_frames(self.tmx_data, item)
                        groups = (self.top_sprites_layer, self.enemy_sprites)
                        tile_details = SpiderTileDetails(item, layer)
                        SpiderEnemy(frames, (x, y), groups, self.game_state, tile_details, item.name,
                                    self.moving_obstacle_sprites)

                    elif layer_name == 'ghost-enemy':
                        frames = tmx_helper.get_frames(self.tmx_data, item)
                        groups = (self.top_sprites_layer, self.enemy_sprites)
                        tile_details = GhostTileDetails(item, layer)
                        GhostEnemy(frames, (x, y), groups, tile_details, self.obstacle_map.items,
                                   self.moving_obstacle_sprites)

                    elif layer_name == 'bat-enemy':
                        frames = tmx_helper.get_frames(self.tmx_data, item)
                        groups = (self.top_sprites_layer, self.enemy_sprites)
                        tile_details = BatTileDetails(item, layer)
                        BatEnemy(frames, (x, y), groups, self.game_state, tile_details, item.name,
                                 self.obstacle_map.items, self.moving_obstacle_sprites, self.hostile_force_sprites)

    def run(self):
        self.remove_unnecessary_effects()

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
        # Blit dark_surface on the main screen
        self.blit_dark_surface()

        # Read inputs and display variables if debugger is enabled
        settings.debugger.input()
        settings.debugger.show()

    def blit_dark_surface(self):
        if self.game_state.lighting_status != LightingStatus.LIGHT_ON:
            # Create surface with transparent color (alpha) with the same size as game surface
            dark_surface = pygame.Surface(pygame.Rect(self.game_surface_rect).size, pygame.SRCALPHA)
            dark_surface.fill((0, 0, 0))
            # Calculate circle position
            offset = self.middle_sprites_layer.get_map_offset()
            circle_x = self.player.rect.centerx + offset.x
            circle_y = self.player.rect.centery + offset.y

            if self.game_state.lighting_status == LightingStatus.TWILIGHT:
                pygame.draw.circle(dark_surface, (0, 0, 0, 150), (circle_x, circle_y), 80)
            elif self.game_state.lighting_status == LightingStatus.TORCHLIGHT:
                circle_radius = 200, 220, 240, 260, 280
                circle_alpha = 0, 50, 100, 150, 200
                for index in range(4, -1, -1):
                    pygame.draw.circle(dark_surface, (0, 0, 0, circle_alpha[index]), (circle_x, circle_y),
                                       circle_radius[index])

            self.screen.blit(dark_surface, self.game_surface_position)

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
        self.exit_point.show()

    def add_tombstone(self, position):
        self.tombstones.append(Tombstone(position, self.bottom_sprites_layer))

    def add_vanishing_point(self, position):
        self.vanishing_points.append(VanishingPoint(position, self.bottom_sprites_layer))

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
        self.player.disable()
        self.player.trigger_tombstone_creation()

    def show_player_vanishing_point(self):
        self.player.disable()
        self.player.trigger_vanishing_point_creation()

    def respawn_player(self, position=None):
        if position is None:
            position = self.game_state.get_check_point_position()
        self.player.respawn(position)
        self.player.enable()

    def remove_unnecessary_effects(self):
        for tombstone in self.tombstones:
            if tombstone.is_expired():
                self.tombstones.remove(tombstone)
                tombstone.kill()
        for vanishing_point in self.vanishing_points:
            if vanishing_point.is_expired():
                self.vanishing_points.remove(vanishing_point)
                vanishing_point.kill()
        for particle_effect in self.particle_effects:
            if particle_effect.is_expired():
                self.particle_effects.remove(particle_effect)
