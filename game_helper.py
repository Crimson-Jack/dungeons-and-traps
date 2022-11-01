import settings

# Base tile size - base on this parameter, all other speed values are calculated
BASE_TILE_SIZE = 64


def get_speed(speed):
    return speed * settings.TILE_SIZE / BASE_TILE_SIZE
