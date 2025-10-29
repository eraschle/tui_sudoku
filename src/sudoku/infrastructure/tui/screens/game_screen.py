"""Game screen for playing Sudoku.

This module provides the main game screen where users interact with
the Sudoku board, make moves, and complete puzzles.
"""

from collections.abc import Callable
from datetime import timedelta
from typing import ClassVar

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
from sudoku.infrastructure.validators.sudoku_validator import SudokuValidator


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

    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("n", "new_game", "New Game"),
        ("s", "show_statistics", "Statistics"),
        ("escape", "back_to_menu", "Menu"),
        ("p", "pause", "Pause"),
        ("v", "toggle_validation", "Validation"),
        ("t", "adjust_transparency", "Transparency"),
    ]

    CSS: ClassVar[str] = """
    GameScreen {
        align: center middle;
    }

    #game-container {
        width: 100%;
        height: 100%;
        border: none;
        background: $surface;
    }

    #board-container {
        align: center middle;
        width: 100%;
        height: 100%;
        padding: 0;
    }

    BoardWidget {
        width: 100%;
        height: 100%;
    }

    StatusWidget {
        dock: top;
        height: 3;
    }

    Footer {
        dock: bottom;
        height: 1;
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
        validator: SudokuValidator | None = None,
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
            validator: Validator for Sudoku rule validation (optional).
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
        self._validator = validator

        self._cursor_position = Position(0, 0)
        self._key_mapper = KeyMapper(enable_qwertz=True, enable_vim_navigation=True)
        self._elapsed_time = timedelta()
        self._game_state = "In Progress"
        self._is_paused = False
        self._validation_enabled = False
        self._cursor_opacity = 80  # Default 80%

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
                cursor_opacity=self._cursor_opacity,
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
        # When paused, block all input except 'p' which is handled by BINDINGS
        if self._is_paused:
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

        # Always allow the move (no blocking)
        if self._on_move:
            self._on_move(self._cursor_position, number)
        else:
            # Demo mode - update board directly
            try:
                self._board.set_cell_value(self._cursor_position, number, is_fixed=False)
                self.refresh()
            except Exception:
                pass

        # Validate only if validation mode is enabled
        if self._validation_enabled:
            is_valid = self._validate_move(number)
            if not is_valid:
                self.add_error(self._cursor_position)
                self._show_message(f"Invalid placement: {number}")
            else:
                self.clear_error(self._cursor_position)
                self._show_message(f"Valid: {number}")
        else:
            # Clear any previous error markers when validation is off
            self.clear_error(self._cursor_position)

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

    def action_toggle_validation(self) -> None:
        """Action to toggle validation mode on/off."""
        self._validation_enabled = not self._validation_enabled
        if self._validation_enabled:
            self._show_message("Validation ON - Invalid moves shown in red")
            # Validate all current moves
            self._validate_all_cells()
        else:
            self._show_message("Validation OFF - All moves allowed")
            # Clear all error markers
            self.clear_all_errors()

    def action_adjust_transparency(self) -> None:
        """Action to adjust cursor transparency."""
        # Cycle through transparency levels: 100% -> 80% -> 60% -> 40% -> 20% -> 100%
        transparency_levels = [100, 80, 60, 40, 20]
        try:
            current_index = transparency_levels.index(self._cursor_opacity)
            next_index = (current_index + 1) % len(transparency_levels)
            self._cursor_opacity = transparency_levels[next_index]
        except ValueError:
            # Current value not in list, reset to default
            self._cursor_opacity = 80

        # Update board widget
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.set_cursor_opacity(self._cursor_opacity)
            self._show_message(f"Cursor opacity: {self._cursor_opacity}%")
        except Exception:
            pass

    def _board_to_list(self) -> list[list[int]]:
        """Convert Board entity to 2D list for validator.

        Returns:
            2D list representation of the board (empty cells as 0).
        """
        if not self._board:
            return []

        size = self._board.size.rows
        result = []
        for row in range(size):
            row_values = []
            for col in range(size):
                position = Position(row, col)
                cell = self._board.get_cell(position)
                numeric_value = cell.get_numeric_value()
                if numeric_value is None:
                    row_values.append(0)
                else:
                    row_values.append(numeric_value)
            result.append(row_values)
        return result

    def _validate_move(self, value: int) -> bool:
        """Validate if a move is valid according to Sudoku rules.

        Args:
            value: The value to validate at current cursor position.

        Returns:
            True if the move is valid, False otherwise.
        """
        if not self._board:
            return True

        # Fallback to True if no validator is injected
        if self._validator is None:
            return True

        # Convert board to 2D list format
        board_2d = self._board_to_list()

        # Clear the current cell in the board copy for validation
        # The validator expects the cell to be empty when checking if a move is valid
        board_2d[self._cursor_position.row][self._cursor_position.col] = 0

        # Delegate validation to the injected validator
        return self._validator.is_valid_move(
            board_2d,
            self._cursor_position.row,
            self._cursor_position.col,
            value,
            self._board.size.box_cols,
            self._board.size.box_rows,
        )

    def _validate_all_cells(self) -> None:
        """Validate all cells on the board and mark errors."""
        if not self._board:
            return

        self.clear_all_errors()

        for row in range(self._board.size.rows):
            for col in range(self._board.size.cols):
                position = Position(row, col)
                cell = self._board.get_cell(position)
                value = cell.get_numeric_value()

                # Skip empty and fixed cells
                if value is None or cell.is_fixed:
                    continue

                # Temporarily set cursor to this position for validation
                old_cursor = self._cursor_position
                self._cursor_position = position
                is_valid = self._validate_move(value)
                self._cursor_position = old_cursor

                if not is_valid:
                    self.add_error(position)

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
