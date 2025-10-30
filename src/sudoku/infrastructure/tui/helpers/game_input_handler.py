"""Game input handler for Sudoku game screen.

This module handles all user input logic for the game screen,
following the Single Responsibility Principle.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

from sudoku.domain.value_objects.position import Position

if TYPE_CHECKING:
    from sudoku.domain.entities.board import Board

logger = logging.getLogger(__name__)


class GameInputHandler:
    """Handles user input for the game screen.

    Responsibilities:
    - Number input validation
    - Fixed cell checking
    - Input delegation to callbacks
    """

    def __init__(
        self,
        on_move: Callable[[Position, int | None], None] | None = None,
    ) -> None:
        """Initialize the input handler.

        Args:
            on_move: Callback for when a move is made.
        """
        self._on_move = on_move

    def handle_number_input(
        self,
        board: Board | None,
        position: Position,
        number: int
    ) -> tuple[bool, str | None]:
        """Handle number input from keyboard.

        Args:
            board: Current game board.
            position: Position where number should be placed.
            number: The number to place (1-9).

        Returns:
            tuple[bool, str | None]: (success, error_message)
                - success: True if input was handled
                - error_message: None if successful, error string if failed
        """
        if not board:
            return False, "No board available"

        # Check if current cell is fixed
        try:
            cell = board.get_cell(position)
            if cell.is_fixed:
                return False, "Cannot modify a fixed cell"
        except IndexError:
            logger.warning("Invalid position for input: %s", position)
            return False, "Invalid position"

        # Delegate to callback
        if self._on_move:
            self._on_move(position, number)
            return True, None

        return False, "No move handler configured"

    def handle_clear_cell(
        self,
        board: Board | None,
        position: Position
    ) -> tuple[bool, str | None]:
        """Handle clearing the current cell.

        Args:
            board: Current game board.
            position: Position to clear.

        Returns:
            tuple[bool, str | None]: (success, error_message)
        """
        if not board:
            return False, "No board available"

        # Check if current cell is fixed
        try:
            cell = board.get_cell(position)
            if cell.is_fixed:
                return False, "Cannot modify a fixed cell"
        except IndexError:
            logger.warning("Invalid position for clear: %s", position)
            return False, "Invalid position"

        # Delegate to callback
        if self._on_move:
            self._on_move(position, None)
            return True, None

        return False, "No move handler configured"
