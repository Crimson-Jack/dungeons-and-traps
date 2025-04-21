import settings
import pygame
from src.spritesheet import SpriteSheet
from src.sprite_costume import SpriteCostume


SCALE = int(settings.TILE_SIZE), int(settings.TILE_SIZE)
KEY_COLOR = 0, 0, 0


def _create_sprite_sheet(path: str, source_size: int, size: tuple[float, float], key_color) -> SpriteSheet:
    sprite_sheet = SpriteSheet(
        pygame.image.load(path).convert_alpha(),
        source_size,
        source_size,
        size,
        key_color
    )

    return sprite_sheet


def get_sprite_image(sprite_sheet_name: str, row: int, cell: int):
    sprite_sheet = _create_sprite_sheet(f'img/{sprite_sheet_name}.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)
    return sprite_sheet.get_image(row, cell)


def get_large_sprite_image(name, row: int, cell: int, number_of_tiles: int):
    octopus_source_tile_size = settings.SOURCE_TILE_SIZE * number_of_tiles
    octopus_scale = int(settings.TILE_SIZE * number_of_tiles), int(settings.TILE_SIZE * number_of_tiles)
    sprite_sheet = _create_sprite_sheet(f'img/{name}.png', octopus_source_tile_size, octopus_scale, KEY_COLOR)
    return sprite_sheet.get_image(row, cell)


def get_sprite_costumes_matrix(sprite_sheet_name: str, sprite_costumes: list[SpriteCostume]) -> list[list[SpriteCostume]]:
    sprite_sheet = _create_sprite_sheet(f'img/{sprite_sheet_name}.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)
    result = list()

    for cell in range(0, len(sprite_costumes)):
        rows = list()
        for row in range(0, sprite_sheet.number_of_rows):
            rows.append(
                SpriteCostume(sprite_sheet.get_image(row, cell), sprite_costumes[cell].number_of_frames)
            )
        result.append(rows)

    return result


def get_all_player_sprites(number_of_sprites):
    sprite_sheet = _create_sprite_sheet('img/player.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = {
        'left': [],
        'right': [],
        'up': [],
        'down': [],
        'right_down': [],
        'left_down': [],
        'left_up': [],
        'right_up': []}

    # Sprites with the state: standing
    sprites['right'].append(sprite_sheet.get_image(0, 0))
    sprites['left'].append(sprite_sheet.get_image(2, 0))
    sprites['up'].append(sprite_sheet.get_image(4, 0))
    sprites['down'].append(sprite_sheet.get_image(6, 0))
    sprites['right_down'].append(sprite_sheet.get_image(6, 0))
    sprites['right_up'].append(sprite_sheet.get_image(4, 0))
    sprites['left_down'].append(sprite_sheet.get_image(6, 0))
    sprites['left_up'].append(sprite_sheet.get_image(4, 0))

    # Sprites with the state: walking
    for number in range(0, number_of_sprites):
        sprites['right'].append(sprite_sheet.get_image(1, number))
        sprites['left'].append(sprite_sheet.get_image(3, number))
        sprites['up'].append(sprite_sheet.get_image(5, number))
        sprites['down'].append(sprite_sheet.get_image(7, number))
        sprites['right_down'].append(sprite_sheet.get_image(7, number))
        sprites['right_up'].append(sprite_sheet.get_image(5, number))
        sprites['left_down'].append(sprite_sheet.get_image(7, number))
        sprites['left_up'].append(sprite_sheet.get_image(5, number))

    return sprites


def get_life_sprite():
    sprite_sheet = _create_sprite_sheet('img/misc.png', settings.SOURCE_TILE_SIZE, (64, 64), KEY_COLOR)
    return sprite_sheet.get_image(1, 2)


def get_all_arrow_sprites():
    sprite_sheet = _create_sprite_sheet('img/arrow.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = {
        'left': [],
        'right': [],
        'up': [],
        'down': []}

    sprites['right'].append(sprite_sheet.get_image(0, 0))
    sprites['left'].append(sprite_sheet.get_image(1, 0))
    sprites['up'].append(sprite_sheet.get_image(2, 0))
    sprites['down'].append(sprite_sheet.get_image(3, 0))

    return sprites


def get_all_sword_sprites():
    sprite_sheet = _create_sprite_sheet('img/sword.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = {
        'left': [],
        'right': [],
        'up': [],
        'down': []}

    sprites['right'].append(sprite_sheet.get_image(0, 0))
    sprites['right'].append(sprite_sheet.get_image(0, 1))
    sprites['right'].append(sprite_sheet.get_image(0, 2))
    sprites['right'].append(sprite_sheet.get_image(0, 3))
    sprites['right'].append(sprite_sheet.get_image(0, 3))
    sprites['right'].append(sprite_sheet.get_image(0, 3))
    sprites['right'].append(sprite_sheet.get_image(0, 3))
    sprites['right'].append(sprite_sheet.get_image(0, 3))

    sprites['left'].append(sprite_sheet.get_image(1, 0))
    sprites['left'].append(sprite_sheet.get_image(1, 1))
    sprites['left'].append(sprite_sheet.get_image(1, 2))
    sprites['left'].append(sprite_sheet.get_image(1, 3))
    sprites['left'].append(sprite_sheet.get_image(1, 3))
    sprites['left'].append(sprite_sheet.get_image(1, 3))
    sprites['left'].append(sprite_sheet.get_image(1, 3))
    sprites['left'].append(sprite_sheet.get_image(1, 3))

    sprites['up'].append(sprite_sheet.get_image(2, 0))
    sprites['up'].append(sprite_sheet.get_image(2, 1))
    sprites['up'].append(sprite_sheet.get_image(2, 2))
    sprites['up'].append(sprite_sheet.get_image(2, 3))
    sprites['up'].append(sprite_sheet.get_image(2, 3))
    sprites['up'].append(sprite_sheet.get_image(2, 3))
    sprites['up'].append(sprite_sheet.get_image(2, 3))
    sprites['up'].append(sprite_sheet.get_image(2, 3))

    sprites['down'].append(sprite_sheet.get_image(3, 0))
    sprites['down'].append(sprite_sheet.get_image(3, 1))
    sprites['down'].append(sprite_sheet.get_image(3, 2))
    sprites['down'].append(sprite_sheet.get_image(3, 3))
    sprites['down'].append(sprite_sheet.get_image(3, 3))
    sprites['down'].append(sprite_sheet.get_image(3, 3))
    sprites['down'].append(sprite_sheet.get_image(3, 3))
    sprites['down'].append(sprite_sheet.get_image(3, 3))

    return sprites


def get_all_tombstone_sprites():
    sprite_sheet = _create_sprite_sheet('img/skull.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = list()
    sprites.append(sprite_sheet.get_image(0, 0))
    sprites.append(sprite_sheet.get_image(0, 1))
    sprites.append(sprite_sheet.get_image(0, 2))
    sprites.append(sprite_sheet.get_image(0, 3))

    return sprites


def get_all_vanishing_point_sprites():
    sprite_sheet = _create_sprite_sheet('img/vanishing-point.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = list()
    sprites.append(sprite_sheet.get_image(0, 0))
    sprites.append(sprite_sheet.get_image(0, 1))
    sprites.append(sprite_sheet.get_image(0, 2))
    sprites.append(sprite_sheet.get_image(0, 3))
    sprites.append(sprite_sheet.get_image(0, 4))
    sprites.append(sprite_sheet.get_image(0, 5))
    sprites.append(sprite_sheet.get_image(0, 6))
    sprites.append(sprite_sheet.get_image(0, 7))

    return sprites


def get_all_bow_sprites():
    sprite_sheet = _create_sprite_sheet('img/bow.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = {
        'left': [],
        'right': [],
        'up': [],
        'down': []}

    sprites['right'].append(sprite_sheet.get_image(0, 0))
    sprites['left'].append(sprite_sheet.get_image(1, 0))
    sprites['up'].append(sprite_sheet.get_image(2, 0))
    sprites['down'].append(sprite_sheet.get_image(3, 0))

    return sprites


def get_all_monster_sprites(name):
    sprite_sheet = _create_sprite_sheet(f'img/{name}.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = list()

    sprites.append(sprite_sheet.get_image(0, 0))
    sprites.append(sprite_sheet.get_image(0, 1))
    sprites.append(sprite_sheet.get_image(0, 2))
    sprites.append(sprite_sheet.get_image(0, 3))

    return sprites


def get_sword_images_to_header_view():
    sprite_sheet = _create_sprite_sheet(f'img/misc.png', settings.SOURCE_TILE_SIZE, (64, 64), KEY_COLOR)

    images = list()
    images.append(sprite_sheet.get_image(2, 0))
    images.append(sprite_sheet.get_image(2, 1))
    images.append(sprite_sheet.get_image(2, 2))
    images.append(sprite_sheet.get_image(2, 3))
    images.append(sprite_sheet.get_image(2, 4))

    return images


def get_bow_image_to_header_view():
    sprite_sheet = _create_sprite_sheet(f'img/misc.png', settings.SOURCE_TILE_SIZE, (64, 64), KEY_COLOR)
    return sprite_sheet.get_image(1, 1)


def get_all_fire_ball_enemy_sprites():
    sprite_sheet = _create_sprite_sheet('img/fireball.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = list()

    sprites.append(sprite_sheet.get_image(0, 0))
    sprites.append(sprite_sheet.get_image(0, 1))
    sprites.append(sprite_sheet.get_image(0, 2))
    sprites.append(sprite_sheet.get_image(0, 3))

    return sprites


def get_all_egg_sprites():
    sprite_sheet = _create_sprite_sheet('img/egg.png', settings.SOURCE_TILE_SIZE, SCALE, KEY_COLOR)

    sprites = list()

    sprites.append(sprite_sheet.get_image(0, 0))
    sprites.append(sprite_sheet.get_image(0, 1))
    sprites.append(sprite_sheet.get_image(0, 2))
    sprites.append(sprite_sheet.get_image(0, 3))

    return sprites
