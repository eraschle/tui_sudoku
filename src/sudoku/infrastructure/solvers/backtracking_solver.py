"""Backtracking-based Sudoku board solver.

This module implements a BoardSolver using the backtracking algorithm
to solve Sudoku puzzles and verify solution uniqueness.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class BoardSolver(Protocol):
    """Protocol for board solving."""

    def solve(self, board: list[list[int]], box_width: int, box_height: int) -> list[list[int]] | None:
        """Solve a Sudoku board.

        Args:
            board: The Sudoku board to solve
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            Solved board or None if unsolvable
        """
        ...

    def has_unique_solution(self, board: list[list[int]], box_width: int, box_height: int) -> bool:
        """Check if board has exactly one solution.

        Args:
            board: The Sudoku board to check
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if board has unique solution, False otherwise
        """
        ...


class BacktrackingSolver:
    """Solve Sudoku boards using backtracking algorithm.

    This solver can:
    - Find a solution to any valid Sudoku puzzle
    - Verify if a puzzle has a unique solution
    - Handle both 9x9 (3x3 boxes) and 6x6 (3x2 boxes) boards

    The backtracking algorithm works by:
    1. Finding an empty cell
    2. Trying each valid number (1 to board_size)
    3. Recursively solving with that number
    4. Backtracking if no solution found
    """

    def solve(
        self, board: list[list[int]], box_width: int, box_height: int
    ) -> list[list[int]] | None:
        """Solve a Sudoku board using backtracking.

        Args:
            board: The Sudoku board to solve (0 represents empty cells)
            box_width: Width of each box (typically 3)
            box_height: Height of each box (typically 3 for 9x9, 2 for 6x6)

        Returns:
            A solved board if solution exists, None otherwise
        """
        # Validate initial board state
        if not self._is_initial_board_valid(board, box_width, box_height):
            return None

        # Create a deep copy to avoid modifying the original
        solution = [row[:] for row in board]

        if self._solve_recursive(solution, box_width, box_height):
            return solution

        return None

    def has_unique_solution(
        self, board: list[list[int]], box_width: int, box_height: int
    ) -> bool:
        """Check if the board has exactly one unique solution.

        Args:
            board: The Sudoku board to check
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if board has exactly one solution, False otherwise
        """
        solution_count = self._count_solutions(
            [row[:] for row in board], box_width, box_height, max_count=2
        )
        return solution_count == 1

    def _solve_recursive(
        self, board: list[list[int]], box_width: int, box_height: int
    ) -> bool:
        """Recursively solve the board using backtracking.

        Args:
            board: The board to solve (modified in place)
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if board was solved, False otherwise
        """
        board_size = box_width * box_height
        empty_cell = self._find_empty_cell(board, board_size)

        if not empty_cell:
            return True  # Board is complete

        row, col = empty_cell

        for num in range(1, board_size + 1):
            if self._is_valid_placement(board, row, col, num, box_width, box_height):
                board[row][col] = num

                if self._solve_recursive(board, box_width, box_height):
                    return True

                board[row][col] = 0  # Backtrack

        return False

    def _count_solutions(
        self,
        board: list[list[int]],
        box_width: int,
        box_height: int,
        max_count: int = 2,
    ) -> int:
        """Count the number of solutions for a board.

        Args:
            board: The board to check
            box_width: Width of each box
            box_height: Height of each box
            max_count: Maximum number of solutions to find before stopping

        Returns:
            Number of solutions found (up to max_count)
        """
        board_size = box_width * box_height
        empty_cell = self._find_empty_cell(board, board_size)

        if not empty_cell:
            return 1  # Found a solution

        row, col = empty_cell
        count = 0

        for num in range(1, board_size + 1):
            if self._is_valid_placement(board, row, col, num, box_width, box_height):
                board[row][col] = num

                count += self._count_solutions(board, box_width, box_height, max_count)

                board[row][col] = 0  # Backtrack

                if count >= max_count:
                    return count  # Early exit if we found enough solutions

        return count

    def _find_empty_cell(
        self, board: list[list[int]], board_size: int
    ) -> tuple[int, int] | None:
        """Find the first empty cell in the board.

        Uses a simple left-to-right, top-to-bottom scan.

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

        Validates against Sudoku rules:
        - Number must not exist in the same row
        - Number must not exist in the same column
        - Number must not exist in the same box

        Args:
            board: The Sudoku board
            row: Row index (0-based)
            col: Column index (0-based)
            num: Number to place (1 to board_size)
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if placement is valid, False otherwise
        """
        board_size = box_width * box_height

        # Check row constraint
        if num in board[row]:
            return False

        # Check column constraint
        if num in [board[r][col] for r in range(board_size)]:
            return False

        # Check box constraint
        box_start_row = (row // box_height) * box_height
        box_start_col = (col // box_width) * box_width

        for r in range(box_start_row, box_start_row + box_height):
            for c in range(box_start_col, box_start_col + box_width):
                if board[r][c] == num:
                    return False

        return True

    def _is_initial_board_valid(
        self, board: list[list[int]], box_width: int, box_height: int
    ) -> bool:
        """Check if the initial board state is valid.

        Validates that the initial board has no duplicate non-zero values
        in any row, column, or box.

        Args:
            board: The Sudoku board to validate
            box_width: Width of each box
            box_height: Height of each box

        Returns:
            True if initial board is valid, False otherwise
        """
        board_size = box_width * box_height

        # Check rows
        for row in board:
            non_zero = [num for num in row if num != 0]
            if len(non_zero) != len(set(non_zero)):
                return False  # Duplicate found in row

        # Check columns
        for col in range(board_size):
            column = [board[row][col] for row in range(board_size)]
            non_zero = [num for num in column if num != 0]
            if len(non_zero) != len(set(non_zero)):
                return False  # Duplicate found in column

        # Check boxes
        for box_row in range(0, board_size, box_height):
            for box_col in range(0, board_size, box_width):
                box_nums = []
                for r in range(box_row, box_row + box_height):
                    for c in range(box_col, box_col + box_width):
                        if board[r][c] != 0:
                            box_nums.append(board[r][c])
                if len(box_nums) != len(set(box_nums)):
                    return False  # Duplicate found in box

        return True


def create_backtracking_solver() -> BacktrackingSolver:
    """Factory function to create a BacktrackingSolver instance.

    Returns:
        A new BacktrackingSolver instance
    """
    return BacktrackingSolver()
