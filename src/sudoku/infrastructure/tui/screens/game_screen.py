"""Game screen for playing Sudoku.

This module provides the main game screen where users interact with
the Sudoku board, make moves, and complete puzzles.
"""

import logging
from collections.abc import Callable
from datetime import timedelta
from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.css.query import NoMatches
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Footer, Header

from sudoku.domain.entities.board import Board
from sudoku.domain.strategies import (
    NoValidation,
    RelaxedValidation,
    StrictSudokuValidation,
    ValidationStrategy,
    create_validation_strategy,
)
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.tui.components.board_widget import BoardWidget
from sudoku.infrastructure.tui.components.status_widget import StatusWidget
from sudoku.infrastructure.tui.helpers import (
    CursorNavigator,
    GameInputHandler,
    GameStateManager,
)
from sudoku.infrastructure.tui.input.key_mappings import KeyMapper, NavigationKey

logger = logging.getLogger(__name__)


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
        ("m", "cycle_validation_mode", "Cycle Mode"),
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
        validation_strategy: ValidationStrategy | None = None,
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
            validation_strategy: Strategy for validation (optional, defaults to strict).
            name: The name of the screen.
            id: The ID of the screen.
        """
        super().__init__(name=name, id=id)
        self._board = board
        self._player_name = player_name
        self._difficulty = difficulty
        self._on_new_game = on_new_game
        self._on_quit = on_quit

        # Use provided strategy or default to strict
        if validation_strategy is None:
            validation_strategy = create_validation_strategy("strict")
        self._validation_strategy = validation_strategy

        # Create helper objects (Composition over inheritance)
        self._input_handler = GameInputHandler(on_move=on_move)
        self._state_manager = GameStateManager()
        self._navigator = CursorNavigator(Position(0, 0))

        # Keep only UI-specific attributes
        self._key_mapper = KeyMapper(enable_qwertz=True, enable_vim_navigation=True)
        self._cursor_opacity = 80  # Default 80%
        self._validation_enabled = False

    def compose(self) -> ComposeResult:
        """Compose the game screen layout.

        Returns:
            The composed screen layout.
        """
        yield Header()

        yield StatusWidget(
            player_name=self._player_name,
            difficulty=self._difficulty,
            elapsed_time=self._state_manager.elapsed_time,
            game_state=self._state_manager.game_state,
            id="game-status",
        )

        with Container(id="game-container"), Vertical(id="board-container"):
            yield BoardWidget(
                board=self._board,
                cursor_position=self._navigator.position,
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
        if self._state_manager.is_paused:
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
        """Handle number input by delegating to input handler.

        Args:
            number: The number that was input (1-9).
        """
        # Delegate input handling to helper
        success, error_message = self._input_handler.handle_number_input(
            self._board,
            self._navigator.position,
            number
        )

        if not success and error_message:
            self._show_message(error_message)
            return

        # Re-validate entire board after content change if validation is enabled
        if self._validation_enabled:
            # Re-validate all cells to reflect the impact of this change
            self._validate_all_cells()

            # Check if the current position has an error after validation
            if self._navigator.position in self._get_current_errors():
                self._show_message(f"Invalid placement: {number}")
            else:
                self._show_message(f"Valid: {number}")
        else:
            # Clear any previous error markers when validation is off
            self.clear_error(self._navigator.position)

    def _handle_clear_cell(self) -> None:
        """Handle clear cell by delegating to input handler."""
        success, error_message = self._input_handler.handle_clear_cell(
            self._board,
            self._navigator.position
        )

        if not success and error_message:
            self._show_message(error_message)
            return

        # Re-validate entire board after clearing a cell if validation is enabled
        if self._validation_enabled:
            # Re-validate all cells to reflect the impact of this change
            self._validate_all_cells()
            self._show_message("Cell cleared")

    def _handle_navigation(self, direction: NavigationKey) -> None:
        """Handle navigation by delegating to navigator.

        Args:
            direction: The navigation direction.
        """
        new_position = self._navigator.move(direction, self._board)
        self.set_cursor_position(new_position)

    def _update_timer_callback(self) -> None:
        """Update timer by delegating to state manager.

        This is called periodically by the timer interval.
        """
        self._state_manager.increment_time(1)
        self._update_status_widget()

    def _update_status_widget(self) -> None:
        """Update status widget with state from state manager."""
        try:
            status_widget = self.query_one("#game-status", StatusWidget)
            status_widget.update_status(
                elapsed_time=self._state_manager.elapsed_time,
                game_state=self._state_manager.game_state,
            )
        except NoMatches:
            logger.warning(
                "Status widget not found, cannot update status (elapsed_time=%s, state=%s)",
                self._state_manager.elapsed_time,
                self._state_manager.game_state,
            )
        except Exception as e:
            logger.error(
                "Failed to update status widget: %s",
                e,
                exc_info=True,
            )

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
        except NoMatches:
            logger.warning(
                "Status widget not found, message not displayed: %s",
                message,
            )
            # Fallback: show to user via notification
            self.notify(message, severity="information")
        except Exception as e:
            logger.error(
                "Failed to show message '%s': %s",
                message,
                e,
                exc_info=True,
            )

    def update_board(self, board: Board) -> None:
        """Update the displayed board.

        Args:
            board: The new board state.
        """
        self._board = board
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.set_board(board)
        except NoMatches:
            logger.warning(
                "Board widget not found, cannot update board display",
            )
            # Don't notify user - widget might not be mounted yet during initialization
        except Exception as e:
            logger.error(
                "Failed to update board display: %s",
                e,
                exc_info=True,
            )
            self.notify("Error updating board display", severity="error")

    def set_cursor_position(self, position: Position) -> None:
        """Set the cursor position.

        Args:
            position: The new cursor position.
        """
        self._navigator.set_position(position)
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.set_cursor_position(position)
        except NoMatches:
            logger.warning(
                "Board widget not found, cannot update cursor position to %s",
                position,
            )
        except Exception as e:
            logger.error(
                "Failed to set cursor position to %s: %s",
                position,
                e,
                exc_info=True,
            )

    def add_error(self, position: Position) -> None:
        """Mark a position as having an error.

        Args:
            position: The position with an error.
        """
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.add_error(position)
        except NoMatches:
            logger.warning(
                "Board widget not found, cannot mark error at position %s",
                position,
            )
        except Exception as e:
            logger.error(
                "Failed to add error marker at position %s: %s",
                position,
                e,
                exc_info=True,
            )

    def clear_error(self, position: Position) -> None:
        """Clear an error at a position.

        Args:
            position: The position to clear the error from.
        """
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.clear_error(position)
        except NoMatches:
            logger.warning(
                "Board widget not found, cannot clear error at position %s",
                position,
            )
        except Exception as e:
            logger.error(
                "Failed to clear error marker at position %s: %s",
                position,
                e,
                exc_info=True,
            )

    def clear_all_errors(self) -> None:
        """Clear all error markers."""
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.clear_all_errors()
        except NoMatches:
            logger.warning(
                "Board widget not found, cannot clear all error markers",
            )
        except Exception as e:
            logger.error(
                "Failed to clear all error markers: %s",
                e,
                exc_info=True,
            )

    def set_game_state(self, state: str) -> None:
        """Set game state via state manager.

        Args:
            state: The new game state (e.g., "In Progress", "Won", "Paused").
        """
        self._state_manager.set_state(state)
        self._update_status_widget()

    def set_elapsed_time(self, elapsed: timedelta) -> None:
        """Set elapsed time via state manager.

        Args:
            elapsed: The elapsed time.
        """
        self._state_manager.set_elapsed_time(elapsed)
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
        """Toggle pause by delegating to state manager."""
        self._state_manager.toggle_pause()

        if self._state_manager.is_paused:
            self._show_message("Game Paused - Press 'p' to resume")
        else:
            self._show_message("Game Resumed")

        self._update_status_widget()

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
            logger.debug(
                "Cursor opacity %d not in predefined levels, resetting to default",
                self._cursor_opacity,
            )
            self._cursor_opacity = 80

        # Update board widget
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            board_widget.set_cursor_opacity(self._cursor_opacity)
            self._show_message(f"Cursor opacity: {self._cursor_opacity}%")
        except NoMatches:
            logger.warning(
                "Board widget not found, cannot adjust cursor opacity to %d%%",
                self._cursor_opacity,
            )
            self.notify(
                f"Cursor opacity: {self._cursor_opacity}%",
                severity="information",
            )
        except Exception as e:
            logger.error(
                "Failed to adjust cursor opacity to %d%%: %s",
                self._cursor_opacity,
                e,
                exc_info=True,
            )
            self.notify("Error adjusting cursor transparency", severity="error")

    def action_cycle_validation_mode(self) -> None:
        """Cycle through validation modes."""
        modes = ["strict", "relaxed", "none"]

        # Detect current mode
        if isinstance(self._validation_strategy, StrictSudokuValidation):
            current_idx = 0
        elif isinstance(self._validation_strategy, RelaxedValidation):
            current_idx = 1
        else:  # NoValidation
            current_idx = 2

        # Get next mode
        next_idx = (current_idx + 1) % len(modes)
        next_mode = modes[next_idx]

        self.set_validation_strategy(next_mode)

    def set_validation_strategy(self, mode: str) -> None:
        """Change validation strategy at runtime.

        Args:
            mode: Validation mode ('strict', 'relaxed', 'none').
        """
        try:
            self._validation_strategy = create_validation_strategy(mode)
            logger.info("Validation strategy changed to: %s", mode)
            self._show_message(f"Validation mode: {mode.capitalize()}")

            # Re-validate all cells with new strategy
            if self._validation_enabled:
                self._validate_all_cells()
        except ValueError as e:
            logger.error("Failed to set validation strategy: %s", e)
            self._show_message(f"Invalid validation mode: {mode}")

    def _validate_move(self, value: int) -> bool:
        """Validate move using the current validation strategy.

        Args:
            value: The value to validate at current cursor position.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        if not self._board:
            return True

        # Use the injected validation strategy
        return self._validation_strategy.validate_move(
            self._board,
            self._navigator.position,
            value
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
                old_cursor = self._navigator.position
                self._navigator.set_position(position)
                is_valid = self._validate_move(value)
                self._navigator.set_position(old_cursor)

                if not is_valid:
                    self.add_error(position)

    def _get_current_errors(self) -> set[Position]:
        """Get the current set of error positions from the board widget.

        Returns:
            Set of positions with errors, or empty set if widget not found.
        """
        try:
            board_widget = self.query_one("#game-board", BoardWidget)
            return board_widget.errors
        except NoMatches:
            logger.warning("Board widget not found, cannot get error positions")
            return set()
        except Exception as e:
            logger.error(
                "Failed to get error positions: %s",
                e,
                exc_info=True,
            )
            return set()

    @property
    def cursor_position(self) -> Position:
        """Get current cursor position from navigator.

        Returns:
            The current cursor position.
        """
        return self._navigator.position

    @property
    def is_paused(self) -> bool:
        """Check if game is paused from state manager.

        Returns:
            True if the game is paused, False otherwise.
        """
        return self._state_manager.is_paused
