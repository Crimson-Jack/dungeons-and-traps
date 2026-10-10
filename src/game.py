import pygame

from settings import Settings
from src.events import Events
from src.custom_event_controller import CustomEventController
from src.game_manager import GameManager
from src.keyboard_controller import KeyboardController
from src.screen_manager import ScreenManager


class Game:
    # Timer durations (milliseconds)
    PARTICLE_SPARK_INTERVAL_MS = 40

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption('Dungeons and traps')

        if Settings.FULL_SCREEN_MODE:
            # Full screen mode
            monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
            Settings.WIDTH = pygame.display.Info().current_w
            Settings.HEIGHT = pygame.display.Info().current_h
            self.screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
        else:
            # Regular window
            self.screen = pygame.display.set_mode((Settings.WIDTH, Settings.HEIGHT))

        # Game manager
        self.game_manager = GameManager()

        # Game surfaces, level, panels, pages and dialogs
        self.screen_manager = ScreenManager(self.screen, self.game_manager)

        # Keyboard input per game status
        self.keyboard_controller = KeyboardController(self.game_manager, self.screen_manager)

        # Reactions to custom game events
        self.custom_event_controller = CustomEventController(self.game_manager, self.screen_manager)

        # Select startup mode
        if Settings.STUDIO_PAGE_VISIBILITY:
            self.screen_manager.show_studio_page()
        else:
            self.screen_manager.show_first_page()

        # Clock
        self.clock = pygame.time.Clock()

    def run(self) -> None:
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
                    is_running = self.keyboard_controller.handle_keyboard_buttons_down(event)
                # Input events: keyboard (up)
                if event.type == pygame.KEYUP:
                    self.keyboard_controller.handle_keyboard_buttons_up(event)
                # Custom events
                self.custom_event_controller.handle_custom_events(event)

            self.screen_manager.run_current_screen()
            pygame.display.update()
            self.clock.tick(Settings.FPS)
