import pygame
import settings

# Base tile size - reference tile size - base on this parameter, all other values are calculated
BASE_TILE_SIZE = 64


def calculate_with_ratio(value: float | int) -> float:
    """
    Calculate a value with ratio.
    The value is multiplied by a factor that adjusts it to the current tile size.

    :param value: raw value
    :return: calculated value
    """
    return value * settings.TILE_SIZE / BASE_TILE_SIZE


def calculate_thickness(value: float | int) -> int:
    """
    Calculate a value with ratio using calculate_with_ratio() function and convert to integer.
    The minimum thickness value is 1.

    :param value: raw value
    :return: calculated value
    """
    thickness = int(calculate_with_ratio(value))
    if thickness < 1:
        thickness = 1
    return thickness


def calculate_frames(time: float | int) -> int:
    """
    Calculate a number of frames in the period of time (provided in milliseconds), taking into account current FPS.

    :param time: period of time (in milliseconds)
    :return: number of frames
    """
    result = (time / 1000) / (1 / settings.FPS)

    return int(result)
