from enum import IntEnum


class GameStatus(IntEnum):
    UNKNOWN = 0
    STUDIO_PAGE = 1
    FIRST_PAGE = 2
    SECRET_CODE = 3
    SECRET_CODE_IS_VALID = 4
    NEXT_LEVEL = 5
    GAME_IS_RUNNING = 6
    GAME_IS_PAUSED = 7
    LEVEL_COMPLETED = 8
    GAME_OVER = 9
    SUMMARY = 10
