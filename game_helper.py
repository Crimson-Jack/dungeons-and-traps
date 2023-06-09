import pygame
import settings

# Base tile size - reference tile size - base on this parameter, all other values are calculated
BASE_TILE_SIZE = 64


def calculate_ratio(value):
    return value * settings.TILE_SIZE / BASE_TILE_SIZE


def calculate_thickness(value):
    thickness = int(calculate_ratio(value))
    if thickness < 1:
        thickness = 1
    return thickness
