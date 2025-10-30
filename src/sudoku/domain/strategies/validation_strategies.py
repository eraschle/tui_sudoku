"""Concrete validation strategy implementations.

This module provides various validation strategies following
the Strategy Pattern for flexible validation modes.
"""

from __future__ import annotations

import logging

from sudoku.domain.entities.board import Board
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.validators.sudoku_validator import SudokuValidator

logger = logging.getLogger(__name__)


class StrictSudokuValidation:
    """Strict Sudoku rule validation strategy.

    Validates moves according to standard Sudoku rules:
    - No duplicates in row
    - No duplicates in column
    - No duplicates in box
    """

    def __init__(self, validator: SudokuValidator) -> None:
        """Initialize with a Sudoku validator.

        Args:
            validator: Validator for Sudoku rules.
        """
        self._validator = validator

    def validate_move(
        self, board: Board, position: Position, value: int
    ) -> bool:
        """Validate move using strict Sudoku rules.

        Args:
            board: The game board.
            position: Position where move will be made.
            value: Value to place (1-9).

        Returns:
            bool: True if move follows all Sudoku rules.
        """
        # Convert board to 2D list for validator
        board_2d = self._board_to_list(board)

        # Clear the target cell for validation
        board_2d[position.row][position.col] = 0

        return self._validator.is_valid_move(
            board_2d,
            position.row,
            position.col,
            value,
            board.size.box_cols,
            board.size.box_rows,
        )

    def _board_to_list(self, board: Board) -> list[list[int]]:
        """Convert Board entity to 2D list.

        Args:
            board: Board entity.

        Returns:
            2D list representation (empty cells as 0).
        """
        size = board.size.rows
        result = []
        for row in range(size):
            row_values = []
            for col in range(size):
                pos = Position(row, col)
                cell = board.get_cell(pos)
                numeric_value = cell.get_numeric_value()
                row_values.append(numeric_value if numeric_value else 0)
            result.append(row_values)
        return result


class NoValidation:
    """No validation strategy - allow all moves.

    Useful for practice mode or when users want to
    experiment without constraints.
    """

    def validate_move(
        self, board: Board, position: Position, value: int
    ) -> bool:
        """Allow all moves without validation.

        Args:
            board: The game board (unused).
            position: Position where move will be made (unused).
            value: Value to place (unused).

        Returns:
            bool: Always True (all moves allowed).
        """
        return True


class RelaxedValidation:
    """Relaxed validation strategy - only validate within box.

    This is an easier mode that only checks for duplicates
    within the 3x3 box, ignoring row/column constraints.
    """

    def validate_move(
        self, board: Board, position: Position, value: int
    ) -> bool:
        """Validate move only within the box.

        Args:
            board: The game board.
            position: Position where move will be made.
            value: Value to place (1-9).

        Returns:
            bool: True if value doesn't exist in the box.
        """
        # Calculate box boundaries
        box_row_start = (position.row // board.size.box_rows) * board.size.box_rows
        box_col_start = (position.col // board.size.box_cols) * board.size.box_cols

        # Check box for duplicates
        for row in range(box_row_start, box_row_start + board.size.box_rows):
            for col in range(box_col_start, box_col_start + board.size.box_cols):
                # Skip the target cell
                if row == position.row and col == position.col:
                    continue

                cell = board.get_cell(Position(row, col))
                if cell.get_numeric_value() == value:
                    logger.debug(
                        "Relaxed validation failed: %d already in box at (%d, %d)",
                        value, row, col
                    )
                    return False

        return True
