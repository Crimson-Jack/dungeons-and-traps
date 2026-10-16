import random

import pygame
from pytmx.util_pygame import load_pygame

from settings import Settings
from src.events import Events
from src.abstract_classes.pathfinding_enemy import PathfindingEnemy
from src.abstract_classes.obstacle_map_observer import ObstacleMapObserver
from src.enums.enemy_type import EnemyType
from src.effects.blast_effect import BlastEffect
from src.effects.darkness_effect import DarknessEffect
from src.effects.explode_effect import ExplodeEffect
from src.effects.particle_effect_group import ParticleEffectGroup
from src.effects.tilt_effect import TiltEffect
from src.game_helper import GameHelper
from src.game_manager import GameManager
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

    def __init__(self, screen: pygame.Surface, game_surface: pygame.Surface, game_manager: GameManager) -> None:
        # Set screen and game_surface
        self._screen = screen
        self._game_surface = game_surface

        # Set game manager
        self._game_manager = game_manager

        # Load tmx data - world map
        tmx_data = load_pygame(f'data/tmx/{self._game_manager.get_level_filename()}')
        size_of_map = (tmx_data.width, tmx_data.height)

        # Calculate where the game surface is drawn and which part of it is shown
        self._game_surface_position, self._game_surface_rect = GameHelper.calculate_game_surface_area(
            size_of_map,
            self._game_surface.get_size()
        )

        # Set up sprite groups
        self._level_sprite_groups = LevelSpriteGroups(game_surface, size_of_map)

        # Create obstacle map
        self._obstacle_map = ObstacleMapFactory.create(tmx_data)

        # Build the world from the map
        level_sprite_builder = LevelSpriteBuilder(
            tmx_data,
            self._game_manager,
            self._level_sprite_groups,
            self._obstacle_map
        )
        self._player = level_sprite_builder.player
        self._check_point = level_sprite_builder.check_point
        self._exit_point = level_sprite_builder.exit_point
        self._boss_point_position = level_sprite_builder.boss_point_position

        # Tombstones
        self._tombstones = []

        # Vanishing points
        self._vanishing_points = []

        # Blast effect
        self._blast_effect = BlastEffect(
            self._game_surface,
            8,
            Settings.BLAST_EFFECT_COLOR,
            (self._game_surface_rect.width, self._game_surface_rect.height)
        )

        # Explode effect
        self._explode_effect = ExplodeEffect(
            self._game_surface,
            Settings.NUMBER_OF_EXPLOSION_STEPS,
            Settings.EXPLODE_EFFECT_COLOR,
            (Settings.TILE_SIZE * Settings.EXPLOSION_WEAPON_RANGE * 2,
             Settings.TILE_SIZE * Settings.EXPLOSION_WEAPON_RANGE * 2)
        )

        # Darkness effect
        self._darkness_effect = DarknessEffect(self._game_surface_rect.size)

        # Particle effects
        self._particle_effect_group = ParticleEffectGroup(self._game_surface)

        # Tilt effect
        self._tilt_effect = TiltEffect()

        # Create debugger
        self._debugger = Debug()

    def run(self) -> None:
        self._remove_unnecessary_effects()

        # Run an update method for each sprite from the group
        # Note: bottom_background_layer is skipped, because its sprites are static
        self._level_sprite_groups.bottom_sprites_layer.update()
        self._level_sprite_groups.middle_sprites_layer.update()
        self._level_sprite_groups.top_sprites_layer.update()
        self._level_sprite_groups.the_highest_sprites_layer.update()

        # Run an update method for effects
        self._particle_effect_group.update(self._level_sprite_groups.top_sprites_layer.get_map_offset())
        self._blast_effect.update()
        self._explode_effect.update()

        # Clean game surface - fill with background color
        self._game_surface.fill(Settings.GAME_BACKGROUND_COLOR)

        # Draw all visible sprites
        tilt_offset = self._tilt_effect.next_offset()
        self._level_sprite_groups.bottom_background_layer.custom_draw(self._player, tilt_offset)
        self._level_sprite_groups.bottom_sprites_layer.custom_draw(self._player, tilt_offset)
        self._level_sprite_groups.middle_sprites_layer.custom_draw(self._player, tilt_offset)
        self._level_sprite_groups.top_sprites_layer.custom_draw(self._player, tilt_offset)
        self._level_sprite_groups.the_highest_sprites_layer.custom_draw(self._player, tilt_offset)

        # Draw effects
        self._particle_effect_group.draw()
        self._blast_effect.draw()
        self._explode_effect.draw()

        # Blit game_surface on the main screen
        self._screen.blit(self._game_surface, self._game_surface_position, self._game_surface_rect)
        # Blit dark_surface on the main screen
        self._blit_dark_surface()

        # Read inputs and display variables if debugger is enabled
        self._debugger.input()
        self._debugger.show()

    def refresh_obstacle_map(self) -> None:
        # Refresh obstacle map if is required
        self._obstacle_map.calculate_regions()

        for sprite in self._level_sprite_groups.enemy_sprites.sprites():
            if isinstance(sprite, ObstacleMapObserver):
                sprite.refresh_obstacle_map()
        for sprite in self._level_sprite_groups.hostile_force_sprites.sprites():
            if isinstance(sprite, ObstacleMapObserver):
                sprite.refresh_obstacle_map()

    def inform_about_player_tile_position(self) -> None:
        for sprite in self._level_sprite_groups.enemy_sprites.sprites():
            if isinstance(sprite, PathfindingEnemy):
                sprite.set_player_tile_position()

    def show_exit_point(self) -> None:
        if self._exit_point is None:
            raise ValueError('The exit point is missing. Add a visible "exit-point" object to the map.')
        self._blast_effect.run()
        self._exit_point.show()

    def show_explode_effect(self, position: tuple[int, int]) -> None:
        self._explode_effect.run(position)

    def add_tombstone(self, position: tuple[int, int]) -> None:
        sprites = SpriteHelper.get_all_tombstone_sprites()
        self._tombstones.append(Tombstone(sprites, position, (self._level_sprite_groups.bottom_sprites_layer,)))

    def add_boss_tombstone(self, position: tuple[int, int]) -> None:
        sprites = SpriteHelper.get_all_boss_tombstone_sprites()
        self._tombstones.append(Tombstone(sprites, position, (self._level_sprite_groups.bottom_sprites_layer,), 0))

    def add_vanishing_point(self, position: tuple[int, int]) -> None:
        self._vanishing_points.append(VanishingPoint(position, (self._level_sprite_groups.bottom_sprites_layer,)))

    def create_egg(self, position: tuple[int, int]) -> None:
        Egg(position, (self._level_sprite_groups.bottom_sprites_layer, self._level_sprite_groups.collectable_sprites),
            self._game_manager)

    def create_monster(self, position: tuple[int, int]) -> None:
        name = random.choice(['monster-enemy-blue-deaf', 'monster-enemy-green-deaf', 'monster-enemy-red-deaf'])
        tile_details = MonsterTileDetailsFactory.create(name)

        sprite_costumes = SpriteCostume.create_list(SpriteHelper.get_all_monster_sprites(name),
                                                    self.SPAWNED_ENEMY_NUMBER_OF_FRAMES)
        sprite_image_in_damage_state = SpriteHelper.get_sprite_image(name, 1, 0)

        groups = self._level_sprite_groups.top_sprites_layer, self._level_sprite_groups.enemy_sprites

        enemy_type = EnemyType.from_name(name)
        MonsterEnemy(sprite_costumes, sprite_image_in_damage_state, position, groups, self._game_manager,
                     enemy_type, tile_details, self._obstacle_map,
                     self._level_sprite_groups.obstacle_sprites, self._level_sprite_groups.moving_obstacle_sprites,
                     self._level_sprite_groups.hostile_force_sprites)
        self._game_manager.level_stats[-1].record_enemy_spawn(enemy_type)

    def create_boss_octopus(self) -> None:
        if self._boss_point_position is None:
            raise ValueError('The boss point is missing. Add a visible "boss-point" object to the map.')

        name = 'octopus-enemy'
        tile_details = OctopusTileDetails(None, None)

        sprite_costumes = SpriteCostume.create_list(SpriteHelper.get_all_octopus_sprites(name),
                                                    self.SPAWNED_ENEMY_NUMBER_OF_FRAMES)
        sprite_image_in_damage_state = SpriteHelper.get_large_sprite_image(name, 1, 0, 3)

        groups = self._level_sprite_groups.the_highest_sprites_layer, self._level_sprite_groups.enemy_sprites

        OctopusEnemy(sprite_costumes, sprite_image_in_damage_state, self._boss_point_position, groups,
                     self._game_manager,
                     tile_details, self._obstacle_map, self._level_sprite_groups.obstacle_sprites,
                     self._level_sprite_groups.moving_obstacle_sprites)

        self._game_manager.boss_max_energy = tile_details.energy
        self._game_manager.boss_energy = tile_details.energy
        self._game_manager.is_boss_visible = True

    def add_particle_effect(self, position: tuple[int, int], number_of_sparks: int,
                            colors: list[tuple[int, int, int]]) -> None:
        self._particle_effect_group.add(position, number_of_sparks, colors)

    def add_spark_to_particle_effect(self) -> None:
        self._particle_effect_group.add_spark()

    def show_player_tombstone(self) -> None:
        self._player.disable()
        self._player.trigger_tombstone_creation()

    def show_player_vanishing_point(self) -> None:
        self._player.disable()
        self._player.trigger_vanishing_point_creation()

    def respawn_player(self, position: tuple[int, int] | None = None) -> None:
        if position is None:
            position = self._game_manager.get_check_point_position()
        self._player.respawn(position)
        self._player.enable()

    def remove_obstacles(self) -> None:
        if len(self._level_sprite_groups.removable_obstacle_sprites) > 0:
            for sprite in self._level_sprite_groups.removable_obstacle_sprites:
                sprite.kill()
            # Raise event to refresh obstacle map
            pygame.event.post(pygame.event.Event(Events.REFRESH_OBSTACLE_MAP_EVENT))

    def enable_tilt_effect(self, tilt_cursor_increment_value: float | None = None) -> None:
        self._tilt_effect.enable(tilt_cursor_increment_value)

    def _remove_unnecessary_effects(self) -> None:
        remaining_tombstones = []
        for tombstone in self._tombstones:
            if tombstone.is_expired():
                tombstone.kill()
            else:
                remaining_tombstones.append(tombstone)
        self._tombstones = remaining_tombstones

        remaining_vanishing_points = []
        for vanishing_point in self._vanishing_points:
            if vanishing_point.is_expired():
                vanishing_point.kill()
            else:
                remaining_vanishing_points.append(vanishing_point)
        self._vanishing_points = remaining_vanishing_points

        self._particle_effect_group.remove_expired()

    def _blit_dark_surface(self) -> None:
        # Calculate the position of the player on the game surface
        offset = self._level_sprite_groups.middle_sprites_layer.get_map_offset()
        player_rect = self._player.rect
        assert player_rect is not None, 'The player has no rect'
        light_center = (player_rect.centerx + offset.x, player_rect.centery + offset.y)

        self._darkness_effect.draw(self._screen, self._game_surface_position, self._game_manager.lighting_status,
                                  light_center)
