"""Protocol for Sudoku board validation.

This module defines the protocol that board validators must implement
to check if a board configuration is valid according to Sudoku rules.
"""

from typing import Protocol

from sudoku.domain.entities.board import Board
from sudoku.domain.value_objects.position import Position


class BoardValidator(Protocol):
    """Protocol for validating Sudoku boards.

    Implementations should verify that boards follow Sudoku rules:
    no duplicate values in rows, columns, or boxes.
    """

    def is_valid(self, board: Board) -> bool:
        """Check if the entire board is valid.

        Args:
            board: The board to validate.

        Returns:
            True if the board is valid, False otherwise.
        """
        ...

    def is_valid_placement(
        self, board: Board, position: Position, value: int
    ) -> bool:
        """Check if placing a value at a position would be valid.

        Args:
            board: The board to check.
            position: The position where the value would be placed.
            value: The value to check.

        Returns:
            True if the placement would be valid, False otherwise.
        """
        ...
