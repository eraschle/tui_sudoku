"""Board size value object for Sudoku game.

This module defines the size configuration for different Sudoku board layouts.
Supports standard 9x9 (3x3 boxes) and 6x6 (2x3 boxes) configurations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardSize:
    """Immutable value object representing board dimensions.

    Attributes:
        rows: Total number of rows on the board.
        cols: Total number of columns on the board.
        box_rows: Number of rows in each box/region.
        box_cols: Number of columns in each box/region.
    """

    rows: int
    cols: int
    box_rows: int
    box_cols: int

    def __post_init__(self) -> None:
        """Validate board size configuration.

        Raises:
            ValueError: If dimensions are invalid or inconsistent.
        """
        if self.rows <= 0 or self.cols <= 0:
            msg = "Rows and columns must be positive"
            raise ValueError(msg)

        if self.box_rows <= 0 or self.box_cols <= 0:
            msg = "Box dimensions must be positive"
            raise ValueError(msg)

        if self.rows % self.box_rows != 0:
            msg = f"Rows ({self.rows}) must be divisible by box_rows ({self.box_rows})"
            raise ValueError(
                msg
            )

        if self.cols % self.box_cols != 0:
            msg = f"Cols ({self.cols}) must be divisible by box_cols ({self.box_cols})"
            raise ValueError(
                msg
            )

        if self.box_rows * self.box_cols != self.rows:
            msg = (
                f"Box size ({self.box_rows}x{self.box_cols}) must equal "
                f"board size ({self.rows})"
            )
            raise ValueError(
                msg
            )

    @property
    def total_cells(self) -> int:
        """Calculate total number of cells on the board.

        Returns:
            Total number of cells (rows * cols).
        """
        return self.rows * self.cols

    @classmethod
    def standard_9x9(cls) -> "BoardSize":
        """Create standard 9x9 Sudoku board with 3x3 boxes.

        Returns:
            BoardSize instance for standard 9x9 configuration.
        """
        return cls(rows=9, cols=9, box_rows=3, box_cols=3)

    @classmethod
    def mini_6x6(cls) -> "BoardSize":
        """Create mini 6x6 Sudoku board with 2x3 boxes.

        Returns:
            BoardSize instance for mini 6x6 configuration.
        """
        return cls(rows=6, cols=6, box_rows=2, box_cols=3)

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            String representation of board size.
        """
        return f"{self.rows}x{self.cols} (boxes: {self.box_rows}x{self.box_cols})"
