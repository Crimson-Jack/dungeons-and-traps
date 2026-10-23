import pytmx

from settings import Settings
from src.enums.enemy_type import EnemyType
from src.game_helper import GameHelper
from src.game_manager import GameManager
from src.level_sprite_groups import LevelSpriteGroups
from src.obstacle_map import ObstacleMap
from src.factories.powerup_factory import PowerupFactory
from src.sprites.bat_enemy import BatEnemy
from src.sprites.check_point import CheckPoint
from src.sprites.demolished_wall import DemolishedWall
from src.sprites.diamond import Diamond
from src.sprites.door import Door
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
from src.sprites.wall import Wall
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


class LevelSpriteBuilder:
    """Builds the world of a level from a TMX map: sprites from layers, player and special points."""

    def __init__(self, tmx_data: pytmx.TiledMap, game_manager: GameManager,
                 level_sprite_groups: LevelSpriteGroups, obstacle_map: ObstacleMap) -> None:
        """
        Build the whole world from the map: the sprites from all layers, the player, the check point,
        the exit point and the boss point position.
        The results are available in the read-only properties player, check_point, exit_point
        and boss_point_position.

        :param tmx_data: loaded TMX map
        :param game_manager: shared game state
        :param level_sprite_groups: sprite groups the created sprites are added to
        :param obstacle_map: obstacle map passed to stones, doors, demolished walls and enemies
        """
        self._tmx_data = tmx_data
        self._game_manager = game_manager
        self._level_sprite_groups = level_sprite_groups
        self._obstacle_map = obstacle_map
        self._powerup_factory = PowerupFactory()

        self._create_sprites()
        self._player = self._create_player()
        self._check_point = self._create_check_point()
        self._exit_point = self._create_exit_point()
        self._boss_point_position = self._get_boss_point_position()

    @property
    def player(self) -> Player:
        return self._player

    @property
    def check_point(self) -> CheckPoint | None:
        return self._check_point

    @property
    def exit_point(self) -> ExitPoint | None:
        return self._exit_point

    @property
    def boss_point_position(self) -> tuple[int, int] | None:
        return self._boss_point_position

    def _create_sprites(self):
        self._create_sprites_from_layer('ground', self._create_ground)
        self._create_sprites_from_layer('diamond', self._create_diamond)
        self._create_sprites_from_layer('obstacle', self._create_wall)
        self._create_sprites_from_layer('moving-obstacle', self._create_stone)
        self._create_sprites_from_layer('removable-obstacle', self._create_demolished_wall)
        self._create_sprites_from_object_layer('spell', self._create_lighting_spell)
        self._create_sprites_from_object_layer('powerup', self._create_powerup)
        self._create_sprites_from_object_layer('key', self._create_key)
        self._create_sprites_from_object_layer('fire-flame-enemy', self._create_fire_flame_enemy)
        self._create_sprites_from_object_layer('door', self._create_door)
        self._create_sprites_from_object_layer('teleport', self._create_teleport)
        self._create_sprites_from_object_layer('monster-enemy', self._create_monster_enemy)
        self._create_sprites_from_object_layer('spider-enemy', self._create_spider_enemy)
        self._create_sprites_from_object_layer('ghost-enemy', self._create_ghost_enemy)
        self._create_sprites_from_object_layer('bat-enemy', self._create_bat_enemy)
        self._create_sprites_from_object_layer('octopus-enemy', self._create_octopus_enemy)

    def _create_sprites_from_layer(self, layer_name, create_sprite):
        layer: pytmx.TiledTileLayer | None = self._get_visible_layer(layer_name)
        if layer is not None:
            for tile_x, tile_y, image in layer.tiles():
                position = (tile_x * Settings.TILE_SIZE, tile_y * Settings.TILE_SIZE)
                create_sprite(image, layer, position)

    def _create_sprites_from_object_layer(self, layer_name, create_sprite):
        layer: pytmx.TiledObjectGroup | None = self._get_visible_layer(layer_name)
        if layer is not None:
            for item in layer:
                if item.visible:
                    position = TmxHelper.get_tile_position(item.x, item.y, self._tmx_data.tilewidth,
                                                           self._tmx_data.tileheight, item.rotation)
                    create_sprite(item, layer, position)

    def _create_player(self) -> Player:
        player_object = self._get_visible_object('player')
        if player_object is None:
            raise ValueError('The player is missing. Add a visible "player" object to the map.')

        position = TmxHelper.get_tile_position(player_object.x, player_object.y,
                                               self._tmx_data.tilewidth, self._tmx_data.tileheight)
        speed = GameHelper.multiply_by_tile_size_ratio(
            TmxHelper.get_tiled_object_value('speed', 7, player_object, None))
        return Player(position,
                      (self._level_sprite_groups.middle_sprites_layer,),
                      [self._level_sprite_groups.middle_sprites_layer],
                      speed,
                      self._level_sprite_groups.exit_points,
                      self._level_sprite_groups.obstacle_sprites,
                      self._level_sprite_groups.moving_obstacle_sprites,
                      self._level_sprite_groups.passage_sprites,
                      self._level_sprite_groups.teleport_sprites,
                      self._level_sprite_groups.collectable_sprites,
                      self._level_sprite_groups.enemy_sprites,
                      self._level_sprite_groups.hostile_force_sprites,
                      self._game_manager)

    def _create_check_point(self):
        check_point = self._get_visible_object('check-point')
        if check_point is None:
            return None

        position = TmxHelper.get_tile_position(check_point.x, check_point.y,
                                               self._tmx_data.tilewidth, self._tmx_data.tileheight)
        groups = self._level_sprite_groups.bottom_background_layer, self._level_sprite_groups.collectable_sprites
        return CheckPoint(check_point.image, position, groups, self._game_manager)

    def _create_exit_point(self):
        exit_object = self._get_visible_object('exit-point')
        if exit_object is None:
            return None

        position = TmxHelper.get_tile_position(exit_object.x, exit_object.y,
                                               self._tmx_data.tilewidth, self._tmx_data.tileheight)
        groups = self._level_sprite_groups.bottom_background_layer, self._level_sprite_groups.exit_points
        return ExitPoint(exit_object.image, position, groups, False)

    def _get_boss_point_position(self):
        boss_object = self._get_visible_object('boss-point')
        if boss_object is None:
            return None

        return TmxHelper.get_tile_position(boss_object.x, boss_object.y,
                                           self._tmx_data.tilewidth, self._tmx_data.tileheight)

    def _get_visible_object(self, name):
        try:
            tiled_object = self._tmx_data.get_object_by_name(name)
        except (KeyError, ValueError):
            return None
        return tiled_object if tiled_object.visible else None

    def _get_visible_layer(self, name):
        for layer in self._tmx_data.visible_layers:
            if layer.name == name:
                return layer
        return None

    def _create_ground(self, image, _layer, position):
        groups = (self._level_sprite_groups.bottom_background_layer,)
        Ground(image, position, groups)

    def _create_diamond(self, image, layer, position):
        groups = self._level_sprite_groups.bottom_sprites_layer, self._level_sprite_groups.collectable_sprites
        tile_details = DiamondTileDetails(None, layer)
        self._game_manager.add_diamond(Diamond(image, position, groups, self._game_manager, tile_details))

    def _create_wall(self, image, _layer, position):
        groups = self._level_sprite_groups.middle_sprites_layer, self._level_sprite_groups.obstacle_sprites
        Wall(image, position, groups)

    def _create_stone(self, image, _layer, position):
        groups = self._level_sprite_groups.middle_sprites_layer, self._level_sprite_groups.moving_obstacle_sprites
        collision_sprites = [self._level_sprite_groups.enemy_sprites,
                             self._level_sprite_groups.obstacle_sprites,
                             self._level_sprite_groups.moving_obstacle_sprites,
                             self._level_sprite_groups.collectable_sprites]
        # Note: stone can be moved, so the list instead of tuple for position is used
        Stone(image, list(position), groups, self._game_manager, self._obstacle_map.items, collision_sprites)

    def _create_demolished_wall(self, image, _layer, position):
        groups = (self._level_sprite_groups.middle_sprites_layer, self._level_sprite_groups.obstacle_sprites,
                  self._level_sprite_groups.removable_obstacle_sprites)
        DemolishedWall(image, position, groups, self._obstacle_map.items)

    def _create_lighting_spell(self, item, layer, position):
        groups = self._level_sprite_groups.bottom_sprites_layer, self._level_sprite_groups.collectable_sprites
        tile_details = SpellTileDetails(item, layer)
        LightingSpell(item.image, position, groups, self._game_manager, tile_details)

    def _create_powerup(self, item, layer, position):
        groups = self._level_sprite_groups.bottom_sprites_layer, self._level_sprite_groups.collectable_sprites
        tile_details = PowerupTileDetails(item, layer)
        self._powerup_factory.create(tile_details,
                                    image=item.image,
                                    position=position,
                                    groups=groups,
                                    game_manager=self._game_manager)

    def _create_key(self, item, layer, position):
        groups = self._level_sprite_groups.bottom_sprites_layer, self._level_sprite_groups.collectable_sprites
        tile_details = KeyAndDoorTileDetails(item, layer)
        self._game_manager.add_key(Key(item.image, position, groups, self._game_manager, tile_details))

    def _create_fire_flame_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self._tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        groups = self._level_sprite_groups.bottom_sprites_layer, self._level_sprite_groups.hostile_force_sprites
        tile_details = FireFlameTileDetails(item, layer)
        if tile_details.direction == 'left':
            FireFlameEnemyLeft(sprites, position, groups, tile_details,
                               self._level_sprite_groups.moving_obstacle_sprites)
        elif tile_details.direction == 'right':
            FireFlameEnemyRight(sprites, position, groups, tile_details,
                                self._level_sprite_groups.moving_obstacle_sprites)

    def _create_door(self, item, layer, position):
        groups = (self._level_sprite_groups.middle_sprites_layer, self._level_sprite_groups.obstacle_sprites,
                  self._level_sprite_groups.passage_sprites)
        tile_details = KeyAndDoorTileDetails(item, layer)
        Door(item.image, position, groups, tile_details, self._obstacle_map.items)

    def _create_teleport(self, item, layer, position):
        groups = self._level_sprite_groups.bottom_sprites_layer, self._level_sprite_groups.teleport_sprites
        tile_details = TeleportTileDetails(item, layer)
        Teleport(item.image, position, groups, tile_details)

    def _create_monster_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self._tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        sprite_image_in_damage_state = SpriteHelper.get_sprite_image(item.name, 1, 0)
        groups = self._level_sprite_groups.top_sprites_layer, self._level_sprite_groups.enemy_sprites
        tile_details = MonsterTileDetails(item, layer)
        enemy_type = EnemyType.from_name(item.name)
        MonsterEnemy(sprites, sprite_image_in_damage_state, position, groups, self._game_manager,
                     enemy_type, tile_details, self._obstacle_map,
                     self._level_sprite_groups.obstacle_sprites, self._level_sprite_groups.moving_obstacle_sprites,
                     self._level_sprite_groups.hostile_force_sprites)
        self._game_manager.record_enemy_spawn(enemy_type)

    def _create_spider_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self._tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        sprite_costumes_matrix = SpriteHelper.get_sprite_costumes_matrix(item.name, sprites)
        groups = self._level_sprite_groups.top_sprites_layer, self._level_sprite_groups.enemy_sprites
        tile_details = SpiderTileDetails(item, layer)
        enemy_type = EnemyType.from_name(item.name)
        SpiderEnemy(sprite_costumes_matrix, position, groups, self._game_manager,
                    enemy_type, tile_details, self._level_sprite_groups.moving_obstacle_sprites)
        self._game_manager.record_enemy_spawn(enemy_type)

    def _create_ghost_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self._tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        groups = self._level_sprite_groups.top_sprites_layer, self._level_sprite_groups.enemy_sprites
        tile_details = GhostTileDetails(item, layer)
        GhostEnemy(sprites, position, groups, tile_details, self._obstacle_map.items,
                   self._level_sprite_groups.moving_obstacle_sprites)

    def _create_bat_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self._tmx_data, item, (Settings.TILE_SIZE, Settings.TILE_SIZE))
        sprite_image_in_damage_state = SpriteHelper.get_sprite_image(item.name, 1, 0)
        groups = self._level_sprite_groups.top_sprites_layer, self._level_sprite_groups.enemy_sprites
        tile_details = BatTileDetails(item, layer)
        enemy_type = EnemyType.from_name(item.name)
        BatEnemy(sprites, sprite_image_in_damage_state, position, groups, self._game_manager,
                 enemy_type, tile_details, self._obstacle_map,
                 self._level_sprite_groups.moving_obstacle_sprites, self._level_sprite_groups.hostile_force_sprites)
        self._game_manager.record_enemy_spawn(enemy_type)

    def _create_octopus_enemy(self, item, layer, position):
        sprites = TmxHelper.convert_to_sprite_costumes(self._tmx_data, item,
                                                       (Settings.TILE_SIZE * 3, Settings.TILE_SIZE * 3))
        sprite_image_in_damage_state = SpriteHelper.get_large_sprite_image(item.name, 1, 0, 3)
        groups = self._level_sprite_groups.the_highest_sprites_layer, self._level_sprite_groups.enemy_sprites
        tile_details = OctopusTileDetails(item, layer)
        OctopusEnemy(sprites, sprite_image_in_damage_state, position, groups, self._game_manager,
                     tile_details, self._obstacle_map, self._level_sprite_groups.obstacle_sprites,
                     self._level_sprite_groups.moving_obstacle_sprites)
