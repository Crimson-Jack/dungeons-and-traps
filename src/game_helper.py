import pygame

from settings import Settings


class GameHelper:
    """
    Static helpers for scaling values to the tile size, converting time to frames, converting strings
    from map properties to tuples, converting between points and tiles, and calculating rectangles.
    """

    # Tile size in pixels that the hardcoded sizes, speeds and offsets in the code are written for.
    # multiply_by_tile_size_ratio() scales them to the real tile size, e.g. with Settings.TILE_SIZE = 48
    # the ratio is 48 / 64 = 0.75, so a speed of 4 written in the code becomes 3.
    BASE_TILE_SIZE: int = 64

    @staticmethod
    def get_tile_size_ratio() -> float:
        """
        Get the ratio of the current tile size to the base tile size.

        :return: tile size ratio
        """
        return Settings.TILE_SIZE / GameHelper.BASE_TILE_SIZE

    @staticmethod
    def multiply_by_tile_size_ratio(value: float, minimum: float | None = None) -> float:
        """
        Multiply value by the ratio of the current tile size to the base tile size.
        If result is lower than 'minimum' argument, return the 'minimum' value.

        :param value: raw value
        :param minimum: minimum value
        :return: calculated value
        """
        result = value * GameHelper.get_tile_size_ratio()

        if minimum is not None:
            result = max(result, minimum)

        return result

    @staticmethod
    def calculate_frames(milliseconds: int) -> int:
        """
        Calculate the number of frames shown at the current FPS in the period of time.

        :param milliseconds: period of time in milliseconds
        :return: number of frames, rounded down
        """
        return int(milliseconds / 1000 * Settings.FPS)

    @staticmethod
    def convert_string_to_tuple(value: str, separator: str = ',') -> tuple[int, ...]:
        """
        Convert a string of integers to a tuple, e.g. '1,2,3' -> (1, 2, 3).

        :param value: integers separated by the separator
        :param separator: text between the integers
        :return: tuple of integers
        """
        return tuple(map(int, value.split(separator)))

    @staticmethod
    def convert_string_to_list_of_tuples(value: str, separator: str = '|') -> list[tuple[int, ...]]:
        """
        Convert a string of integer groups to a list of tuples, e.g. '1,2|3,4' -> [(1, 2), (3, 4)].
        The integers inside a group are separated by a comma.

        :param value: groups of integers separated by the separator
        :param separator: text between the groups
        :return: list of tuples of integers
        """
        return list(map(GameHelper.convert_string_to_tuple, value.split(separator)))

    @staticmethod
    def get_tile_by_point(position: tuple[int, int]) -> tuple[int, int]:
        """
        Return a tuple with the tile position.

        :param position: tuple with x, y coordinates
        :return: tuple with the tile position
        """
        x_tile = position[0] // Settings.TILE_SIZE
        y_tile = position[1] // Settings.TILE_SIZE

        return x_tile, y_tile

    @staticmethod
    def get_point_by_tile(tile: tuple[int, int]) -> tuple[int, int]:
        """
        Return a tuple with the position.

        :param tile: tuple with the tile position
        :return: tuple with the x, y coordinates
        """
        x_position = tile[0] * Settings.TILE_SIZE
        y_position = tile[1] * Settings.TILE_SIZE

        return x_position, y_position

    @staticmethod
    def get_tile_center_position(tile: tuple[int, int]) -> tuple[int, int]:
        """
        Return a tuple with the tile center position.

        :param tile: tuple with the tile position
        :return: tuple with the tile center position
        """
        x_position, y_position = GameHelper.get_point_by_tile(tile)
        half_tile_size = Settings.TILE_SIZE // 2

        return x_position + half_tile_size, y_position + half_tile_size

    @staticmethod
    def get_collided_rectangle(rectangle_one: pygame.Rect, rectangle_two: pygame.Rect) -> pygame.Rect:
        """
        Return the intersection of two rectangles, or a rectangle of zero size when they do not intersect.

        :param rectangle_one: first rectangle
        :param rectangle_two: second rectangle
        :return: intersection
        """
        return rectangle_one.clip(rectangle_two)

    @staticmethod
    def calculate_visible_area(size_of_map: tuple[int, int],
                               game_surface_size: tuple[int, int]) -> tuple[tuple[int, int], pygame.Rect]:
        """
        Calculate the visible area of the game surface (the part with the map) and its position on the screen.

        Width and height are calculated separately:
        - map smaller than the game surface: visible area cut to the map size and centered on the screen,
        - map larger or equal: visible area is the whole game surface, starting at the edge.
        The header height is added to the vertical position.

        Example (48 px tiles, 80 px header):
            size_of_map   map (px)      game_surface_size   visible_area_screen_position   visible_area_rect
            20 x 30       960 x 1440    1200 x 496          (120, 80)                      (0, 0, 960, 496)
            30 x 20       1440 x 960    1200 x 496          (0, 80)                        (0, 0, 1200, 496)

        :param size_of_map: map size in tiles (width, height)
        :param game_surface_size: game surface size in pixels (width, height)
        :return: position (x, y) of the visible area on the screen
                 and the visible area as a rectangle at (0, 0) on the game surface
        """
        map_rect = pygame.Rect(0, 0, size_of_map[0] * Settings.TILE_SIZE, size_of_map[1] * Settings.TILE_SIZE)
        game_surface_rect = pygame.Rect((0, 0), game_surface_size)

        # Calculate the position of the visible area on the screen
        visible_area_x = 0
        if map_rect.width < game_surface_rect.width:
            visible_area_x = (game_surface_rect.width - map_rect.width) // 2

        visible_area_y = Settings.HEADER_HEIGHT
        if map_rect.height < game_surface_rect.height:
            visible_area_y += (game_surface_rect.height - map_rect.height) // 2

        # Calculate the visible area - the game surface cut to the map size
        visible_area_rect = game_surface_rect.copy()
        if visible_area_rect.width > map_rect.width:
            visible_area_rect.width = map_rect.width
        if visible_area_rect.height > map_rect.height:
            visible_area_rect.height = map_rect.height

        return (visible_area_x, visible_area_y), visible_area_rect
