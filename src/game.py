import pygame

from settings import Settings
from src.events import Events
from src.custom_event_controller import CustomEventController
from src.game_manager import GameManager
from src.keyboard_controller import KeyboardController
from src.screen_manager import ScreenManager


class Game:
    """Main game loop: creates the window and the game components, then dispatches events each frame."""

    # Timer durations (milliseconds)
    PARTICLE_SPARK_INTERVAL_MS = 40

    def __init__(self) -> None:
        """
        Initialize pygame and open the window (full screen or regular, as set in Settings).
        In full screen mode Settings.WIDTH and Settings.HEIGHT are overwritten with the monitor size.
        Create the game manager, the screen manager and both controllers,
        then show the studio page.
        """
        pygame.init()
        pygame.display.set_caption("Dungeons and Traps: Willy's First Adventure")

        if Settings.FULL_SCREEN_MODE:
            # Full screen mode
            monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
            Settings.WIDTH = pygame.display.Info().current_w
            Settings.HEIGHT = pygame.display.Info().current_h
            self._screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
        else:
            # Regular window
            self._screen = pygame.display.set_mode((Settings.WIDTH, Settings.HEIGHT))

        # Game manager
        self._game_manager = GameManager()

        # Game surfaces, level, panels, pages and dialogs
        self._screen_manager = ScreenManager(self._screen, self._game_manager)

        # Keyboard input per game status
        self._keyboard_controller = KeyboardController(self._game_manager, self._screen_manager)

        # Reactions to custom game events
        self._custom_event_controller = CustomEventController(self._game_manager, self._screen_manager)

        # Start with the studio page
        self._screen_manager.show_studio_page()

        # Clock
        self._clock = pygame.time.Clock()

    def run(self) -> None:
        """
        Run the main loop until the window is closed or the player quits from a menu.
        Each frame passes key events to the keyboard controller and every event to the custom event controller,
        then runs the current screen and keeps the frame rate at Settings.FPS.
        """
        pygame.time.set_timer(Events.PARTICLE_EVENT, self.PARTICLE_SPARK_INTERVAL_MS)

        is_running = True
        while is_running:
            # Handle events
            for event in pygame.event.get():
                # Input events: QUIT
                if event.type == pygame.QUIT:
                    is_running = False
                # Input events: keyboard (down)
                if event.type == pygame.KEYDOWN:
                    is_running = self._keyboard_controller.handle_keyboard_buttons_down(event)
                # Input events: keyboard (up)
                if event.type == pygame.KEYUP:
                    self._keyboard_controller.handle_keyboard_buttons_up(event)
                # Custom events
                self._custom_event_controller.handle_custom_events(event)

            self._screen_manager.run_current_screen()
            pygame.display.update()
            self._clock.tick(Settings.FPS)
