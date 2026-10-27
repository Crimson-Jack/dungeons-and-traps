import pygame

from settings import Settings
from src.enums.enemy_type import EnemyType
from src.sprite_costume import SpriteCostume
from src.spritesheet import SpriteSheet


class SpriteHelper:
    """
    Static helpers that load images from img/ and cut them into scaled sprites, icons and page images.
    All game images, apart from the map tiles loaded by pytmx, are loaded through this class.
    """

    # Size in pixels of a single tile in the source sprite sheet images
    SOURCE_TILE_SIZE = 16
    # Size in pixels of a single tile on the screen
    SCALED_TILE_SIZE = int(Settings.TILE_SIZE), int(Settings.TILE_SIZE)
    # Size in pixels of the icons in the header and the dashboard
    ICON_SIZE = 64, 64
    # Size in pixels of the game over images in the source
    GAME_OVER_IMAGE_SOURCE_SIZE = 120

    @staticmethod
    def get_tile_image(sprite_sheet_name: str, row: int, cell: int) -> pygame.Surface:
        """
        Return one frame of 1 x 1 tile from img/<sprite_sheet_name>.png, scaled to the tile size.

        :param sprite_sheet_name: file name of the sprite sheet without the extension
        :param row: row of the frame in the sprite sheet
        :param cell: cell of the frame in the row
        :return: frame image
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet(f'img/{sprite_sheet_name}.png')
        return sprite_sheet.get_image(row, cell)

    @staticmethod
    def get_multi_tile_image(sprite_sheet_name: str, row: int, cell: int, number_of_tiles: int) -> pygame.Surface:
        """
        Return one frame of number_of_tiles x number_of_tiles tiles from img/<sprite_sheet_name>.png,
        scaled to number_of_tiles x number_of_tiles tile sizes.

        :param sprite_sheet_name: file name of the sprite sheet without the extension
        :param row: row of the frame in the sprite sheet
        :param cell: cell of the frame in the row
        :param number_of_tiles: width and height of one frame in tiles
        :return: frame image
        """
        sprite_sheet = SpriteHelper._create_multi_tile_sprite_sheet(f'img/{sprite_sheet_name}.png', number_of_tiles)
        return sprite_sheet.get_image(row, cell)

    @staticmethod
    def get_costumes_matrix(sprite_sheet_name: str, sprite_costumes: list[SpriteCostume]) -> list[list[SpriteCostume]]:
        """
        Return the costumes of every row of the sprite sheet for each cell: result[cell][row].
        Each costume takes the number of frames from sprite_costumes[cell].

        :param sprite_sheet_name: file name of the sprite sheet without the extension
        :param sprite_costumes: one costume per cell, giving its number of frames
        :return: costumes indexed by cell and then by row
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet(f'img/{sprite_sheet_name}.png')
        result = list()

        for cell in range(len(sprite_costumes)):
            cell_costumes = list()
            for row in range(sprite_sheet.number_of_rows):
                cell_costumes.append(
                    SpriteCostume(sprite_sheet.get_image(row, cell), sprite_costumes[cell].number_of_frames)
                )
            result.append(cell_costumes)

        return result

    @staticmethod
    def get_tombstone_frames() -> list[pygame.Surface]:
        """
        Return 4 frames of the enemy tombstone.

        :return: frames in animation order
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/skull.png')

        sprites = list()
        sprites.append(sprite_sheet.get_image(0, 0))
        sprites.append(sprite_sheet.get_image(0, 1))
        sprites.append(sprite_sheet.get_image(0, 2))
        sprites.append(sprite_sheet.get_image(0, 3))

        return sprites

    @staticmethod
    def get_boss_tombstone_frames() -> list[pygame.Surface]:
        """
        Return 18 frames of the vanishing boss, 3 x 3 tiles each.

        :return: frames in animation order
        """
        sprite_sheet = SpriteHelper._create_multi_tile_sprite_sheet('img/vanishing-flare-point.png', 3)

        sprites = list()
        sprites.append(sprite_sheet.get_image(0, 0))
        sprites.append(sprite_sheet.get_image(0, 1))
        sprites.append(sprite_sheet.get_image(0, 2))
        sprites.append(sprite_sheet.get_image(0, 3))
        sprites.append(sprite_sheet.get_image(0, 4))
        sprites.append(sprite_sheet.get_image(0, 5))
        sprites.append(sprite_sheet.get_image(0, 6))
        sprites.append(sprite_sheet.get_image(0, 7))
        sprites.append(sprite_sheet.get_image(0, 8))
        sprites.append(sprite_sheet.get_image(0, 9))
        sprites.append(sprite_sheet.get_image(0, 10))
        sprites.append(sprite_sheet.get_image(0, 11))
        sprites.append(sprite_sheet.get_image(0, 12))
        sprites.append(sprite_sheet.get_image(0, 13))
        sprites.append(sprite_sheet.get_image(0, 14))
        sprites.append(sprite_sheet.get_image(0, 15))
        sprites.append(sprite_sheet.get_image(0, 16))
        sprites.append(sprite_sheet.get_image(0, 17))

        return sprites

    @staticmethod
    def get_vanishing_point_frames() -> list[pygame.Surface]:
        """
        Return 8 frames of the vanishing point.

        :return: frames in animation order
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/vanishing-point.png')

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

    @staticmethod
    def get_monster_frames(sprite_sheet_name: str) -> list[pygame.Surface]:
        """
        Return 4 animation frames of the monster.

        :param sprite_sheet_name: file name of the monster sprite sheet without the extension
        :return: frames in animation order
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet(f'img/{sprite_sheet_name}.png')

        sprites = list()

        sprites.append(sprite_sheet.get_image(0, 0))
        sprites.append(sprite_sheet.get_image(0, 1))
        sprites.append(sprite_sheet.get_image(0, 2))
        sprites.append(sprite_sheet.get_image(0, 3))

        return sprites

    @staticmethod
    def get_octopus_frames(sprite_sheet_name: str) -> list[pygame.Surface]:
        """
        Return 16 animation frames of the octopus, 3 x 3 tiles each.

        :param sprite_sheet_name: file name of the octopus sprite sheet without the extension
        :return: frames in animation order
        """
        sprite_sheet = SpriteHelper._create_multi_tile_sprite_sheet(f'img/{sprite_sheet_name}.png', 3)

        sprites = list()

        sprites.append(sprite_sheet.get_image(0, 0))
        sprites.append(sprite_sheet.get_image(0, 1))
        sprites.append(sprite_sheet.get_image(0, 2))
        sprites.append(sprite_sheet.get_image(0, 3))

        sprites.append(sprite_sheet.get_image(0, 4))
        sprites.append(sprite_sheet.get_image(0, 5))
        sprites.append(sprite_sheet.get_image(0, 6))
        sprites.append(sprite_sheet.get_image(0, 7))

        sprites.append(sprite_sheet.get_image(0, 8))
        sprites.append(sprite_sheet.get_image(0, 9))
        sprites.append(sprite_sheet.get_image(0, 10))
        sprites.append(sprite_sheet.get_image(0, 11))

        sprites.append(sprite_sheet.get_image(0, 12))
        sprites.append(sprite_sheet.get_image(0, 13))
        sprites.append(sprite_sheet.get_image(0, 14))
        sprites.append(sprite_sheet.get_image(0, 15))

        return sprites

    @staticmethod
    def get_fire_ball_frames() -> list[pygame.Surface]:
        """
        Return 4 animation frames of the fireball.

        :return: frames in animation order
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/fireball.png')

        sprites = list()

        sprites.append(sprite_sheet.get_image(0, 0))
        sprites.append(sprite_sheet.get_image(0, 1))
        sprites.append(sprite_sheet.get_image(0, 2))
        sprites.append(sprite_sheet.get_image(0, 3))

        return sprites

    @staticmethod
    def get_egg_frames() -> list[pygame.Surface]:
        """
        Return 4 animation frames of the egg.

        :return: frames in animation order
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/egg.png')

        sprites = list()

        sprites.append(sprite_sheet.get_image(0, 0))
        sprites.append(sprite_sheet.get_image(0, 1))
        sprites.append(sprite_sheet.get_image(0, 2))
        sprites.append(sprite_sheet.get_image(0, 3))

        return sprites

    @staticmethod
    def get_all_player_sprites(number_of_sprites: int) -> dict[str, list[pygame.Surface]]:
        """
        Return the player images for 8 directions: the standing image followed by the walking images.
        Diagonal directions use the up and down images.

        :param number_of_sprites: number of walking images per direction
        :return: images by direction name
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/player.png')

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

    @staticmethod
    def get_all_arrow_sprites() -> dict[str, list[pygame.Surface]]:
        """
        Return one arrow image for each of 8 directions.

        :return: one-element image lists by direction name
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/arrow.png')

        sprites = {
            'left': [],
            'right': [],
            'up': [],
            'down': [],
            'right_up': [],
            'left_up': [],
            'right_down': [],
            'left_down': []
        }

        sprites['right'].append(sprite_sheet.get_image(0, 0))
        sprites['left'].append(sprite_sheet.get_image(1, 0))
        sprites['up'].append(sprite_sheet.get_image(2, 0))
        sprites['down'].append(sprite_sheet.get_image(3, 0))
        sprites['right_up'].append(sprite_sheet.get_image(4, 0))
        sprites['left_up'].append(sprite_sheet.get_image(5, 0))
        sprites['right_down'].append(sprite_sheet.get_image(6, 0))
        sprites['left_down'].append(sprite_sheet.get_image(7, 0))

        return sprites

    @staticmethod
    def get_all_sword_sprites() -> dict[str, list[pygame.Surface]]:
        """
        Return 8 frames of the sword strike for each of 4 directions.
        The last frame is repeated, so the sword stays extended longer.

        :return: frames by direction name
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/sword.png')

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

    @staticmethod
    def get_all_bow_sprites() -> dict[str, list[pygame.Surface]]:
        """
        Return one bow image for each of 8 directions.

        :return: one-element image lists by direction name
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/bow.png')

        sprites = {
            'left': [],
            'right': [],
            'up': [],
            'down': [],
            'right_down': [],
            'left_down': [],
            'left_up': [],
            'right_up': []}

        sprites['right'].append(sprite_sheet.get_image(0, 0))
        sprites['left'].append(sprite_sheet.get_image(1, 0))
        sprites['up'].append(sprite_sheet.get_image(2, 0))
        sprites['down'].append(sprite_sheet.get_image(3, 0))
        sprites['right_up'].append(sprite_sheet.get_image(4, 0))
        sprites['left_up'].append(sprite_sheet.get_image(5, 0))
        sprites['right_down'].append(sprite_sheet.get_image(6, 0))
        sprites['left_down'].append(sprite_sheet.get_image(7, 0))

        return sprites

    @staticmethod
    def get_all_explosion_sprites() -> dict[str, list[pygame.Surface]]:
        """
        Return one TNT image for each of 4 directions.

        :return: one-element image lists by direction name
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/tnt.png')

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

    @staticmethod
    def get_life_dashboard_icon() -> pygame.Surface:
        """
        Return the life icon for the dashboard, 64 x 64 pixels.

        :return: life icon
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/misc.png', size=SpriteHelper.ICON_SIZE)
        return sprite_sheet.get_image(1, 2)

    @staticmethod
    def get_sword_header_icons() -> list[pygame.Surface]:
        """
        Return 5 sword icons for the header, 64 x 64 pixels: one per sword wear level, from new to worn out.

        :return: icons in wear level order
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/misc.png', size=SpriteHelper.ICON_SIZE)

        images = list()
        images.append(sprite_sheet.get_image(2, 0))
        images.append(sprite_sheet.get_image(2, 1))
        images.append(sprite_sheet.get_image(2, 2))
        images.append(sprite_sheet.get_image(2, 3))
        images.append(sprite_sheet.get_image(2, 4))

        return images

    @staticmethod
    def get_bow_header_icon() -> pygame.Surface:
        """
        Return the bow icon for the header, 64 x 64 pixels.

        :return: bow icon
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/misc.png', size=SpriteHelper.ICON_SIZE)
        return sprite_sheet.get_image(1, 1)

    @staticmethod
    def get_explosion_header_icon() -> pygame.Surface:
        """
        Return the TNT icon for the header, 64 x 64 pixels.

        :return: TNT icon
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet('img/misc.png', size=SpriteHelper.ICON_SIZE)
        return sprite_sheet.get_image(1, 0)

    @staticmethod
    def get_enemy_icon(enemy_type: EnemyType, size: tuple[int, int]) -> pygame.Surface:
        """
        Return the icon of the enemy type (its first frame) scaled to the size, for the summary.

        :param enemy_type: type of the enemy
        :param size: size of the returned icon
        :return: enemy icon
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet(f'img/{enemy_type.value}.png', size=size)
        return sprite_sheet.get_image(0, 0)

    @staticmethod
    def get_game_over_lose_image(size: tuple[int, int]) -> pygame.Surface:
        """
        Return the game over (lose) image, 120 x 120 pixels in the source, scaled to the size.

        :param size: size of the returned image
        :return: game over lose image
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet(
            'img/game-over-you-lose.png', SpriteHelper.GAME_OVER_IMAGE_SOURCE_SIZE, size
        )
        return sprite_sheet.get_image(0, 0)

    @staticmethod
    def get_game_over_win_image(size: tuple[int, int]) -> pygame.Surface:
        """
        Return the game over (win) image, 120 x 120 pixels in the source, scaled to the size.

        :param size: size of the returned image
        :return: game over win image
        """
        sprite_sheet = SpriteHelper._create_sprite_sheet(
            'img/game-over-you-win.png', SpriteHelper.GAME_OVER_IMAGE_SOURCE_SIZE, size
        )
        return sprite_sheet.get_image(0, 0)

    @staticmethod
    def get_loading_page_image(size: tuple[int, int]) -> pygame.Surface:
        """
        Return the loading page image scaled to the size.

        :param size: size of the returned image
        :return: loading page image
        """
        return SpriteHelper._get_page_image('img/loading-page.png', size)

    @staticmethod
    def get_start_page_image(size: tuple[int, int]) -> pygame.Surface:
        """
        Return the start page image scaled to the size.

        :param size: size of the returned image
        :return: start page image
        """
        return SpriteHelper._get_page_image('img/start-page.png', size)

    @staticmethod
    def get_studio_page_image(size: tuple[int, int]) -> pygame.Surface:
        """
        Return the studio page image scaled to the size.

        :param size: size of the returned image
        :return: studio page image
        """
        return SpriteHelper._get_page_image('img/studio-page.png', size)

    @staticmethod
    def _create_sprite_sheet(path: str, source_size: int = SOURCE_TILE_SIZE,
                             size: tuple[float, float] = SCALED_TILE_SIZE) -> SpriteSheet:
        # By default, a frame is one source tile scaled to one tile on the screen
        sprite_sheet = SpriteSheet(
            pygame.image.load(path).convert_alpha(),
            source_size,
            source_size,
            size
        )

        return sprite_sheet

    @staticmethod
    def _create_multi_tile_sprite_sheet(path: str, number_of_tiles: int) -> SpriteSheet:
        # Each frame takes number_of_tiles x number_of_tiles tiles in the source and on the screen
        source_size = SpriteHelper.SOURCE_TILE_SIZE * number_of_tiles
        scaled_size = int(Settings.TILE_SIZE * number_of_tiles), int(Settings.TILE_SIZE * number_of_tiles)
        return SpriteHelper._create_sprite_sheet(path, source_size, scaled_size)

    @staticmethod
    def _get_page_image(path: str, size: tuple[int, int]) -> pygame.Surface:
        # Page images are a single 320px x 192px picture
        page_image_source_width = 320
        page_image_source_height = 192
        sprite_sheet = SpriteSheet(
            pygame.image.load(path).convert_alpha(),
            page_image_source_width,
            page_image_source_height,
            size
        )
        return sprite_sheet.get_image(0, 0)
