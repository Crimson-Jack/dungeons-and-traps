from enum import IntEnum


class GameStatus(IntEnum):
    UNKNOWN = 0
    STUDIO_PAGE = 1
    FIRST_PAGE = 2
    SECRET_CODE = 3
    SECRET_CODE_IS_VALID = 4
    CREDITS = 5
    NEXT_LEVEL = 6
    GAME_IS_RUNNING = 7
    GAME_IS_PAUSED = 8
    LEVEL_COMPLETED = 9
    GAME_OVER = 10
    YOU_WIN = 11
    SUMMARY = 12
