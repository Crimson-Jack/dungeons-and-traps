from typing import Any

import pygame
import pytmx

from settings import Settings
from src.game_helper import GameHelper
from src.sprite_costume import SpriteCostume


class TmxHelper:
    """
    Static helpers that read data from a TMX map: object grids, tile positions, property values
    and animation frames.
    """

    @staticmethod
    def get_data_map_by_layer(layer: pytmx.TiledObjectGroup | None, size_of_map: tuple[int, int],
                              tile_width: int, tile_height: int) -> list[list[int]]:
        """
        Create a grid that marks the tiles occupied by the objects of the layer.

        :param layer: group of tiled objects; None gives a grid of zeros
        :param size_of_map: map size in tiles (width, height)
        :param tile_width: tile width of the TMX map in pixels
        :param tile_height: tile height of the TMX map in pixels
        :return: grid indexed [row][column], 1 for a tile with an object, 0 otherwise
        """
        rows = list()
        for row_counter in range(0, size_of_map[1]):
            columns = list()
            for columns_counter in range(0, size_of_map[0]):
                columns.append(0)
            rows.append(columns)

        if layer is not None:
            for item in layer:
                tile_x = int(item.x // tile_width)
                tile_y = int(item.y // tile_height)
                rows[tile_y][tile_x] = 1

        return rows

    @staticmethod
    def get_tile_position(x: float, y: float, width: int, height: int, rotation: float = 0) -> tuple[int, int]:
        """
        Convert the position of a TMX object to the top left corner of its tile on the screen.
        The position is corrected by the rotation of the object.

        :param x: x coordinate of the object in TMX map pixels
        :param y: y coordinate of the object in TMX map pixels
        :param width: tile width of the TMX map in pixels
        :param height: tile height of the TMX map in pixels
        :param rotation: rotation of the object in degrees, clockwise
        :return: top left corner of the tile in screen pixels (Settings.TILE_SIZE)
        """
        tile_x = int(x // width)
        tile_y = int(y // height)
        x = tile_x * Settings.TILE_SIZE
        y = tile_y * Settings.TILE_SIZE

        # According to the tmx format, rotation causes the object to move clockwise around the point 0, 0, which is the
        # bottom left corner of the tile.
        # Original baseline values do not correspond to visible on the map therefore they need to be corrected.
        if rotation == 90 or rotation == -270:
            y = y + Settings.TILE_SIZE
        elif rotation == 180 or rotation == -180:
            x = x - Settings.TILE_SIZE
            y = y + Settings.TILE_SIZE
        elif rotation == 270 or rotation == -90:
            x = x - Settings.TILE_SIZE

        return x, y

    @staticmethod
    def get_tiled_object_value(name: str, default: Any, tiled_object: pytmx.TiledObject,
                               layer: pytmx.TiledObjectGroup | None) -> Any:
        """
        Get the property value of the tiled object.
        If the object does not have it, get the value from the layer (group of tiled objects).
        If neither has it, return the default value. A property set to None counts as missing.

        :param name: property name
        :param default: value returned when neither the object nor the layer has the property
        :param tiled_object: tiled object; can be None
        :param layer: group of tiled objects; can be None
        :return: property value
        """
        value = default

        if tiled_object is not None and tiled_object.properties.get(name) is not None:
            value = tiled_object.properties.get(name)
        elif layer is not None and layer.properties.get(name) is not None:
            value = layer.properties.get(name)

        return value

    @staticmethod
    def convert_to_sprite_costumes(tiled_map: pytmx.TiledMap, tiled_object: pytmx.TiledObject,
                                   size: tuple[float, float] | None = None) -> list[SpriteCostume]:
        """
        Convert the animation frames of the tiled object (the 'frames' property) to sprite costumes.
        Each frame gives the tile image of its gid and the number of game frames for its duration.

        :param tiled_map: tiled map with the tile images
        :param tiled_object: tiled object with the animation frames
        :param size: size the images are scaled to; None keeps the original size
        :return: sprite costumes in the order of the frames; empty if the object has no frames
        """
        sprite_costumes = list()
        tmx_frames = tiled_object.properties.get('frames')

        if tmx_frames is not None:
            for tmx_frame in tmx_frames:
                image = tiled_map.get_tile_image_by_gid(tmx_frame.gid)
                if size is not None:
                    image = pygame.transform.scale(image, size)
                sprite_costumes.append(
                    SpriteCostume(image, GameHelper.calculate_frames(tmx_frame.duration))
                )

        return sprite_costumes
