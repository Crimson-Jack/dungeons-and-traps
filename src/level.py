import random

import pygame
from pytmx.util_pygame import load_pygame

from settings import Settings
from src.events import Events
from src.abstract_classes.pathfinding_enemy import PathfindingEnemy
from src.abstract_classes.obstacle_map_observer import ObstacleMapObserver
from src.enums.enemy_type import EnemyType
from src.effects.blast_effect import BlastEffect
from src.effects.explode_effect import ExplodeEffect
from src.effects.particle_effect import ParticleEffect
from src.enums.lighting_status import LightingStatus
from src.game_helper import GameHelper
from src.level_sprite_groups import LevelSpriteGroups
from src.factories.monster_tile_details_factory import MonsterTileDetailsFactory
from src.obstacle_map import ObstacleMap
from src.factories.powerup_factory import PowerupFactory
from src.sprites.bat_enemy import BatEnemy
from src.sprites.check_point import CheckPoint
from src.sprites.demolished_wall import DemolishedWall
from src.sprites.diamond import Diamond
from src.sprites.door import Door
from src.sprites.egg import Egg
from src.sprites.exit_point import ExitPoint
from src.sprites.fire_flame_enemy_left import FireFlameEnemyLeft
from src.sprites.fire_flame_enemy_right import FireFlameEnemyRight
from src.sprites.ghost_enemy import GhostEnemy
from src.sprites.ground import Ground
from src.sprites.key import Key
from src.sprites.lighting_spell import LightingSpell
from src.sprites.monster_enemy import MonsterEnemy
from src.sprites.octopus_enemy import OctopusEnemy
from src.sprites.player import Player
from src.sprites.spider_enemy import SpiderEnemy
from src.sprites.stone import Stone
from src.sprites.teleport import Teleport
from src.sprites.tombstone import Tombstone
from src.sprites.vanishing_point import VanishingPoint
from src.sprites.wall import Wall
from src.sprite_costume import SpriteCostume
from src.sprite_helper import SpriteHelper
from src.tile_details.bat_tile_details import BatTileDetails
from src.tile_details.diamond_tile_details import DiamondTileDetails
from src.tile_details.fire_flame_tile_details import FireFlameTileDetails
from src.tile_details.ghost_tile_details import GhostTileDetails
from src.tile_details.key_and_door_tile_details import KeyAndDoorTileDetails
from src.tile_details.monster_tile_details import MonsterTileDetails
from src.tile_details.octopus_tile_details import OctopusTileDetails
from src.tile_details.powerup_tile_details import PowerupTileDetails
from src.tile_details.spell_tile_details import SpellTileDetails
from src.tile_details.spider_tile_details import SpiderTileDetails
from src.tile_details.teleport_tile_details import TeleportTileDetails
from src.tmx_helper import TmxHelper
from src.utilities.debug import Debug


