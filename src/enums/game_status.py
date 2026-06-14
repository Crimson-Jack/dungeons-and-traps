from enum import IntEnum


class GameStatus(IntEnum):
    UNKNOWN = 0
    FIRST_PAGE = 1
    SECRET_CODE = 2
    SECRET_CODE_IS_VALID = 3
    NEXT_LEVEL = 4
    GAME_IS_RUNNING = 5
    GAME_IS_PAUSED = 6
    LEVEL_COMPLETED = 7
    GAME_OVER = 8
    SUMMARY = 9
