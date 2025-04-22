from enum import IntEnum


class GameStatus(IntEnum):
    UNKNOWN = 0
    FIRST_PAGE = 1
    NEXT_LEVEL = 2
    GAME_IS_RUNNING = 3
    GAME_IS_PAUSED = 4
    OPTIONS = 5
    LEVEL_COMPLETED = 6
    GAME_OVER = 7

