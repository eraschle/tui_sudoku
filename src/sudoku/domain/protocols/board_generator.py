"""Protocol for Sudoku board generation.

This module defines the protocol that board generators must implement
to create valid Sudoku puzzles.
"""

from typing import Protocol

from sudoku.domain.entities.board import Board
from sudoku.domain.value_objects.board_size import BoardSize
from sudoku.domain.value_objects.difficulty import Difficulty


class BoardGenerator(Protocol):
    """Protocol for generating Sudoku boards.

    Implementations should generate valid, solvable Sudoku puzzles
    with appropriate difficulty levels.
    """

    def generate(self, size: BoardSize, difficulty: Difficulty) -> Board:
        """Generate a new Sudoku board.

        Args:
            size: The desired board size configuration.
            difficulty: The difficulty level for the puzzle.

        Returns:
            A new Board instance with a valid puzzle.

        Raises:
            ValueError: If unable to generate a valid board.
        """
        ...
