"""Protocol for Sudoku board solving.

This module defines the protocol that board solvers must implement
to solve Sudoku puzzles.
"""

from typing import Protocol

from sudoku.domain.entities.board import Board


class BoardSolver(Protocol):
    """Protocol for solving Sudoku boards.

    Implementations should provide algorithms to solve valid Sudoku puzzles.
    """

    def solve(self, board: Board) -> Board | None:
        """Attempt to solve the given board.

        Args:
            board: The board to solve (will not be modified).

        Returns:
            A new Board instance with the solution, or None if unsolvable.
        """
        ...

    def has_solution(self, board: Board) -> bool:
        """Check if the board has a valid solution.

        Args:
            board: The board to check.

        Returns:
            True if the board can be solved, False otherwise.
        """
        ...

    def has_unique_solution(self, board: Board) -> bool:
        """Check if the board has exactly one solution.

        Args:
            board: The board to check.

        Returns:
            True if the board has exactly one solution, False otherwise.
        """
        ...