class Level:
    def __init__(self, screen, game_surface, game_manager):
        # Factories
        self.powerup_factory = PowerupFactory()

        # Set screen and game_surface
        self.screen = screen
        self.game_surface = game_surface

        # Set game manager
        self.game_manager = game_manager

        # Load tmx data - world map
        self.tmx_data = load_pygame(f'data/tmx/{self.game_manager.get_level_filename()}')
        size_of_map = (self.tmx_data.width, self.tmx_data.height)

        # Calculate game surface position
        map_rect = pygame.Rect(0, 0, size_of_map[0] * Settings.TILE_SIZE, size_of_map[1] * Settings.TILE_SIZE)
        self.game_surface_position = [0, 0]

        if map_rect.width < self.game_surface.get_width():
            self.game_surface_position[0] = (self.game_surface.get_width() - map_rect.width) // 2
        if map_rect.height < self.game_surface.get_height():
            self.game_surface_position[1] = (self.game_surface.get_height() - map_rect.height) // 2

        self.game_surface_position[1] += Settings.HEADER_HEIGHT

        # Calculate game surface rectangle
        self.game_surface_rect = self.game_surface.get_rect()

        if self.game_surface_rect.width > map_rect.width:
            self.game_surface_rect.width = map_rect.width
        if self.game_surface_rect.height > map_rect.height:
            self.game_surface_rect.height = map_rect.height

        # Set up sprite groups
        self.level_sprite_groups = LevelSpriteGroups(game_surface, size_of_map)

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
        # Get boss point position
        self.boss_point_position = self.get_boss_point_position()

        # Set blast effect details
        self.blast_effect = BlastEffect(self.game_surface,
                                        8,
                                        Settings.BLAST_EFFECT_COLOR,
                                        (self.game_surface_rect.width,
                                         self.game_surface_rect.height)
                                        )
        self.explode_effect = ExplodeEffect(self.game_surface,
                                          Settings.NUMBER_OF_EXPLOSION_STEPS,
                                          Settings.EXPLODE_EFFECT_COLOR,
                                          (Settings.TILE_SIZE * Settings.EXPLOSION_WEAPON_RANGE * 2,
                                           Settings.TILE_SIZE * Settings.EXPLOSION_WEAPON_RANGE * 2)
                                          )
        # Tombstones
        self.tombstones = list()
        # Vanishing points
        self.vanishing_points = list()
        # Particle effects
        self.particle_effects = list()

        # Tilt effect variables
        self.tilt_effect_enabled = False
        self.tilt_offset_values = (-25, 20, -15, 14, -9, 9, -6, 5, -5, 4, -5, 4, -4, 3, -4, 3, -3, 2, -3, 2, -2, 2, -2,
                                   1, -1, 1, -1, 1, -1, 1, -1, 1)
        self.tilt_cursor = 0
        self.tilt_cursor_increment_base_value = 0.75
        self.tilt_cursor_increment_value = self.tilt_cursor_increment_base_value

        # Create debugger
        self.debugger = Debug()

    def create_obstacle_map(self, size_of_map):
        # Create obstacle map and combine all layers with obstacles
        obstacle_layer_data = None
        moving_obstacle_layer_data = None
        removable_obstacle_layer_data = None
        door_layer_data = None

        for layer in self.tmx_data.visible_layers:
            if layer.name == 'obstacle':
                obstacle_layer_data = self.tmx_data.get_layer_by_name('obstacle').data
            if layer.name == 'moving-obstacle':
                moving_obstacle_layer_data = self.tmx_data.get_layer_by_name('moving-obstacle').data
            if layer.name == 'removable-obstacle':
                removable_obstacle_layer_data = self.tmx_data.get_layer_by_name('removable-obstacle').data
            if layer.name == 'door':
                door_layer_data = TmxHelper.get_data_map_by_layer(self.tmx_data.get_layer_by_name('door'),
                                                                   size_of_map,
                                                                   self.tmx_data.tilewidth,
                                                                   self.tmx_data.tileheight)

        return ObstacleMap([
            obstacle_layer_data,
            moving_obstacle_layer_data,
            removable_obstacle_layer_data,
            door_layer_data
        ])

    def create_player(self):
        player_object = self._get_visible_object('player')
        if player_object is None:
            return None

        position = TmxHelper.get_tile_position(player_object.x, player_object.y,
                                               self.tmx_data.tilewidth, self.tmx_data.tileheight)
        speed = GameHelper.multiply_by_tile_size_ratio(
            TmxHelper.get_tiled_object_value('speed', 7, player_object, None))
        return Player(position,
                      (self.level_sprite_groups.middle_sprites_layer,),
                      [self.level_sprite_groups.middle_sprites_layer],
                      speed,
                      self.level_sprite_groups.exit_points,
                      self.level_sprite_groups.obstacle_sprites,
                      self.level_sprite_groups.moving_obstacle_sprites,
                      self.level_sprite_groups.passage_sprites,
                      self.level_sprite_groups.teleport_sprites,
                      self.level_sprite_groups.collectable_sprites,
                      self.level_sprite_groups.enemy_sprites,
                      self.level_sprite_groups.hostile_force_sprites,
                      self.game_manager)

    def create_check_point(self):
        check_point = self._get_visible_object('check-point')
        if check_point is None:
            return None

        position = TmxHelper.get_tile_position(check_point.x, check_point.y,
                                               self.tmx_data.tilewidth, self.tmx_data.tileheight)
        groups = self.level_sprite_groups.bottom_background_layer, self.level_sprite_groups.collectable_sprites
        return CheckPoint(check_point.image, position, groups, self.game_manager)

    def create_exit_point(self):
        exit_object = self._get_visible_object('exit-point')
        if exit_object is None:
            return None

        position = TmxHelper.get_tile_position(exit_object.x, exit_object.y,
                                               self.tmx_data.tilewidth, self.tmx_data.tileheight)
        groups = self.level_sprite_groups.bottom_background_layer, self.level_sprite_groups.exit_points
        return ExitPoint(exit_object.image, position, groups, False)

    def get_boss_point_position(self):
        boss_object = self._get_visible_object('boss-point')
        if boss_object is None:
            return None

        return TmxHelper.get_tile_position(boss_object.x, boss_object.y,
                                           self.tmx_data.tilewidth, self.tmx_data.tileheight)

    def create_sprites(self):
        self.create_sprites_from_layer('ground', self._create_ground)
        self.create_sprites_from_layer('diamond', self._create_diamond)
        self.create_sprites_from_layer('obstacle', self._create_wall)
        self.create_sprites_from_layer('moving-obstacle', self._create_stone)
        self.create_sprites_from_layer('removable-obstacle', self._create_demolished_wall)
        self.create_sprites_from_object_layer('spell', self._create_lighting_spell)
        self.create_sprites_from_object_layer('powerup', self._create_powerup)
        self.create_sprites_from_object_layer('key', self._create_key)
        self.create_sprites_from_object_layer('fire-flame-enemy', self._create_fire_flame_enemy)
        self.create_sprites_from_object_layer('door', self._create_door)
        self.create_sprites_from_object_layer('teleport', self._create_teleport)
        self.create_sprites_from_object_layer('monster-enemy', self._create_monster_enemy)
        self.create_sprites_from_object_layer('spider-enemy', self._create_spider_enemy)
        self.create_sprites_from_object_layer('ghost-enemy', self._create_ghost_enemy)
        self.create_sprites_from_object_layer('bat-enemy', self._create_bat_enemy)
        self.create_sprites_from_object_layer('octopus-enemy', self._create_octopus_enemy)

    def create_sprites_from_layer(self, layer_name, create_sprite):
        layer = self._get_visible_layer(layer_name)
        if layer is not None:
            for tile_x, tile_y, image in layer.tiles():
                position = (tile_x * Settings.TILE_SIZE, tile_y * Settings.TILE_SIZE)
                create_sprite(image, layer, position)

    def create_sprites_from_object_layer(self, layer_name, create_sprite):
        layer = self._get_visible_layer(layer_name)
        if layer is not None:
            for item in layer:
                if item.visible:
                    position = TmxHelper.get_tile_position(item.x, item.y, self.tmx_data.tilewidth,
                                                           self.tmx_data.tileheight, item.rotation)
                    create_sprite(item, layer, position)

    def run(self):
        self.remove_unnecessary_effects()

        # Run an update method foreach sprite from the group
        # NOTE: bottom_layer_background_sprites is static
        self.level_sprite_groups.bottom_sprites_layer.update()
        self.level_sprite_groups.middle_sprites_layer.update()
        self.level_sprite_groups.top_sprites_layer.update()
        self.level_sprite_groups.the_highest_sprites_layer.update()

        # Run an update method for effects
        self.update_particle_effects()
        self.blast_effect.update()
        self.explode_effect.update()

        # Clean game surface - fill with background color
        self.game_surface.fill(Settings.GAME_BACKGROUND_COLOR)

        # Draw all visible sprites
        tilt_offset = self.get_tilt_effect_offset()
        self.level_sprite_groups.bottom_background_layer.custom_draw(self.player, tilt_offset)
        self.level_sprite_groups.bottom_sprites_layer.custom_draw(self.player, tilt_offset)
        self.level_sprite_groups.middle_sprites_layer.custom_draw(self.player, tilt_offset)
        self.level_sprite_groups.top_sprites_layer.custom_draw(self.player, tilt_offset)
        self.level_sprite_groups.the_highest_sprites_layer.custom_draw(self.player, tilt_offset)

        # Draw effects
        self.draw_particle_effects()
        self.blast_effect.draw()
        self.explode_effect.draw()

        # Blit game_surface on the main screen
        self.screen.blit(self.game_surface, self.game_surface_position, self.game_surface_rect)
        # Blit dark_surface on the main screen
        self.blit_dark_surface()

        # Read inputs and display variables if debugger is enabled
        self.debugger.input()
        self.debugger.show()

    def blit_dark_surface(self):
        if self.game_manager.lighting_status != LightingStatus.LIGHT_ON:
            # Create surface with transparent color (alpha) with the same size as game surface
            dark_surface = pygame.Surface(pygame.Rect(self.game_surface_rect).size, pygame.SRCALPHA)
            dark_surface.fill((0, 0, 0))
            # Calculate circle position
            offset = self.level_sprite_groups.middle_sprites_layer.get_map_offset()
            circle_x = self.player.rect.centerx + offset.x
            circle_y = self.player.rect.centery + offset.y

            if self.game_manager.lighting_status == LightingStatus.TWILIGHT:
                pygame.draw.circle(dark_surface, (0, 0, 0, 150), (circle_x, circle_y), 100)
            elif self.game_manager.lighting_status == LightingStatus.TORCHLIGHT:
                circle_radius = 200, 220, 240, 260, 280
                circle_alpha = 0, 50, 100, 150, 200
                for index in range(4, -1, -1):
                    pygame.draw.circle(dark_surface, (0, 0, 0, circle_alpha[index]), (circle_x, circle_y),
                                       circle_radius[index])

            self.screen.blit(dark_surface, self.game_surface_position)

    def refresh_obstacle_map(self):
        # Refresh obstacle map if is required
        self.obstacle_map.calculate_regions()

        for sprite in self.level_sprite_groups.enemy_sprites.sprites():
            if isinstance(sprite, ObstacleMapObserver):
                sprite.refresh_obstacle_map()
        for sprite in self.level_sprite_groups.hostile_force_sprites.sprites():
            if isinstance(sprite, ObstacleMapObserver):
                sprite.refresh_obstacle_map()

    def inform_about_player_tile_position(self):
        for sprite in self.level_sprite_groups.enemy_sprites.sprites():
            if isinstance(sprite, PathfindingEnemy):
                sprite.set_player_tile_position()

    def show_exit_point(self):
        self.blast_effect.run()
        self.exit_point.show()

    def show_explode_effect(self, position: tuple[int, int]):
        self.explode_effect.run(position)

    def add_tombstone(self, position):
        sprites = SpriteHelper.get_all_tombstone_sprites()
        self.tombstones.append(Tombstone(sprites, position, (self.level_sprite_groups.bottom_sprites_layer,)))

    def add_boss_tombstone(self, position):
        sprites = SpriteHelper.get_all_boss_tombstone_sprites()
        self.tombstones.append(Tombstone(sprites, position, (self.level_sprite_groups.bottom_sprites_layer,), 0))

    def add_vanishing_point(self, position):
        self.vanishing_points.append(VanishingPoint(position, (self.level_sprite_groups.bottom_sprites_layer,)))

    def create_egg(self, position):
        Egg(position, (self.level_sprite_groups.bottom_sprites_layer, self.level_sprite_groups.collectable_sprites),
            self.game_manager)

    def create_monster(self, position):
        name = random.choice(['monster-enemy-blue-deaf', 'monster-enemy-green-deaf', 'monster-enemy-red-deaf'])
        tile_details = MonsterTileDetailsFactory.create(name)

        sprite_costumes = list()
        for image in SpriteHelper.get_all_monster_sprites(name):
            sprite_costumes.append(SpriteCostume(image, 6))
        sprite_image_in_damage_state = SpriteHelper.get_sprite_image(name, 1, 0)

        groups = self.level_sprite_groups.top_sprites_layer, self.level_sprite_groups.enemy_sprites

        enemy_type = EnemyType.from_name(name)
        MonsterEnemy(sprite_costumes, sprite_image_in_damage_state, position, groups, self.game_manager,
                     enemy_type, tile_details, self.obstacle_map,
                     self.level_sprite_groups.obstacle_sprites, self.level_sprite_groups.moving_obstacle_sprites,
                     self.level_sprite_groups.hostile_force_sprites)
        self.game_manager.level_stats[-1].record_enemy_spawn(enemy_type)

    def create_boss_octopus(self):
        if self.boss_point_position is None:
            raise ValueError(f'The boss point position is none. Add "boss-point" to "major-game-item" layer.')

        name = 'octopus-enemy'
        tile_details = OctopusTileDetails(None, None)

        sprite_costumes = list()
        for image in SpriteHelper.get_all_octopus_sprites(name):
            sprite_costumes.append(SpriteCostume(image, 6))
        sprite_image_in_damage_state = SpriteHelper.get_large_sprite_image(name, 1, 0, 3)

        groups = self.level_sprite_groups.the_highest_sprites_layer, self.level_sprite_groups.enemy_sprites

        OctopusEnemy(sprite_costumes, sprite_image_in_damage_state, self.boss_point_position, groups, self.game_manager,
                     tile_details, self.obstacle_map, self.level_sprite_groups.obstacle_sprites,
                     self.level_sprite_groups.moving_obstacle_sprites)

        self.game_manager.boss_max_energy = tile_details.energy
        self.game_manager.boss_energy = tile_details.energy
        self.game_manager.is_boss_visible = True

    def add_particle_effect(self, position, number_of_sparks, colors):
        self.particle_effects.append(
            ParticleEffect(self.game_surface, position, colors, number_of_sparks,
                           GameHelper.get_tile_size_ratio()))

    def update_particle_effects(self):
        map_offset = self.level_sprite_groups.top_sprites_layer.get_map_offset()
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
            position = self.game_manager.get_check_point_position()
        self.player.respawn(position)
        self.player.enable()

    def remove_obstacles(self):
        if len(self.level_sprite_groups.removable_obstacle_sprites) > 0:
            for sprite in self.level_sprite_groups.removable_obstacle_sprites:
                sprite.kill()
            # Raise event to refresh obstacle map
            pygame.event.post(pygame.event.Event(Events.REFRESH_OBSTACLE_MAP_EVENT))

    def remove_unnecessary_effects(self):
        remaining_tombstones = []
        for tombstone in self.tombstones:
            if tombstone.is_expired():
                tombstone.kill()
            else:
                remaining_tombstones.append(tombstone)
        self.tombstones = remaining_tombstones

        remaining_vanishing_points = []
        for vanishing_point in self.vanishing_points:
            if vanishing_point.is_expired():
                vanishing_point.kill()
            else:
                remaining_vanishing_points.append(vanishing_point)
        self.vanishing_points = remaining_vanishing_points

        remaining_particle_effects = []
        for particle_effect in self.particle_effects:
            if not particle_effect.is_expired():
                remaining_particle_effects.append(particle_effect)
        self.particle_effects = remaining_particle_effects

    def get_tilt_effect_offset(self):
        tilt_offset = None

        if self.tilt_effect_enabled:
            if self.tilt_cursor < len(self.tilt_offset_values):
                tilt_offset = pygame.math.Vector2()
                tilt_offset.y = self.tilt_offset_values[int(self.tilt_cursor)]
                self.tilt_cursor += self.tilt_cursor_increment_value
            else:
                self.tilt_effect_enabled = False
                self.tilt_cursor = 0

        return tilt_offset

    def enable_tilt_effect(self, tilt_cursor_increment_value: float = None):
        self.tilt_effect_enabled = True

        if tilt_cursor_increment_value is not None:
            self.tilt_cursor_increment_value = tilt_cursor_increment_value
        else:
            self.tilt_cursor_increment_value = self.tilt_cursor_increment_base_value

    def _get_visible_object(self, name):
        try:
            tiled_object = self.tmx_data.get_object_by_name(name)
        except (KeyError, ValueError):
            return None
        return tiled_object if tiled_object.visible else None

    def _get_visible_layer(self, name):
        try:
            layer = self.tmx_data.get_layer_by_name(name)
        except (KeyError, ValueError):
            return None
        return layer if layer.visible else None

    def _create_ground(self, image, layer, position):
        groups = (self.level_sprite_groups.bottom_background_layer,)
        Ground(image, position, groups)

    def _create_diamond(self, image, layer, position):
        groups = self.level_sprite_groups.bottom_sprites_layer, self.level_sprite_groups.collectable_sprites
        tile_details = DiamondTileDetails(None, layer)
        self.game_manager.add_diamond(Diamond(image, position, groups, self.game_manager, tile_details))

    def _create_wall(self, image, layer, position):
        groups = self.level_sprite_groups.middle_sprites_layer, self.level_sprite_groups.obstacle_sprites
        Wall(image, position, groups)

    def _create_stone(self, image, layer, position):
        groups = self.level_sprite_groups.middle_sprites_layer, self.level_sprite_groups.moving_obstacle_sprites
        collision_sprites = [self.level_sprite_groups.enemy_sprites,
                             self.level_sprite_groups.obstacle_sprites,
                             self.level_sprite_groups.moving_obstacle_sprites,
                             self.level_sprite_groups.collectable_sprites]
        # Note: stone can be moved, so the list instead of tuple for position is used
        Stone(image, list(position), groups, self.game_manager, self.obstacle_map.items, collision_sprites)

    def _create_demolished_wall(self, image, layer, position):
        groups = (self.level_sprite_groups.middle_sprites_layer, self.level_sprite_groups.obstacle_sprites,
                  self.level_sprite_groups.removable_obstacle_sprites)
        DemolishedWall(image, position, groups, self.obstacle_map.items)

    def _create_lighting_spell(self, item, layer, position):
        groups = self.level_sprite_groups.bottom_sprites_layer, self.level_sprite_groups.collectable_sprites
        tile_details = SpellTileDetails(item, layer)
        LightingSpell(item.image, position, groups, self.game_manager, tile_details)

    def _create_powerup(self, item, layer, position):
        groups = self.level_sprite_groups.bottom_sprites_layer, self.level_sprite_groups.collectable_sprites
        tile_details = PowerupTileDetails(item, layer)
        self.powerup_factory.create(tile_details,
                                    image=item.image,
                                    position=position,
                                    groups=groups,
                                    game_manager=self.game_manager)

    def _create_key(self, item, layer, position):
        groups = self.level_sprite_groups.bottom_sprites_layer, self.level_sprite_groups.collectable_sprites
        tile_details = KeyAndDoorTileDetails(item, layer)
        self.game_manager.add_key(Key(item.image, position, groups, self.game_manager, tile_details))

    def _create_fire_flame_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self.tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        groups = self.level_sprite_groups.bottom_sprites_layer, self.level_sprite_groups.hostile_force_sprites
        tile_details = FireFlameTileDetails(item, layer)
        if tile_details.direction == 'left':
            FireFlameEnemyLeft(sprites, position, groups, tile_details,
                               self.level_sprite_groups.moving_obstacle_sprites)
        elif tile_details.direction == 'right':
            FireFlameEnemyRight(sprites, position, groups, tile_details,
                                self.level_sprite_groups.moving_obstacle_sprites)

    def _create_door(self, item, layer, position):
        groups = (self.level_sprite_groups.middle_sprites_layer, self.level_sprite_groups.obstacle_sprites,
                  self.level_sprite_groups.passage_sprites)
        tile_details = KeyAndDoorTileDetails(item, layer)
        Door(item.image, position, groups, tile_details, self.obstacle_map.items)

    def _create_teleport(self, item, layer, position):
        groups = self.level_sprite_groups.bottom_sprites_layer, self.level_sprite_groups.teleport_sprites
        tile_details = TeleportTileDetails(item, layer)
        Teleport(item.image, position, groups, tile_details)

    def _create_monster_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self.tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        sprite_image_in_damage_state = SpriteHelper.get_sprite_image(item.name, 1, 0)
        groups = self.level_sprite_groups.top_sprites_layer, self.level_sprite_groups.enemy_sprites
        tile_details = MonsterTileDetails(item, layer)
        enemy_type = EnemyType.from_name(item.name)
        MonsterEnemy(sprites, sprite_image_in_damage_state, position, groups, self.game_manager,
                     enemy_type, tile_details, self.obstacle_map,
                     self.level_sprite_groups.obstacle_sprites, self.level_sprite_groups.moving_obstacle_sprites,
                     self.level_sprite_groups.hostile_force_sprites)
        self.game_manager.level_stats[-1].record_enemy_spawn(enemy_type)

    def _create_spider_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self.tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        sprite_costumes_matrix = SpriteHelper.get_sprite_costumes_matrix(item.name, sprites)
        groups = self.level_sprite_groups.top_sprites_layer, self.level_sprite_groups.enemy_sprites
        tile_details = SpiderTileDetails(item, layer)
        enemy_type = EnemyType.from_name(item.name)
        SpiderEnemy(sprite_costumes_matrix, position, groups, self.game_manager,
                    enemy_type, tile_details, self.level_sprite_groups.moving_obstacle_sprites)
        self.game_manager.level_stats[-1].record_enemy_spawn(enemy_type)

    def _create_ghost_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self.tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        groups = self.level_sprite_groups.top_sprites_layer, self.level_sprite_groups.enemy_sprites
        tile_details = GhostTileDetails(item, layer)
        GhostEnemy(sprites, position, groups, tile_details, self.obstacle_map.items,
                   self.level_sprite_groups.moving_obstacle_sprites)

    def _create_bat_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self.tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        sprite_image_in_damage_state = SpriteHelper.get_sprite_image(item.name, 1, 0)
        groups = self.level_sprite_groups.top_sprites_layer, self.level_sprite_groups.enemy_sprites
        tile_details = BatTileDetails(item, layer)
        enemy_type = EnemyType.from_name(item.name)
        BatEnemy(sprites, sprite_image_in_damage_state, position, groups, self.game_manager,
                 enemy_type, tile_details, self.obstacle_map,
                 self.level_sprite_groups.moving_obstacle_sprites, self.level_sprite_groups.hostile_force_sprites)
        self.game_manager.level_stats[-1].record_enemy_spawn(enemy_type)

    def _create_octopus_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self.tmx_data, item,
                                                       (Settings.TILE_SIZE * 3, Settings.TILE_SIZE * 3))
        sprite_image_in_damage_state = SpriteHelper.get_large_sprite_image(item.name, 1, 0, 3)
        groups = self.level_sprite_groups.the_highest_sprites_layer, self.level_sprite_groups.enemy_sprites
        tile_details = OctopusTileDetails(item, layer)
        OctopusEnemy(sprites, sprite_image_in_damage_state, position, groups, self.game_manager,
                     tile_details, self.obstacle_map, self.level_sprite_groups.obstacle_sprites,
                     self.level_sprite_groups.moving_obstacle_sprites)
