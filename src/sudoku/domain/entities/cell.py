"""Cell entity representing a single cell on the Sudoku board.

This module provides the Cell entity which represents an individual cell
in the Sudoku puzzle with its value and mutability status.
"""

from dataclasses import dataclass

from sudoku.domain.value_objects.cell_value import CellValue


@dataclass
class Cell:
    """Entity representing a single cell on the Sudoku board.

    A cell can be fixed (given as part of the puzzle) or mutable (player can
    modify it). Fixed cells cannot be changed during gameplay.

    Attributes:
        value: The current value of the cell.
        is_fixed: Whether the cell is part of the original puzzle.
    """

    value: CellValue
    is_fixed: bool = False

    def set_value(self, new_value: CellValue) -> None:
        """Set a new value for the cell.

        Args:
            new_value: The new cell value to set.

        Raises:
            ValueError: If attempting to modify a fixed cell or if
                       max_value doesn't match.
        """
        if self.is_fixed:
            msg = "Cannot modify a fixed cell"
            raise ValueError(msg)

        if new_value.max_value != self.value.max_value:
            msg = (
                f"Cannot change max_value from {self.value.max_value} "
                f"to {new_value.max_value}"
            )
            raise ValueError(
                msg
            )

        self.value = new_value

    def clear(self) -> None:
        """Clear the cell value if it's not fixed.

        Raises:
            ValueError: If attempting to clear a fixed cell.
        """
        if self.is_fixed:
            msg = "Cannot clear a fixed cell"
            raise ValueError(msg)

        self.value = CellValue(None, self.value.max_value)

    def is_empty(self) -> bool:
        """Check if the cell is empty.

        Returns:
            True if the cell has no value, False otherwise.
        """
        return self.value.is_empty()

    def get_numeric_value(self) -> int | None:
        """Get the numeric value of the cell.

        Returns:
            The integer value or None if empty.
        """
        return self.value.value

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            String representation showing value and fixed status.
        """
        value_str = str(self.value)
        return f"{value_str}*" if self.is_fixed else value_str
