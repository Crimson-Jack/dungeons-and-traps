from settings import Settings
import pygame


class GameHelper:
    # Base tile size - reference tile size - base on this parameter, all other values are calculated
    BASE_TILE_SIZE = 64

    @staticmethod
    def get_tile_size_ratio() -> float:
        """
        Get the ratio of the current tile size to the base tile size.

        :return: tile size ratio
        """
        return Settings.TILE_SIZE / GameHelper.BASE_TILE_SIZE

    @staticmethod
    def multiply_by_tile_size_ratio(value: float, minimum: float = None) -> float:
        """
        Multiply value by the ratio of the current tile size to the base tile size.
        If result is lower than 'minimum' argument, return the 'minimum' value.

        :param value: raw value
        :param minimum: minimum value
        :return: calculated value
        """
        result: float = value * Settings.TILE_SIZE / GameHelper.BASE_TILE_SIZE

        if minimum is not None and result < minimum:
            result = minimum

        return result

    @staticmethod
    def calculate_frames(time: int) -> int:
        """
        Calculate a number of frames in the period of time (provided in milliseconds), taking into account current FPS.

        :param time: period of time (in milliseconds)
        :return: number of frames
        """
        result = (time / 1000) * Settings.FPS

        return int(result)

    @staticmethod
    def convert_string_to_tuple(value: str, separator: str = ',') -> tuple[int, ...]:
        """
        Return a tuple of integers from the string.

        :param value: input
        :param separator: separator
        :return: tuple of integers
        """
        return tuple(map(int, value.split(separator)))

    @staticmethod
    def convert_string_to_list_of_tuples(value: str, separator: str = '|') -> list[tuple[int, ...]]:
        """
        Return a list of tuples from the string.

        :param value: input
        :param separator: separator
        :return: list of tuples
        """
        return list(map(GameHelper.convert_string_to_tuple, value.split(separator)))

    @staticmethod
    def get_tile_by_point(position: tuple) -> tuple[int, int]:
        """
        Return a tuple with the tile position.

        :param position: tuple with x, y coordinates
        :return: tuple with the tile position
        """
        x_tile = position[0] // Settings.TILE_SIZE
        y_tile = position[1] // Settings.TILE_SIZE

        return x_tile, y_tile

    @staticmethod
    def get_point_by_tile(tile: tuple) -> tuple:
        """
        Return a tuple with the position.

        :param tile: tuple with tile position
        :return: tuple with the x, y coordinates
        """
        x_position = tile[0] * Settings.TILE_SIZE
        y_position = tile[1] * Settings.TILE_SIZE

        return  x_position, y_position

    @staticmethod
    def get_collided_rectangle(rectangle_one: pygame.Rect, rectangle_two: pygame.Rect) -> pygame.Rect:
        """
        Return an intersection of two rectangles in collision.

        :param rectangle_one: first rectangle
        :param rectangle_two: second rectangle
        :return: intersection
        """
        left = max(rectangle_one.left, rectangle_two.left)
        width = min(rectangle_one.right, rectangle_two.right) - left
        top = max(rectangle_one.top, rectangle_two.top)
        height = min(rectangle_one.bottom, rectangle_two.bottom) - top

        return pygame.Rect(left, top, width, height)
