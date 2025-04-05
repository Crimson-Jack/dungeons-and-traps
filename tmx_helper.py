import settings


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


def convert_position(position_x, position_y, tile_width, tile_height, rotation=0):
    tile_x = int(position_x // tile_width)
    tile_y = int(position_y // tile_height)
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


# def get_property(name: str, default, item: pytmx.TiledObject | None, layer: pytmx.TiledObjectGroup | None):
def get_property(name: str, default, item, layer):
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
            frames.append([tmx_data.get_tile_image_by_gid(tmx_frame.gid), tmx_frame.duration])
    else:
        # Default duration for one frame is not important
        frames.append((item.image, 0))

    return frames
