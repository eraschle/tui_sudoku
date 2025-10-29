"""Difficulty level value object for Sudoku game.

This module defines the difficulty levels available in the Sudoku game.
Each difficulty level determines the number of pre-filled cells in the puzzle.
"""

from enum import Enum, auto


class Difficulty(Enum):
    """Enumeration of Sudoku difficulty levels.

    The difficulty level determines how many cells are initially filled
    and how challenging the puzzle will be to solve.
    """

    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            String representation of the difficulty level.
        """
        return self.name.capitalize()
