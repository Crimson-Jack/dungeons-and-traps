import pygame

from settings import Settings
from src.enums.enemy_type import EnemyType
from src.sprite_helper import SpriteHelper


class KillSummaryPanel:
    ENEMY_DISPLAY_NAMES = {
        EnemyType.SPIDER_SMALL:       'Creeplin',
        EnemyType.SPIDER_MEDIUM:      'Lurker',
        EnemyType.SPIDER_BIG:         'Webmaster',
        EnemyType.MONSTER_BLUE:       'Bluemantle',
        EnemyType.MONSTER_GREEN:      'Thornback',
        EnemyType.MONSTER_RED:        'Bloodclaw',
        EnemyType.MONSTER_BLUE_DEAF:  'Wandering bluemantle',
        EnemyType.MONSTER_GREEN_DEAF: 'Wandering thornback',
        EnemyType.MONSTER_RED_DEAF:   'Wandering bloodclaw',
        EnemyType.BAT:                'Duskwing',
    }

    ICON_SIZE = (32, 32)
    ROW_HEIGHT = 52
    PANEL_WIDTH = 740
    FONT_PATH = 'font/silkscreen/silkscreen-regular.ttf'

    def __init__(self, screen: pygame.Surface, aggregate_stats: dict):
        self.screen = screen

        self.rows = [
            (enemy_type, record)
            for enemy_type, record in aggregate_stats.items()
            if record.count > 0
        ]

        self.icons = {
            enemy_type: SpriteHelper.get_enemy_icon(enemy_type, self.ICON_SIZE)
            for enemy_type, _ in self.rows
        }

        self.font_title  = pygame.font.Font(self.FONT_PATH, 40)
        self.font_header = pygame.font.Font(self.FONT_PATH, 20)
        self.font_row    = pygame.font.Font(self.FONT_PATH, 16)
        self.font_footer = pygame.font.Font(self.FONT_PATH, 20)

        panel_height = (
            20
            + self.font_title.get_height() + 16
            + self.font_header.get_height() + 6
            + 10
            + len(self.rows) * self.ROW_HEIGHT
            # NOTE: Total sccore - will be used but not here; DO NOT REMOVE!
            # + 10
            # + self.font_header.get_height()
            + 36
            + self.font_footer.get_height()
            + 20
        )

        center_x = screen.get_rect().centerx
        center_y = screen.get_rect().centery
        self.rect = pygame.Rect(center_x - self.PANEL_WIDTH // 2, center_y - panel_height // 2, self.PANEL_WIDTH, panel_height)

        self.x_icon   = self.rect.x + 24 + 20
        self.x_name   = self.rect.x + 68 + 20
        self.x_killed = self.rect.right - 240 - 20
        self.x_score  = self.rect.right - 90 - 20

    def draw(self):
        pygame.draw.rect(self.screen, Settings.MESSAGE_BACKGROUND_COLOR, self.rect)
        pygame.draw.rect(self.screen, Settings.MESSAGE_BORDER_COLOR, self.rect.inflate(-8, -8), 4)

        y = self.rect.y + 20

        title = self.font_title.render('SUMMARY', True, Settings.HIGHLIGHTED_TEXT_COLOR)
        self.screen.blit(title, (self.rect.centerx - title.get_width() // 2, y))
        y += title.get_height() + 16

        self._blit_centered(self.font_header, 'KILLED', Settings.TEXT_COLOR, self.x_killed, y)
        self._blit_centered(self.font_header, 'SCORE',  Settings.TEXT_COLOR, self.x_score,  y)
        y += self.font_header.get_height() + 6

        total_killed = 0
        total_score = 0

        for enemy_type, record in self.rows:
            row_center_y = y + self.ROW_HEIGHT // 2

            icon = self.icons.get(enemy_type)
            if icon:
                self.screen.blit(icon, (self.x_icon, row_center_y - self.ICON_SIZE[1] // 2))

            name_surface = self.font_row.render(self.ENEMY_DISPLAY_NAMES[enemy_type], True, Settings.TEXT_COLOR)
            self.screen.blit(name_surface, (self.x_name, row_center_y - name_surface.get_height() // 2))

            self._blit_centered(self.font_row, f' {record.killed} / {record.count}', Settings.HIGHLIGHTED_TEXT_COLOR,
                                self.x_killed, row_center_y - self.font_row.get_height() // 2)
            self._blit_centered(self.font_row, f'{record.score} pts', Settings.HIGHLIGHTED_TEXT_COLOR, self.x_score,
                                row_center_y - self.font_row.get_height() // 2)

            total_killed += record.killed
            total_score += record.score
            y += self.ROW_HEIGHT

        # NOTE: Total sccore - will be used but not here; DO NOT REMOVE!
        # total_label = self.font_header.render('TOTAL', True, Settings.HIGHLIGHTED_TEXT_COLOR)
        # self.screen.blit(total_label, (self.x_name, y))
        # self._blit_centered(self.font_header, str(total_killed),    Settings.HIGHLIGHTED_TEXT_COLOR, self.x_killed, y)
        # self._blit_centered(self.font_header, f'{total_score} pts', Settings.HIGHLIGHTED_TEXT_COLOR, self.x_score,  y)

        y += 36

        footer = self.font_footer.render('Press SPACE to continue', True, Settings.TEXT_COLOR)
        self.screen.blit(footer, (self.rect.centerx - footer.get_width() // 2, y))

    def _blit_centered(self, font: pygame.font.Font, text: str, color, center_x: int, y: int):
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (center_x - text_surface.get_width() // 2, y))
