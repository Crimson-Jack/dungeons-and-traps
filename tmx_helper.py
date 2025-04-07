import pytmx
import settings
import game_helper
from sprite_costume import SpriteCostume


def get_object_group_data_map(object_group, size_of_map, tile_width, tile_height):
    rows = list()
    for row_counter in range(0, size_of_map[1]):
        columns = list()
        for columns_counter in range(0, size_of_map[0]):
            columns.append(0)
        rows.append(columns)

    if object_group is not None:
        for item in object_group:
            tile_x = int(item.x // tile_width)
            tile_y = int(item.y // tile_height)
            rows[tile_y][tile_x] = 1

    return rows


def get_tile_position(x: float, y: float, width: int, height: int, rotation: int=0) -> tuple[int, int]:
    """
    Get tile position, based on x, y coordinates and rotation.

    :param x: x coordinate
    :param y: y coordinate
    :param width: width
    :param height: height
    :param rotation: rotation
    :return: tile position
    """
    tile_x = int(x // width)
    tile_y = int(y // height)
    x = tile_x * settings.TILE_SIZE
    y = tile_y * settings.TILE_SIZE

    # According to the tmx format, rotation causes the object to move clockwise around the point 0, 0, which is the
    # bottom left corner of the tile.
    # Original baseline values do not correspond to visible on the map therefore they need to be corrected.
    if rotation == 90 or rotation == -270:
        y = y + settings.TILE_SIZE
    elif rotation == 180 or rotation == -180:
        x = x - settings.TILE_SIZE
        y = y + settings.TILE_SIZE
    elif rotation == 270 or rotation == -90:
        x = x - settings.TILE_SIZE

    return x, y


def get_tiled_object_value(name: str, default, item: pytmx.TiledObject, layer: pytmx.TiledObjectGroup):
    """
    Get the value from the item (tile object) if it exists.
    If not, get the value from the layer (tile object group) if it exists.
    Otherwise, return the default value.

    :param name: property name
    :param default: default value
    :param item: tile object
    :param layer: group of tile objects
    :return: property value
    """
    value = default

    if item is not None and item.properties.get(name) is not None:
        value = item.properties.get(name)
    elif layer is not None and layer.properties.get(name) is not None:
        value = layer.properties.get(name)

    return value


def get_sprite_costumes(tmx_data: pytmx.TiledMap, tiled_object: pytmx.TiledObjectGroup) -> list[SpriteCostume]:
    """
    Get each id and duration from the tiled object and create a sprite costume object with an image and number of frames.

    :param tmx_data: tile map
    :param tiled_object: tiled object
    :return: list of sprite costumes
    """
    frames = list()
    tmx_frames = tiled_object.properties.get('frames')

    if tmx_frames is not None:
        for tmx_frame in tmx_frames:
            frames.append(
                SpriteCostume(tmx_data.get_tile_image_by_gid(tmx_frame.gid),
                              game_helper.calculate_frames(tmx_frame.duration))
            )

    return frames
