"""Main Textual application for Sudoku TUI.

This module provides the main Textual App class that orchestrates
all screens and manages application state.
"""


from textual.app import App
from textual.binding import Binding

from sudoku.presentation.controllers.app_controller import AppController

from .screens.game_screen import GameScreen
from .screens.menu_screen import MenuScreen
from .screens.player_input_screen import PlayerInputScreen
from .screens.statistics_screen import StatisticsScreen


class SudokuApp(App):
    """Main Textual application for Sudoku.

    This application provides a terminal-based user interface for playing
    Sudoku with the following features:
    - Main menu for navigation
    - Player name and difficulty selection
    - Interactive game board with vim/QWERTZ input
    - Statistics tracking and display
    - Responsive layout and keyboard shortcuts

    The app follows the Single Responsibility Principle by delegating
    game logic to the controller and focusing on UI orchestration.

    Attributes:
        controller: The application controller coordinating use cases.
    """

    TITLE = "Sudoku - Terminal Edition"
    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+q", "quit", "Quit", show=False),
    ]

    def __init__(
        self,
        controller: AppController | None = None,
        **kwargs,
    ) -> None:
        """Initialize the Sudoku application.

        Args:
            controller: The application controller. If None, a default
                       controller will be created (for testing).
            **kwargs: Additional arguments passed to App.
        """
        super().__init__(**kwargs)
        self._controller = controller
        self._current_player: str = ""
        self._current_difficulty: str = ""

    def on_mount(self) -> None:
        """Called when app is mounted.

        Sets up initial state and navigates to the main menu.
        """
        # Install all screens only if not already installed
        if not self.is_screen_installed("menu"):
            self.install_screen(MenuScreen(), name="menu")
        if not self.is_screen_installed("player_input"):
            self.install_screen(
                PlayerInputScreen(on_confirm=self._handle_player_input),
                name="player_input",
            )
        if not self.is_screen_installed("statistics"):
            self.install_screen(StatisticsScreen(), name="statistics")

        # Start at the menu
        self.push_screen("menu")

    def _handle_player_input(self, player_name: str, difficulty: str) -> None:
        """Handle player name and difficulty input.

        This callback is triggered when the player confirms their input
        on the PlayerInputScreen.

        Args:
            player_name: The entered player name.
            difficulty: The selected difficulty level.
        """
        self._current_player = player_name
        self._current_difficulty = difficulty

        # Start a new game through the controller
        if self._controller:
            try:
                game_state = self._controller.start_new_game(player_name, difficulty)
                self._start_game_screen(game_state)
            except Exception as e:
                self._show_error(f"Failed to start game: {e}")
        else:
            # No controller - just show a demo screen
            self._show_error("No controller configured")

    def _start_game_screen(self, game_state) -> None:
        """Start the game screen with the given game state.

        Args:
            game_state: The initial game state DTO.
        """
        # Get the board from the current game
        board = None
        if self._controller:
            current_game = self._controller.get_current_game()
            if current_game:
                board = current_game.board

        # Create and show game screen
        game_screen = GameScreen(
            board=board,
            player_name=self._current_player,
            difficulty=self._current_difficulty,
            on_move=self._handle_move,
            on_new_game=self._handle_new_game_request,
        )

        # Uninstall old game screen if it exists, then install the new one
        if self.is_screen_installed("game"):
            self.uninstall_screen("game")
        self.install_screen(game_screen, name="game")
        self.switch_screen("game")

    def _handle_move(self, position, value: int | None) -> None:
        """Handle a move made on the game board.

        Args:
            position: The position where the move was made.
            value: The value placed, or None to clear.
        """
        if not self._controller:
            return

        try:
            # Make the move through the controller (no validation blocking)
            success, _game_state = self._controller.make_move(position, value)

            # Update the game screen with the new state
            game_screen = self.get_screen("game")
            if isinstance(game_screen, GameScreen):
                # Always update the board display
                current_game = self._controller.get_current_game()
                if current_game:
                    game_screen.update_board(current_game.board)

                # Check for game completion
                if self._controller.check_game_completion():
                    game_screen.set_game_state("Won!")
                    self._show_completion_message()

        except Exception as e:
            self._show_error(f"Error: {e}")

    def _handle_new_game_request(self) -> None:
        """Handle request to start a new game.

        Returns to the player input screen to configure a new game.
        """
        # Switch to player input screen
        self.switch_screen("player_input")

    def _show_completion_message(self) -> None:
        """Show a message when the game is completed."""
        # In a complete implementation, this could show a modal dialog
        # or notification about winning the game

    def _show_error(self, message: str) -> None:
        """Show an error message.

        Args:
            message: The error message to display.
        """
        # In a complete implementation, this could show a modal dialog
        # or notification with the error
        # For now, we'll just print to stderr
        self.notify(message, severity="error", timeout=5.0)

    def action_show_menu(self) -> None:
        """Action to show the main menu."""
        self.switch_screen("menu")

    def action_show_statistics(self) -> None:
        """Action to show statistics screen."""
        if self._controller and self._current_player:
            try:
                stats = self._controller.get_player_statistics(self._current_player)
                stats_screen = self.get_screen("statistics")
                if isinstance(stats_screen, StatisticsScreen):
                    stats_screen.set_statistics(stats)
                self.push_screen("statistics")
            except Exception as e:
                self._show_error(f"Failed to load statistics: {e}")
        else:
            self.push_screen("statistics")

    async def action_quit(self) -> None:
        """Action to quit the application."""
        self.exit()

    def set_controller(self, controller: AppController) -> None:
        """Set the application controller.

        This method allows injecting the controller after instantiation,
        which is useful for testing and configuration.

        Args:
            controller: The application controller to use.
        """
        self._controller = controller


class DemoSudokuApp(SudokuApp):
    """Demo version of Sudoku app without controller dependencies.

    This variant can be run without a fully configured controller,
    useful for testing the UI independently from the business logic.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize the demo application."""
        super().__init__(controller=None, **kwargs)

    def _start_game_screen(self, game_state=None) -> None:
        """Start a demo game screen.

        Args:
            game_state: Ignored in demo mode.
        """
        from sudoku.domain.entities.board import Board
        from sudoku.domain.value_objects.board_size import BoardSize

        # Create a demo board
        board = Board(BoardSize(9, 9, 3, 3))

        # Add some demo fixed cells
        demo_positions = [
            (0, 0, 5),
            (0, 3, 6),
            (0, 6, 8),
            (1, 1, 7),
            (1, 4, 2),
            (2, 2, 3),
            (2, 5, 9),
        ]

        for row, col, value in demo_positions:
            from sudoku.domain.value_objects.position import Position

            board.set_cell_value(Position(row, col), value, is_fixed=True)

        game_screen = GameScreen(
            board=board,
            player_name=self._current_player,
            difficulty=self._current_difficulty,
        )

        # Uninstall old game screen if it exists, then install the new one
        if self.is_screen_installed("game"):
            self.uninstall_screen("game")
        self.install_screen(game_screen, name="game")
        self.switch_screen("game")

    def _handle_move(self, position, value: int | None) -> None:
        """Handle move in demo mode.

        Args:
            position: The position where the move was made.
            value: The value placed, or None to clear.
        """
        # In demo mode, just allow the move without validation


def run_app(controller: AppController | None = None) -> None:
    """Run the Sudoku application.

    Args:
        controller: Optional application controller. If None, runs in demo mode.
    """
    app = SudokuApp(controller=controller) if controller else DemoSudokuApp()

    app.run()


if __name__ == "__main__":
    # Run in demo mode when executed directly
    run_app()
