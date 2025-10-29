"""Cell value object with validation for Sudoku game.

This module provides a validated value object for cell values in the game.
Values are validated against the board size to ensure they are within range.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CellValue:
    """Immutable value object representing a cell value.

    A cell can either be empty (None) or contain a valid integer value
    based on the board size (1 to max_value).

    Attributes:
        value: The cell value or None if empty.
        max_value: Maximum allowed value (typically board size).
    """

    value: int | None
    max_value: int

    def __post_init__(self) -> None:
        """Validate cell value after initialization.

        Raises:
            ValueError: If value is out of valid range or max_value is invalid.
        """
        if self.max_value <= 0:
            msg = f"max_value must be positive, got {self.max_value}"
            raise ValueError(msg)

        if self.value is not None:
            if not isinstance(self.value, int):
                msg = f"Value must be an integer, got {type(self.value)}"
                raise ValueError(msg)

            if self.value < 1 or self.value > self.max_value:
                msg = f"Value must be between 1 and {self.max_value}, got {self.value}"
                raise ValueError(
                    msg
                )

    def is_empty(self) -> bool:
        """Check if the cell is empty.

        Returns:
            True if the cell has no value, False otherwise.
        """
        return self.value is None

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            String representation of the cell value.
        """
        return str(self.value) if self.value is not None else "."

    def __int__(self) -> int:
        """Convert to integer value.

        Returns:
            Integer value of the cell.

        Raises:
            ValueError: If the cell is empty.
        """
        if self.value is None:
            msg = "Cannot convert empty cell to integer"
            raise ValueError(msg)
        return self.value
