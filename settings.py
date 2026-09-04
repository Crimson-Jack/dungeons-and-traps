class Settings:
    # Clock
    FPS = 45
    # NOTE: experimental feature
    DYNAMIC_FPS_ENABLED = True

    # Screen size
    FULL_SCREEN_MODE = False
    # WIDTH/HEIGHT below are ignored when FULL_SCREEN_MODE is True — they get overwritten at
    # startup with the monitor resolution (see game.py).
    WIDTH = 1200
    HEIGHT = 720

    # HEADER_HEIGHT + DASHBOARD_HEIGHT must be smaller than HEIGHT — the remaining space becomes
    # the game surface height (see game.py).
    # Header size
    HEADER_HEIGHT = 80
    # Dashboard size
    DASHBOARD_HEIGHT = 144

    # Tile size (rendered). Should be a multiple of 16 (source sprite pixel size) so scaling
    # stays an even integer ratio and pixels don't get blurred/misaligned.
    TILE_SIZE = 48

    # Explosion
    EXPLOSION_WEAPON_RANGE = 5
    NUMBER_OF_EXPLOSION_STEPS = 12

    # Studio page
    STUDIO_PAGE_VISIBILITY = True

    # Colors
    GAME_BACKGROUND_COLOR = 39, 39, 39
    ENEMY_PARTICLE_COLORS = [(240, 89, 65), (190, 49, 68), (135, 35, 65), (34, 9, 44)]
    OBSTACLE_PARTICLE_COLORS = [(255, 255, 255), (240, 240, 240), (230, 230, 230), (220, 220, 220)]
    MESSAGE_BACKGROUND_COLOR = 39, 39, 39
    MESSAGE_BORDER_COLOR = 120, 120, 120
    SURFACE_COLOR = 100, 100, 100
    BACKGROUND_COLOR = 120, 120, 120
    BORDER_COLOR = 70, 70, 70
    TEXT_COLOR = 208, 208, 208
    HIGHLIGHTED_TEXT_COLOR = 255, 255, 255
    BAR_TEXT_COLOR = 50, 50, 50
    BLAST_EFFECT_COLOR = 255, 255, 255
    EXPLODE_EFFECT_COLOR = 255, 210, 0
