import pygame
import settings

# Base tile size - reference tile size - base on this parameter, all other values are calculated
BASE_TILE_SIZE = 64


def multiply_by_tile_size_ratio(value: float | int, minimum: float | int | None = None) -> float:
    """
    Return argument multiplied by a factor that adjusts it to the current tile size.
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


def convert_to_tuple_decorator(func_name):
    """
    Return a wrapper where the result (string with coma separator) is converted to a tuple.

    :param func_name: function name
    :return: wrapper
    """
    def wrapper(*args):
        func_result = func_name(*args)
        result = tuple(map(int, func_result.split(',')))
        return result
    return wrapper


def convert_to_tile_size_ratio_decorator(func_name):
    """
    Return a wrapper where the result is multiplied by the tile size ratio.

    :param func_name: function name
    :return: wrapper
    """
    def wrapper(*args):
        func_result = func_name(*args)
        result = multiply_by_tile_size_ratio(func_result)
        return result
    return wrapper


def calculate_game_surface_position(game_surface_width, game_surface_height, map_width, map_height):
    position = [0, 0]

    if map_width < game_surface_width:
        position[0] = (game_surface_width - map_width) // 2

    if map_height < game_surface_height:
        position[1] = (game_surface_height - map_height) // 2

    return tuple(position)
