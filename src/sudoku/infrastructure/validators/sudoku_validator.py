"""Sudoku board validation implementation.

This module implements a BoardValidator to validate Sudoku board states,
moves, and completeness according to standard Sudoku rules.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class BoardValidator(Protocol):
    """Protocol for board validation."""

    def is_valid_move(
        self,
        board: list[list[int]],
        row: int,
        col: int,
        num: int,
        box_width: int,
        box_height: int,
    ) -> bool:
        """Check if a move is valid.

        Args:
            board: The current board state
            row: Row index
            col: Column index
            num: Number to place
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if move is valid, False otherwise
        """
        ...

    def is_board_complete(self, board: list[list[int]], box_width: int, box_height: int) -> bool:
        """Check if board is completely filled and valid.

        Args:
            board: The board to check
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if board is complete and valid, False otherwise
        """
        ...

    def is_board_valid(self, board: list[list[int]], box_width: int, box_height: int) -> bool:
        """Check if current board state is valid.

        Args:
            board: The board to check
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if board state is valid, False otherwise
        """
        ...


class SudokuValidator:
    """Validate Sudoku boards and moves.

    This validator implements the standard Sudoku rules:
    - Each row must contain unique numbers from 1 to board_size
    - Each column must contain unique numbers from 1 to board_size
    - Each box must contain unique numbers from 1 to board_size
    - Empty cells are represented by 0

    Supports both 9x9 (3x3 boxes) and 6x6 (3x2 boxes) boards.
    """

    def is_valid_move(
        self,
        board: list[list[int]],
        row: int,
        col: int,
        num: int,
        box_width: int,
        box_height: int,
    ) -> bool:
        """Validate if placing a number at position is allowed.

        Checks if the move would violate any Sudoku rules without
        actually modifying the board.

        Args:
            board: The current board state
            row: Row index (0-based)
            col: Column index (0-based)
            num: Number to place (1 to board_size)
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if the move is valid according to Sudoku rules,
            False otherwise
        """
        board_size = box_width * box_height

        # Validate input parameters
        if not self._is_valid_position(row, col, board_size):
            return False

        if not self._is_valid_number(num, board_size):
            return False

        # Check if cell is already occupied
        if board[row][col] != 0:
            return False

        # Check row constraint
        if self._number_in_row(board, row, num, board_size):
            return False

        # Check column constraint
        if self._number_in_column(board, col, num, board_size):
            return False

        # Check box constraint
        return not self._number_in_box(board, row, col, num, box_width, box_height)

    def is_board_complete(
        self, board: list[list[int]], box_width: int, box_height: int
    ) -> bool:
        """Check if the board is completely filled with valid values.

        A board is complete when:
        - All cells are filled (no zeros)
        - All Sudoku rules are satisfied

        Args:
            board: The board to check
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if board is complete and valid, False otherwise
        """
        board_size = box_width * box_height

        # Check if all cells are filled
        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] == 0:
                    return False

        # Check if board is valid
        return self.is_board_valid(board, box_width, box_height)

    def is_board_valid(
        self, board: list[list[int]], box_width: int, box_height: int
    ) -> bool:
        """Check if the current board state is valid.

        A board is valid when all filled cells satisfy Sudoku rules.
        Empty cells (zeros) are allowed.

        Args:
            board: The board to check
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if board state is valid, False otherwise
        """
        board_size = box_width * box_height

        # Validate all rows
        for row in range(board_size):
            if not self._is_row_valid(board, row, board_size):
                return False

        # Validate all columns
        for col in range(board_size):
            if not self._is_column_valid(board, col, board_size):
                return False

        # Validate all boxes
        # Number of boxes = board_size / box dimension
        num_box_rows = board_size // box_height
        num_box_cols = board_size // box_width

        for box_row in range(num_box_rows):
            for box_col in range(num_box_cols):
                if not self._is_box_valid(
                    board, box_row, box_col, box_width, box_height
                ):
                    return False

        return True

    def _is_valid_position(self, row: int, col: int, board_size: int) -> bool:
        """Check if position is within board bounds.

        Args:
            row: Row index
            col: Column index
            board_size: Size of the board

        Returns:
            True if position is valid, False otherwise
        """
        return 0 <= row < board_size and 0 <= col < board_size

    def _is_valid_number(self, num: int, board_size: int) -> bool:
        """Check if number is valid for the board.

        Args:
            num: Number to check
            board_size: Size of the board

        Returns:
            True if number is valid, False otherwise
        """
        return 1 <= num <= board_size

    def _number_in_row(
        self, board: list[list[int]], row: int, num: int, board_size: int
    ) -> bool:
        """Check if number exists in the specified row.

        Args:
            board: The board to check
            row: Row index
            num: Number to find
            board_size: Size of the board

        Returns:
            True if number exists in row, False otherwise
        """
        return num in board[row]

    def _number_in_column(
        self, board: list[list[int]], col: int, num: int, board_size: int
    ) -> bool:
        """Check if number exists in the specified column.

        Args:
            board: The board to check
            col: Column index
            num: Number to find
            board_size: Size of the board

        Returns:
            True if number exists in column, False otherwise
        """
        return num in [board[row][col] for row in range(board_size)]

    def _number_in_box(
        self,
        board: list[list[int]],
        row: int,
        col: int,
        num: int,
        box_width: int,
        box_height: int,
    ) -> bool:
        """Check if number exists in the box containing the position.

        Args:
            board: The board to check
            row: Row index
            col: Column index
            num: Number to find
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if number exists in box, False otherwise
        """
        box_start_row = (row // box_height) * box_height
        box_start_col = (col // box_width) * box_width

        for r in range(box_start_row, box_start_row + box_height):
            for c in range(box_start_col, box_start_col + box_width):
                if board[r][c] == num:
                    return True

        return False

    def _is_row_valid(
        self, board: list[list[int]], row: int, board_size: int
    ) -> bool:
        """Check if a row contains only unique non-zero values.

        Args:
            board: The board to check
            row: Row index
            board_size: Size of the board

        Returns:
            True if row is valid, False otherwise
        """
        values = [board[row][col] for col in range(board_size) if board[row][col] != 0]
        return len(values) == len(set(values))

    def _is_column_valid(
        self, board: list[list[int]], col: int, board_size: int
    ) -> bool:
        """Check if a column contains only unique non-zero values.

        Args:
            board: The board to check
            col: Column index
            board_size: Size of the board

        Returns:
            True if column is valid, False otherwise
        """
        values = [board[row][col] for row in range(board_size) if board[row][col] != 0]
        return len(values) == len(set(values))

    def _is_box_valid(
        self,
        board: list[list[int]],
        box_row: int,
        box_col: int,
        box_width: int,
        box_height: int,
    ) -> bool:
        """Check if a box contains only unique non-zero values.

        Args:
            board: The board to check
            box_row: Box row index (0-based)
            box_col: Box column index (0-based)
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if box is valid, False otherwise
        """
        start_row = box_row * box_height
        start_col = box_col * box_width

        values = []
        for r in range(start_row, start_row + box_height):
            for c in range(start_col, start_col + box_width):
                if board[r][c] != 0:
                    values.append(board[r][c])

        return len(values) == len(set(values))


def create_sudoku_validator() -> SudokuValidator:
    """Factory function to create a SudokuValidator instance.

    Returns:
        A new SudokuValidator instance
    """
    return SudokuValidator()
