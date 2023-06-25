import settings
import game_helper
import pytmx


def convert_position(position_x, position_y, tile_width, tile_height):
    tile_x = int(position_x // tile_width)
    tile_y = int(position_y // tile_height)
    x = tile_x * settings.TILE_SIZE
    y = tile_y * settings.TILE_SIZE

    return x, y


def get_property(name: str, default, item: pytmx.TiledObject | None, layer: pytmx.TiledObjectGroup | None):
    """
    Get the value from the item if it exists.
    If not, get the value from the layer if it exists.
    Otherwise, return the default value.

    :param name: property name
    :param default: default value
    :param item: item
    :param layer: layer
    :return: property value
    """
    value = default

    if item is not None and item.properties.get(name) is not None:
        value = item.properties.get(name)
    elif layer is not None and layer.properties.get(name) is not None:
        value = layer.properties.get(name)

    return value


def get_frames(tmx_data, item):
    frames = []
    tmx_frames = item.properties.get('frames')

    if tmx_frames is not None:
        for tmx_frame in tmx_frames:
            frames.append((tmx_data.get_tile_image_by_gid(tmx_frame.gid), tmx_frame.duration))
    else:
        # Default duration for one frame is not important
        frames.append((item.image, 0))

    return frames
