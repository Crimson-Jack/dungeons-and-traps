import settings
import pygame

# Base tile size - reference tile size - base on this parameter, all other values are calculated
BASE_TILE_SIZE = 64


def get_tile_size_ratio() -> float:
    """
    Get the ratio of the current tile size to the base tile size.

    :return: tile size ratio
    """
    return settings.TILE_SIZE / BASE_TILE_SIZE


def multiply_by_tile_size_ratio(value: float | int, minimum: float | int | None = None) -> float:
    """
    Multiply value by the ratio of the current tile size to the base tile size.
    If result is lower than 'minimum' argument, return the 'minimum' value.

    :param value: raw value
    :param minimum: minimum value
    :return: calculated value
    """
    result = value * settings.TILE_SIZE / BASE_TILE_SIZE

    if minimum is not None and result < minimum:
        result = minimum

    return result


def calculate_frames(time: float | int) -> int:
    """
    Calculate a number of frames in the period of time (provided in milliseconds), taking into account current FPS.

    :param time: period of time (in milliseconds)
    :return: number of frames
    """
    result = (time / 1000) / (1 / settings.FPS)

    return int(result)


def convert_string_to_tuple(value, separator=','):
    """
    Return a tuple of integers from the string.

    :param value: input
    :param separator: separator
    :return: tuple of integers
    """
    return tuple(map(int, value.split(separator)))


def get_tile_by_point(position: tuple):
    """
    Return a tuple with the tile position.

    :param position: tuple with x, y coordinates
    :return: tuple with the tile position
    """
    x_tile = position[0] // settings.TILE_SIZE
    y_tile = position[1] // settings.TILE_SIZE

    return x_tile, y_tile


def get_collided_rectangle(rectangle_one, rectangle_two):
    left = max(rectangle_one.left, rectangle_two.left)
    width = min(rectangle_one.right, rectangle_two.right) - left
    top = max(rectangle_one.top, rectangle_two.top)
    height = min(rectangle_one.bottom, rectangle_two.bottom) - top

    return pygame.Rect(left, top, width, height)
