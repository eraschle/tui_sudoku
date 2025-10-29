"""Game screen for playing Sudoku.

This module provides the main game screen where users interact with
the Sudoku board, make moves, and complete puzzles.
"""

from collections.abc import Callable
from datetime import timedelta

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Footer, Header

from sudoku.domain.entities.board import Board
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.tui.components.board_widget import BoardWidget
from sudoku.infrastructure.tui.components.status_widget import StatusWidget
from sudoku.infrastructure.tui.input.key_mappings import KeyMapper, NavigationKey


class GameScreen(Screen):
    """Main game screen for playing Sudoku.

    This screen provides:
    - Interactive board with cursor navigation
    - Number input via QWERTZ or standard keys
    - Vim-style navigation (hjkl) and arrow keys
    - Status bar showing player info, difficulty, and timer
    - Game actions (new game, quit, clear cell, etc.)

    The screen delegates game logic to the controller and focuses
    on presentation and user input handling.

    Attributes:
        board: The current game board.
        player_name: Name of the current player.
        difficulty: Current difficulty level.
        on_move: Callback for when a move is made.
        on_new_game: Callback for new game request.
        on_quit: Callback for quit request.
    """

    BINDINGS = [
        ("n", "new_game", "New Game"),
        ("s", "show_statistics", "Statistics"),
        ("escape", "back_to_menu", "Menu"),
        ("p", "pause", "Pause"),
    ]

    CSS = """
    GameScreen {
        align: center middle;
    }

    #game-container {
        width: auto;
        height: auto;
        border: thick $primary;
        background: $surface;
    }

    #board-container {
        align: center middle;
        padding: 1;
    }

    StatusWidget {
        dock: top;
    }

    Footer {
        dock: bottom;
    }
    """

    def __init__(
        self,
        board: Board | None = None,
        player_name: str = "",
        difficulty: str = "",
        on_move: Callable[[Position, int | None], None] | None = None,
        on_new_game: Callable[[], None] | None = None,
        on_quit: Callable[[], None] | None = None,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize the game screen.

        Args:
            board: The game board to display.
            player_name: Name of the current player.
            difficulty: Current difficulty level.
            on_move: Callback(position, value) for when a move is made.
            on_new_game: Callback for new game request.
            on_quit: Callback for quit request.
            name: The name of the screen.
            id: The ID of the screen.
        """
        super().__init__(name=name, id=id)
        self._board = board
        self._player_name = player_name
        self._difficulty = difficulty
        self._on_move = on_move
        self._on_new_game = on_new_game
        self._on_quit = on_quit

        self._cursor_position = Position(0, 0)
        self._key_mapper = KeyMapper(enable_qwertz=True, enable_vim_navigation=True)
        self._elapsed_time = timedelta()
        self._game_state = "In Progress"
        self._is_paused = False

    def compose(self) -> ComposeResult:
        """Compose the game screen layout.

        Returns:
            The composed screen layout.
        """
        yield Header()

        yield StatusWidget(
            player_name=self._player_name,
            difficulty=self._difficulty,
            elapsed_time=self._elapsed_time,
            game_state=self._game_state,
            id="game-status",
        )

        with Container(id="game-container"), Vertical(id="board-container"):
            yield BoardWidget(
                board=self._board,
                cursor_position=self._cursor_position,
                id="game-board",
            )

        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted.

        Sets up the initial display state and timer updates.
        """
        if self._board:
            self.update_board(self._board)

        # Set up timer update interval
        self.set_interval(1.0, self._update_timer_callback)

    def on_key(self, event: Key) -> None:
        """Handle keyboard input.

        Args:
            event: The key event.
        """
        if self._is_paused:
            # Only allow unpause when paused
            if event.key == "p":
                self.action_pause()
            return

        key = event.key

        # Try to handle as number input
        number = self._key_mapper.get_number(key)
        if number is not None:
            self._handle_number_input(number)
            event.prevent_default()
            return

        # Try to handle as navigation
        navigation = self._key_mapper.get_navigation(key)
        if navigation is not None:
            self._handle_navigation(navigation)
            event.prevent_default()
            return

        # Try to handle as game action
        # Note: Some keys conflict with QWERTZ (e.g., 'q' for quit vs. '1')
        # We prioritize number input, so 'q' in game context enters '1'
        # Use 'escape' to go back to menu instead
        if key in ["x", "delete"]:
            self._handle_clear_cell()
            event.prevent_default()
            return

    def _handle_number_input(self, number: int) -> None:
        """Handle number input from keyboard.

        Args:
            number: The number that was input (1-9).
        """
        if not self._board:
            return

        # Check if current cell is fixed
        try:
            cell = self._board.get_cell(self._cursor_position)
            if cell.is_fixed:
                self._show_message("Cannot modify a fixed cell")
                return
        except IndexError:
            return

        # Call the move callback if provided
        if self._on_move:
            self._on_move(self._cursor_position, number)

    def _handle_clear_cell(self) -> None:
        """Handle clearing the current cell."""
        if not self._board:
            return

        # Check if current cell is fixed
        try:
            cell = self._board.get_cell(self._cursor_position)
            if cell.is_fixed:
                self._show_message("Cannot modify a fixed cell")
                return
        except IndexError:
            return

        # Call the move callback with None to clear
        if self._on_move:
            self._on_move(self._cursor_position, None)

    def _handle_navigation(self, direction: NavigationKey) -> None:
        """Handle cursor navigation.

        Args:
            direction: The navigation direction.
        """
        if not self._board:
            return

        row = self._cursor_position.row
        col = self._cursor_position.col

        # Calculate new position based on direction
        if direction == NavigationKey.UP:
            row = max(0, row - 1)
        elif direction == NavigationKey.DOWN:
            row = min(self._board.size.rows - 1, row + 1)
        elif direction == NavigationKey.LEFT:
            col = max(0, col - 1)
        elif direction == NavigationKey.RIGHT:
            col = min(self._board.size.cols - 1, col + 1)

        # Update cursor position
        new_position = Position(row, col)
        self.set_cursor_position(new_position)

    def _update_timer_callback(self) -> None:
        """Update the elapsed time display.

        This is called periodically by the timer interval.
        """
        if not self._is_paused and self._game_state == "In Progress":
            self._elapsed_time += timedelta(seconds=1)
            self._update_status_widget()

    def _update_status_widget(self) -> None:
        """Update the status widget with current game state."""
        try:
            status_widget = self.query_one("#game-status", StatusWidget)
            status_widget.update_status(
                elapsed_time=self._elapsed_time,
                game_state=self._game_state,
            )
        except Exception:
            pass  # Widget might not be mounted yet

    def _show_message(self, message: str) -> None:
        """Display a message in the status bar.

        Args:
            message: The message to display.
        """
        try:
            status_widget = self.query_one("#game-status", StatusWidget)
            status_widget.set_message(message)
            # Clear message after 3 seconds
            self.set_timer(3.0, status_widget.clear_message)
        except Exception:
            pass

    def update_board(self, board: Board) -> None:
        """Update the displayed board.

        Args:
            board: The new board state.
        """
        self._board = board
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.set_board(board)
        except Exception:
            pass  # Widget might not be mounted yet

    def set_cursor_position(self, position: Position) -> None:
        """Set the cursor position.

        Args:
            position: The new cursor position.
        """
        self._cursor_position = position
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.set_cursor_position(position)
        except Exception:
            pass  # Widget might not be mounted yet

    def add_error(self, position: Position) -> None:
        """Mark a position as having an error.

        Args:
            position: The position with an error.
        """
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.add_error(position)
        except Exception:
            pass

    def clear_error(self, position: Position) -> None:
        """Clear an error at a position.

        Args:
            position: The position to clear the error from.
        """
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.clear_error(position)
        except Exception:
            pass

    def clear_all_errors(self) -> None:
        """Clear all error markers."""
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.clear_all_errors()
        except Exception:
            pass

    def set_game_state(self, state: str) -> None:
        """Set the game state.

        Args:
            state: The new game state (e.g., "In Progress", "Won", "Paused").
        """
        self._game_state = state
        self._update_status_widget()

    def set_elapsed_time(self, elapsed: timedelta) -> None:
        """Set the elapsed time.

        Args:
            elapsed: The elapsed time.
        """
        self._elapsed_time = elapsed
        self._update_status_widget()

    def action_new_game(self) -> None:
        """Action to start a new game."""
        if self._on_new_game:
            self._on_new_game()
        else:
            self.app.push_screen("player_input")

    def action_show_statistics(self) -> None:
        """Action to show statistics."""
        self.app.push_screen("statistics")

    def action_back_to_menu(self) -> None:
        """Action to return to the main menu."""
        self.app.pop_screen()

    def action_pause(self) -> None:
        """Action to pause/resume the game."""
        self._is_paused = not self._is_paused
        if self._is_paused:
            self.set_game_state("Paused")
            self._show_message("Game Paused - Press 'p' to resume")
        else:
            self.set_game_state("In Progress")
            self._show_message("Game Resumed")

    @property
    def cursor_position(self) -> Position:
        """Get the current cursor position.

        Returns:
            The current cursor position.
        """
        return self._cursor_position

    @property
    def is_paused(self) -> bool:
        """Check if the game is paused.

        Returns:
            True if the game is paused, False otherwise.
        """
        return self._is_paused
