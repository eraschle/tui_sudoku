"""Sudoku game rules validation service.

This module provides domain services for validating Sudoku game rules,
including checking for duplicates in rows, columns, and boxes.
"""

from sudoku.domain.entities.board import Board
from sudoku.domain.value_objects.position import Position


class GameRules:
    """Domain service for Sudoku game rules validation.

    Provides methods to validate Sudoku rules: no duplicate non-empty
    values in any row, column, or box.
    """

    @staticmethod
    def is_valid_row(board: Board, row_index: int) -> bool:
        """Check if a row contains no duplicate values.

        Args:
            board: The board to check.
            row_index: The row index to validate.

        Returns:
            True if the row is valid (no duplicates), False otherwise.

        Raises:
            IndexError: If row index is out of bounds.
        """
        row_cells = board.get_row(row_index)
        values = [
            cell.get_numeric_value()
            for cell in row_cells
            if not cell.is_empty()
        ]
        return len(values) == len(set(values))

    @staticmethod
    def is_valid_column(board: Board, col_index: int) -> bool:
        """Check if a column contains no duplicate values.

        Args:
            board: The board to check.
            col_index: The column index to validate.

        Returns:
            True if the column is valid (no duplicates), False otherwise.

        Raises:
            IndexError: If column index is out of bounds.
        """
        col_cells = board.get_column(col_index)
        values = [
            cell.get_numeric_value()
            for cell in col_cells
            if not cell.is_empty()
        ]
        return len(values) == len(set(values))

    @staticmethod
    def is_valid_box(board: Board, position: Position) -> bool:
        """Check if a box contains no duplicate values.

        Args:
            board: The board to check.
            position: A position within the box to validate.

        Returns:
            True if the box is valid (no duplicates), False otherwise.

        Raises:
            IndexError: If position is out of bounds.
        """
        box_cells = board.get_box(position)
        values = [
            cell.get_numeric_value()
            for cell in box_cells
            if not cell.is_empty()
        ]
        return len(values) == len(set(values))

    @classmethod
    def is_valid_placement(
        cls, board: Board, position: Position, value: int
    ) -> bool:
        """Check if placing a value at a position would be valid.

        Validates that placing the value would not violate Sudoku rules
        by creating duplicates in the row, column, or box.

        Args:
            board: The board to check.
            position: The position where the value would be placed.
            value: The value to check (must be positive).

        Returns:
            True if the placement would be valid, False otherwise.

        Raises:
            IndexError: If position is out of bounds.
            ValueError: If value is not positive.
        """
        if value <= 0:
            msg = f"Value must be positive, got {value}"
            raise ValueError(msg)

        row_cells = board.get_row(position.row)
        for cell in row_cells:
            if not cell.is_empty() and cell.get_numeric_value() == value:
                return False

        col_cells = board.get_column(position.col)
        for cell in col_cells:
            if not cell.is_empty() and cell.get_numeric_value() == value:
                return False

        box_cells = board.get_box(position)
        for cell in box_cells:
            if not cell.is_empty() and cell.get_numeric_value() == value:
                return False

        return True

    @classmethod
    def is_valid_board(cls, board: Board) -> bool:
        """Check if the entire board is valid.

        Validates all rows, columns, and boxes according to Sudoku rules.

        Args:
            board: The board to validate.

        Returns:
            True if the board is valid, False otherwise.
        """
        for row_idx in range(board.size.rows):
            if not cls.is_valid_row(board, row_idx):
                return False

        for col_idx in range(board.size.cols):
            if not cls.is_valid_column(board, col_idx):
                return False

        for row in range(0, board.size.rows, board.size.box_rows):
            for col in range(0, board.size.cols, board.size.box_cols):
                position = Position(row, col)
                if not cls.is_valid_box(board, position):
                    return False

        return True

    @classmethod
    def is_solved(cls, board: Board) -> bool:
        """Check if the board is completely and correctly solved.

        A board is solved if it is complete (all cells filled) and valid
        (follows all Sudoku rules).

        Args:
            board: The board to check.

        Returns:
            True if the board is solved, False otherwise.
        """
        return board.is_complete() and cls.is_valid_board(board)

    @classmethod
    def get_candidates(cls, board: Board, position: Position) -> set[int]:
        """Get all valid candidate values for a position.

        Returns the set of values that could be validly placed at the
        given position without violating Sudoku rules.

        Args:
            board: The board to check.
            position: The position to get candidates for.

        Returns:
            Set of valid candidate values.

        Raises:
            IndexError: If position is out of bounds.
        """
        if not board.get_cell(position).is_empty():
            return set()

        all_values = set(range(1, board.size.rows + 1))

        row_cells = board.get_row(position.row)
        row_values = {
            cell.get_numeric_value()
            for cell in row_cells
            if not cell.is_empty()
        }

        col_cells = board.get_column(position.col)
        col_values = {
            cell.get_numeric_value()
            for cell in col_cells
            if not cell.is_empty()
        }

        box_cells = board.get_box(position)
        box_values = {
            cell.get_numeric_value()
            for cell in box_cells
            if not cell.is_empty()
        }

        used_values = row_values | col_values | box_values
        return all_values - used_values
