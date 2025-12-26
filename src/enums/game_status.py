from enum import IntEnum


class GameStatus(IntEnum):
    UNKNOWN = 0
    FIRST_PAGE = 1
    SECRET_CODE = 2
    NEXT_LEVEL = 3
    GAME_IS_RUNNING = 4
    GAME_IS_PAUSED = 5
    OPTIONS = 6
    LEVEL_COMPLETED = 7
    GAME_OVER = 8
