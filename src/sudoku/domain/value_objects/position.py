"""Position value object representing coordinates on the Sudoku board.

This module provides an immutable value object for representing cell positions
on the game board.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """Immutable value object representing a position on the board.

    Attributes:
        row: Zero-based row index.
        col: Zero-based column index.
    """

    row: int
    col: int

    def __post_init__(self) -> None:
        """Validate position values after initialization.

        Raises:
            ValueError: If row or column is negative.
        """
        if self.row < 0:
            msg = f"Row must be non-negative, got {self.row}"
            raise ValueError(msg)
        if self.col < 0:
            msg = f"Column must be non-negative, got {self.col}"
            raise ValueError(msg)

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            String representation in format (row, col).
        """
        return f"({self.row}, {self.col})"
