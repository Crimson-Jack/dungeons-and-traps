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
from src.effects.tilt_effect import TiltEffect
from src.enums.lighting_status import LightingStatus
from src.game_helper import GameHelper
from src.level_sprite_builder import LevelSpriteBuilder
from src.level_sprite_groups import LevelSpriteGroups
from src.obstacle_map_factory import ObstacleMapFactory
from src.factories.monster_tile_details_factory import MonsterTileDetailsFactory
from src.sprites.egg import Egg
from src.sprites.monster_enemy import MonsterEnemy
from src.sprites.octopus_enemy import OctopusEnemy
from src.sprites.tombstone import Tombstone
from src.sprites.vanishing_point import VanishingPoint
from src.sprite_costume import SpriteCostume
from src.sprite_helper import SpriteHelper
from src.tile_details.octopus_tile_details import OctopusTileDetails
from src.utilities.debug import Debug


class Level:
    # Number of game frames each costume of the enemies created during play (monster from an egg, boss) is shown
    SPAWNED_ENEMY_NUMBER_OF_FRAMES = 6

    def __init__(self, screen, game_surface, game_manager):
        # Set screen and game_surface
        self.screen = screen
        self.game_surface = game_surface

        # Set game manager
        self.game_manager = game_manager

        # Load tmx data - world map
        tmx_data = load_pygame(f'data/tmx/{self.game_manager.get_level_filename()}')
        size_of_map = (tmx_data.width, tmx_data.height)

        # Calculate where the game surface is drawn and which part of it is shown
        self.game_surface_position, self.game_surface_rect = GameHelper.calculate_game_surface_area(
            size_of_map, self.game_surface.get_size())

        # Set up sprite groups
        self.level_sprite_groups = LevelSpriteGroups(game_surface, size_of_map)

        # Create obstacle map
        self.obstacle_map = ObstacleMapFactory.create(tmx_data)

        # Build the world from the map
        level_sprite_builder = LevelSpriteBuilder(tmx_data, self.game_manager, self.level_sprite_groups,
                                                  self.obstacle_map)
        self.player = level_sprite_builder.player
        self.check_point = level_sprite_builder.check_point
        self.exit_point = level_sprite_builder.exit_point
        self.boss_point_position = level_sprite_builder.boss_point_position

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

        # Tilt effect
        self.tilt_effect = TiltEffect()

        # Create debugger
        self.debugger = Debug()

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
        tilt_offset = self.tilt_effect.next_offset()
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
            player_rect = self.player.rect
            assert player_rect is not None, 'The player has no rect'
            circle_x = player_rect.centerx + offset.x
            circle_y = player_rect.centery + offset.y

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
        if self.exit_point is None:
            raise ValueError('The exit point is missing. Add a visible "exit-point" object to the map.')
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

        sprite_costumes = SpriteCostume.create_list(SpriteHelper.get_all_monster_sprites(name),
                                                    self.SPAWNED_ENEMY_NUMBER_OF_FRAMES)
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

        sprite_costumes = SpriteCostume.create_list(SpriteHelper.get_all_octopus_sprites(name),
                                                    self.SPAWNED_ENEMY_NUMBER_OF_FRAMES)
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

    def enable_tilt_effect(self, tilt_cursor_increment_value: float | None = None):
        self.tilt_effect.enable(tilt_cursor_increment_value)
