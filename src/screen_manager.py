import pygame

from settings import Settings
from src.enums.game_status import GameStatus
from src.game_manager import GameManager
from src.level import Level
from src.panels.dashboard import Dashboard
from src.panels.dialog_factory import DialogFactory
from src.panels.first_page import FirstPage
from src.panels.loading_page import LoadingPage
from src.panels.studio_page import StudioPage
from src.panels.header import Header
from src.panels.message import Message
from src.panels.multi_page_panel import MultiPagePanel
from src.panels.summary_collectables_page import SummaryCollectablesPage
from src.panels.summary_enemies_page import SummaryEnemiesPage
from src.panels.summary_trophy_page import SummaryTrophyPage


class ScreenManager:
    """Owns what is currently on screen: surfaces, level, panels, pages and dialogs."""

    # Statuses whose whole screen is the current message_dialog
    MESSAGE_DIALOG_STATUSES = frozenset({
        GameStatus.CREDITS,
        GameStatus.SECRET_CODE,
        GameStatus.SECRET_CODE_IS_VALID,
        GameStatus.NEXT_LEVEL,
        GameStatus.LEVEL_COMPLETED,
        GameStatus.GAME_OVER,
        GameStatus.YOU_WIN,
    })

    def __init__(self, screen: pygame.Surface, game_manager: GameManager) -> None:
        """
        Create the game surfaces, the level, the header and the dashboard.
        Pages, dialogs and the summary panel start empty.

        :param screen: the whole game window
        :param game_manager: shared game state
        """
        self.screen = screen
        self.game_manager = game_manager

        # Game surfaces
        game_surface_size = Settings.WIDTH, Settings.HEIGHT - Settings.HEADER_HEIGHT - Settings.DASHBOARD_HEIGHT
        header_surface_size = Settings.WIDTH, Settings.HEADER_HEIGHT
        dashboard_surface_size = Settings.WIDTH, Settings.DASHBOARD_HEIGHT
        self.game_surface = pygame.Surface(game_surface_size)
        self.header_surface = pygame.Surface(header_surface_size)
        self.dashboard_surface = pygame.Surface(dashboard_surface_size)

        # Game components
        self.level = Level(self.screen, self.game_surface, self.game_manager)
        self.header = Header(self.screen, self.header_surface, self.game_manager)
        self.dashboard = Dashboard(self.screen, self.dashboard_surface, self.game_manager)

        # Studio page, loading page, first page, dialogs and summary panel
        self.studio_page = None
        self.loading_page = None
        self.first_page = None
        self.menu_dialog = None
        self.message_dialog = None
        self.summary_panel = None
        self.first_page_selected_index = 0

    def run_current_screen(self) -> None:
        """
        Run the level or draw the page, dialog or panel that belongs to the current game status.
        Called once per frame.
        """
        status = self.game_manager.game_status
        if status == GameStatus.GAME_IS_RUNNING:
            # Main game logic
            self.level.run()
        elif status == GameStatus.STUDIO_PAGE:
            self.studio_page.draw()
        elif status == GameStatus.LOADING_PAGE:
            self.loading_page.draw()
        elif status == GameStatus.FIRST_PAGE:
            self.first_page.draw()
            self.menu_dialog.draw()
        elif status == GameStatus.GAME_IS_PAUSED:
            self.menu_dialog.draw()
        elif status == GameStatus.SUMMARY:
            self.summary_panel.draw()
        elif status in self.MESSAGE_DIALOG_STATUSES:
            self.message_dialog.draw()

    def show_studio_page(self) -> None:
        """
        Switch to the studio page status, clear the screen and load the studio page.
        """
        self.game_manager.set_studio_page()
        self.clean_screen()
        self._load_studio_page()

    def show_loading_page(self) -> None:
        """
        Switch to the loading page status, clear the screen and load the loading page.
        """
        self.game_manager.set_loading_page()
        self.clean_screen()
        self._load_loading_page()

    def show_first_page(self) -> None:
        """
        Switch to the first page status, clear the screen and load the first page with its menu.
        """
        self.game_manager.set_first_page()
        self.clean_screen()
        self._load_first_page()

    def show_next_level_dialog(self) -> None:
        """
        Switch to the next level status and load the dialog introducing the current level.
        """
        self.game_manager.set_next_level()
        self._load_next_level_message_dialog()

    def rebuild_level(self) -> None:
        """
        Create a new Level object for the level number stored in game_manager and replace the old one.
        Always access the level through screen_manager.level, never keep a reference to it.
        """
        self.level = Level(self.screen, self.game_surface, self.game_manager)

    def _load_studio_page(self) -> None:
        # Create the studio page
        self.studio_page = StudioPage(self.screen)

    def _load_loading_page(self) -> None:
        # Create the loading page
        self.loading_page = LoadingPage(self.screen)

    def _load_first_page(self) -> None:
        # Create the first page and its menu, restoring the menu item selected on the previous visit
        self.first_page = FirstPage(self.screen)
        self.menu_dialog = DialogFactory.create_first_page_menu(self.screen)
        self.menu_dialog.selected_index = self.first_page_selected_index

    def load_credits_message_dialog(self) -> None:
        """
        Create the 'credits' dialog.
        """
        self.message_dialog = DialogFactory.create_credits_dialog(self.screen)

    def load_secret_code_message_dialog(self, secret_code_text: str,
                                        dialog_response_messages: list[Message] | None = None) -> None:
        """
        Create the secret code dialog showing the typed text.

        :param secret_code_text: text typed by the player so far
        :param dialog_response_messages: validation result messages shown below the text, or None
        """
        self.message_dialog = DialogFactory.create_secret_code_dialog(self.screen, secret_code_text,
                                                                      dialog_response_messages)

    def _load_next_level_message_dialog(self) -> None:
        # Create the dialog introducing the current level: number, name, description and secret code
        self.message_dialog = DialogFactory.create_next_level_dialog(self.screen,
                                                                     self.game_manager.level + 1,
                                                                     self.game_manager.get_level_name(),
                                                                     self.game_manager.get_level_description(),
                                                                     self.game_manager.get_secret_code())

    def load_game_paused_menu(self) -> None:
        """
        Create the pause menu.
        """
        self.menu_dialog = DialogFactory.create_game_paused_menu(self.screen)

    def load_level_completed_message_dialog(self) -> None:
        """
        Create the level completed dialog with the statistics of the current level.
        """
        self.message_dialog = DialogFactory.create_level_completed_dialog(self.screen,
                                                                          self.game_manager.level_stats[-1])

    def load_game_over_message_dialog(self) -> None:
        """
        Create the game over dialog.
        """
        self.message_dialog = DialogFactory.create_game_over_dialog(self.screen)

    def load_you_win_message_dialog(self) -> None:
        """
        Create the 'you win' dialog.
        """
        self.message_dialog = DialogFactory.create_you_win_dialog(self.screen)

    def load_summary_panel(self, player_won: bool) -> None:
        """
        Create the end of game summary panel (trophy, enemies and collectables pages)
        and switch to the summary status.

        :param player_won: True when the player completed the game, False after game over
        """
        diamond_record, key_record, bonus_record = self.game_manager.get_aggregate_collectable_stats()
        pages = (
            [SummaryTrophyPage(self.game_manager.score, player_won)]
            + SummaryEnemiesPage.create_pages(self.game_manager.get_aggregate_kill_stats())
            + [SummaryCollectablesPage(diamond_record, key_record, bonus_record)]
        )
        self.summary_panel = MultiPagePanel(self.screen, pages)
        self.game_manager.set_summary()

    def dispose_studio_page(self) -> None:
        """
        Remove the studio page.
        """
        self.studio_page = None

    def dispose_loading_page(self) -> None:
        """
        Remove the loading page.
        """
        self.loading_page = None

    def dispose_first_page(self) -> None:
        """
        Remove the first page and its menu, remembering the selected menu item for the next visit.
        """
        if self.menu_dialog is not None:
            self.first_page_selected_index = self.menu_dialog.get_selected_index()
        self.first_page = None
        self.menu_dialog = None

    def dispose_menu_dialog(self) -> None:
        """
        Remove the menu dialog.
        """
        self.menu_dialog = None

    def dispose_message_dialog(self) -> None:
        """
        Remove the message dialog.
        """
        self.message_dialog = None

    def dispose_summary_panel(self) -> None:
        """
        Remove the summary panel.
        """
        self.summary_panel = None

    def clean_screen(self) -> None:
        """
        Fill the whole screen with the background color.
        """
        self.screen.fill(Settings.GAME_BACKGROUND_COLOR)

    def refresh_header_surface(self) -> None:
        """
        Clear and redraw the header.
        """
        self.header.clean()
        self.header.draw()

    def refresh_dashboard_surface(self) -> None:
        """
        Clear and redraw the dashboard.
        """
        self.dashboard.clean()
        self.dashboard.draw()

    def refresh_header_and_dashboard_surfaces(self) -> None:
        """
        Clear and redraw both the header and the dashboard.
        """
        self.refresh_header_surface()
        self.refresh_dashboard_surface()
