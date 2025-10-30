"""Cursor navigator for Sudoku game screen.

This module handles cursor navigation logic,
following the Single Responsibility Principle.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.tui.input.key_mappings import NavigationKey

if TYPE_CHECKING:
    from sudoku.domain.entities.board import Board


class CursorNavigator:
    """Handles cursor navigation for the game screen.

    Responsibilities:
    - Cursor position management
    - Navigation direction handling
    - Boundary checking
    """

    def __init__(self, initial_position: Position | None = None) -> None:
        """Initialize the cursor navigator.

        Args:
            initial_position: Initial cursor position.
        """
        self._position = initial_position or Position(0, 0)

    @property
    def position(self) -> Position:
        """Get current cursor position."""
        return self._position

    def set_position(self, position: Position) -> None:
        """Set cursor position.

        Args:
            position: New cursor position.
        """
        self._position = position

    def move(
        self,
        direction: NavigationKey,
        board: Board | None
    ) -> Position:
        """Move cursor in the specified direction.

        Args:
            direction: Navigation direction.
            board: Current board (for boundary checking).

        Returns:
            Position: New cursor position.
        """
        if not board:
            return self._position

        row = self._position.row
        col = self._position.col

        # Calculate new position based on direction
        if direction == NavigationKey.UP:
            row = max(0, row - 1)
        elif direction == NavigationKey.DOWN:
            row = min(board.size.rows - 1, row + 1)
        elif direction == NavigationKey.LEFT:
            col = max(0, col - 1)
        elif direction == NavigationKey.RIGHT:
            col = min(board.size.cols - 1, col + 1)

        # Update and return new position
        self._position = Position(row, col)
        return self._position
