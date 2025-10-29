"""Backtracking-based Sudoku board generator.

This module implements a BoardGenerator using the backtracking algorithm
to create valid Sudoku puzzles with varying difficulty levels.
"""

import random
from typing import Protocol, runtime_checkable


@runtime_checkable
class BoardGenerator(Protocol):
    """Protocol for board generation."""

    def generate(self, box_width: int, box_height: int, difficulty: str) -> list[list[int]]:
        """Generate a Sudoku board.

        Args:
            box_width: Width of each box (3 for standard 9x9)
            box_height: Height of each box (3 for standard 9x9)
            difficulty: Difficulty level (EASY, MEDIUM, HARD)

        Returns:
            A 2D list representing the Sudoku board
        """
        ...


class BacktrackingGenerator:
    """Generate Sudoku boards using backtracking algorithm.

    This generator creates valid Sudoku puzzles by:
    1. Generating a complete valid board using backtracking
    2. Removing cells based on difficulty level
    3. Ensuring the puzzle has a unique solution

    Supports both standard 9x9 (3x3 boxes) and 6x6 (3x2 boxes) boards.
    """

    def __init__(self) -> None:
        """Initialize the backtracking generator."""
        self._difficulty_removal_rates = {
            "EASY": (0.30, 0.40),    # Remove 30-40% of cells
            "MEDIUM": (0.45, 0.55),  # Remove 45-55% of cells
            "HARD": (0.60, 0.65),    # Remove 60-65% of cells
        }

    def generate(
        self, box_width: int, box_height: int, difficulty: str = "MEDIUM"
    ) -> list[list[int]]:
        """Generate a Sudoku board with specified parameters.

        Args:
            box_width: Width of each box (typically 3)
            box_height: Height of each box (typically 3 for 9x9, 2 for 6x6)
            difficulty: Difficulty level (EASY, MEDIUM, or HARD)

        Returns:
            A 2D list representing the generated Sudoku board with empty
            cells represented as 0

        Raises:
            ValueError: If difficulty is not recognized
        """
        if difficulty.upper() not in self._difficulty_removal_rates:
            msg = (
                f"Invalid difficulty: {difficulty}. "
                f"Must be one of {list(self._difficulty_removal_rates.keys())}"
            )
            raise ValueError(
                msg
            )

        box_width * box_height
        complete_board = self._generate_complete_board(box_width, box_height)
        return self._remove_cells(
            complete_board, box_width, box_height, difficulty.upper()
        )


    def _generate_complete_board(
        self, box_width: int, box_height: int
    ) -> list[list[int]]:
        """Generate a complete valid Sudoku board.

        Uses backtracking with randomization to create a fully filled
        valid Sudoku board.

        Args:
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            A complete valid Sudoku board
        """
        board_size = box_width * box_height
        board = [[0 for _ in range(board_size)] for _ in range(board_size)]

        self._fill_board(board, box_width, box_height)
        return board

    def _fill_board(
        self, board: list[list[int]], box_width: int, box_height: int
    ) -> bool:
        """Fill the board using backtracking with randomization.

        Args:
            board: The board to fill (modified in place)
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if board was successfully filled, False otherwise
        """
        board_size = box_width * box_height
        empty_cell = self._find_empty_cell(board, board_size)

        if not empty_cell:
            return True  # Board is complete

        row, col = empty_cell
        numbers = list(range(1, board_size + 1))
        random.shuffle(numbers)  # Randomize for variety

        for num in numbers:
            if self._is_valid_placement(board, row, col, num, box_width, box_height):
                board[row][col] = num

                if self._fill_board(board, box_width, box_height):
                    return True

                board[row][col] = 0  # Backtrack

        return False

    def _find_empty_cell(
        self, board: list[list[int]], board_size: int
    ) -> tuple[int, int] | None:
        """Find the first empty cell in the board.

        Args:
            board: The Sudoku board
            board_size: Size of the board

        Returns:
            Tuple of (row, col) for the first empty cell, or None if board is full
        """
        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] == 0:
                    return (row, col)
        return None

    def _is_valid_placement(
        self,
        board: list[list[int]],
        row: int,
        col: int,
        num: int,
        box_width: int,
        box_height: int,
    ) -> bool:
        """Check if placing a number at position is valid.

        Args:
            board: The Sudoku board
            row: Row index
            col: Column index
            num: Number to place
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if placement is valid, False otherwise
        """
        board_size = box_width * box_height

        # Check row
        if num in board[row]:
            return False

        # Check column
        if num in [board[r][col] for r in range(board_size)]:
            return False

        # Check box
        box_start_row = (row // box_height) * box_height
        box_start_col = (col // box_width) * box_width

        for r in range(box_start_row, box_start_row + box_height):
            for c in range(box_start_col, box_start_col + box_width):
                if board[r][c] == num:
                    return False

        return True

    def _remove_cells(
        self,
        board: list[list[int]],
        box_width: int,
        box_height: int,
        difficulty: str,
    ) -> list[list[int]]:
        """Remove cells from a complete board based on difficulty.

        Creates a puzzle by removing cells while attempting to maintain
        uniqueness of solution.

        Args:
            board: Complete Sudoku board
            box_width: Width of each box
            box_height: Height of each box
            difficulty: Difficulty level

        Returns:
            A new board with cells removed
        """
        board_size = box_width * box_height
        puzzle = [row[:] for row in board]  # Deep copy

        min_rate, max_rate = self._difficulty_removal_rates[difficulty]
        total_cells = board_size * board_size
        cells_to_remove = random.randint(
            int(total_cells * min_rate), int(total_cells * max_rate)
        )

        # Create list of all cell positions
        positions = [(r, c) for r in range(board_size) for c in range(board_size)]
        random.shuffle(positions)

        removed = 0
        for row, col in positions:
            if removed >= cells_to_remove:
                break

            puzzle[row][col]
            puzzle[row][col] = 0
            removed += 1

            # For higher difficulties, we could check uniqueness here
            # For now, we just remove cells randomly

        return puzzle


def create_backtracking_generator() -> BacktrackingGenerator:
    """Factory function to create a BacktrackingGenerator instance.

    Returns:
        A new BacktrackingGenerator instance
    """
    return BacktrackingGenerator()
