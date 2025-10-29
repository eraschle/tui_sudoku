"""Board entity representing the Sudoku game board.

This module provides the Board entity which manages the grid of cells
and provides methods for querying and modifying the board state.
"""


from sudoku.domain.value_objects.board_size import BoardSize
from sudoku.domain.value_objects.cell_value import CellValue
from sudoku.domain.value_objects.position import Position

from .cell import Cell


class Board:
    """Entity representing the Sudoku game board.

    The board maintains a 2D grid of cells and provides methods for
    accessing and modifying cells, as well as querying board state.

    Attributes:
        size: The board size configuration.
    """

    def __init__(self, size: BoardSize) -> None:
        """Initialize a new board with the given size.

        Args:
            size: The board size configuration.
        """
        self.size = size
        self._cells: list[list[Cell]] = [
            [
                Cell(CellValue(None, size.rows), is_fixed=False)
                for _ in range(size.cols)
            ]
            for _ in range(size.rows)
        ]

    def get_cell(self, position: Position) -> Cell:
        """Get the cell at the specified position.

        Args:
            position: The position of the cell to retrieve.

        Returns:
            The cell at the specified position.

        Raises:
            IndexError: If position is out of bounds.
        """
        self._validate_position(position)
        return self._cells[position.row][position.col]

    def set_cell_value(
        self, position: Position, value: int | None, is_fixed: bool = False
    ) -> None:
        """Set the value of a cell at the specified position.

        Args:
            position: The position of the cell to modify.
            value: The value to set (None for empty).
            is_fixed: Whether to mark the cell as fixed.

        Raises:
            IndexError: If position is out of bounds.
            ValueError: If attempting to modify a fixed cell or value is invalid.
        """
        self._validate_position(position)
        cell = self._cells[position.row][position.col]

        cell_value = CellValue(value, self.size.rows)

        if is_fixed:
            self._cells[position.row][position.col] = Cell(cell_value, is_fixed=True)
        else:
            cell.set_value(cell_value)

    def clear_cell(self, position: Position) -> None:
        """Clear the value of a cell at the specified position.

        Args:
            position: The position of the cell to clear.

        Raises:
            IndexError: If position is out of bounds.
            ValueError: If attempting to clear a fixed cell.
        """
        self._validate_position(position)
        cell = self._cells[position.row][position.col]
        cell.clear()

    def get_row(self, row_index: int) -> list[Cell]:
        """Get all cells in a specific row.

        Args:
            row_index: The row index.

        Returns:
            List of cells in the specified row.

        Raises:
            IndexError: If row index is out of bounds.
        """
        if not 0 <= row_index < self.size.rows:
            msg = f"Row index {row_index} out of bounds"
            raise IndexError(msg)
        return self._cells[row_index].copy()

    def get_column(self, col_index: int) -> list[Cell]:
        """Get all cells in a specific column.

        Args:
            col_index: The column index.

        Returns:
            List of cells in the specified column.

        Raises:
            IndexError: If column index is out of bounds.
        """
        if not 0 <= col_index < self.size.cols:
            msg = f"Column index {col_index} out of bounds"
            raise IndexError(msg)
        return [self._cells[row][col_index] for row in range(self.size.rows)]

    def get_box(self, position: Position) -> list[Cell]:
        """Get all cells in the box containing the specified position.

        Args:
            position: A position within the desired box.

        Returns:
            List of cells in the box.

        Raises:
            IndexError: If position is out of bounds.
        """
        self._validate_position(position)

        box_start_row = (position.row // self.size.box_rows) * self.size.box_rows
        box_start_col = (position.col // self.size.box_cols) * self.size.box_cols

        cells = []
        for row in range(box_start_row, box_start_row + self.size.box_rows):
            for col in range(box_start_col, box_start_col + self.size.box_cols):
                cells.append(self._cells[row][col])

        return cells

    def is_complete(self) -> bool:
        """Check if all cells on the board are filled.

        Returns:
            True if no cells are empty, False otherwise.
        """
        for row in self._cells:
            for cell in row:
                if cell.is_empty():
                    return False
        return True

    def count_filled_cells(self) -> int:
        """Count the number of filled cells on the board.

        Returns:
            Number of non-empty cells.
        """
        count = 0
        for row in self._cells:
            for cell in row:
                if not cell.is_empty():
                    count += 1
        return count

    def count_fixed_cells(self) -> int:
        """Count the number of fixed cells on the board.

        Returns:
            Number of fixed cells.
        """
        count = 0
        for row in self._cells:
            for cell in row:
                if cell.is_fixed:
                    count += 1
        return count

    def get_all_positions(self) -> list[Position]:
        """Get all valid positions on the board.

        Returns:
            List of all positions on the board.
        """
        positions = []
        for row in range(self.size.rows):
            for col in range(self.size.cols):
                positions.append(Position(row, col))
        return positions

    def get_empty_positions(self) -> list[Position]:
        """Get all positions of empty cells.

        Returns:
            List of positions where cells are empty.
        """
        empty_positions = []
        for row in range(self.size.rows):
            for col in range(self.size.cols):
                if self._cells[row][col].is_empty():
                    empty_positions.append(Position(row, col))
        return empty_positions

    def clone(self) -> "Board":
        """Create a deep copy of the board.

        Returns:
            A new Board instance with copied cells.
        """
        new_board = Board(self.size)
        for row in range(self.size.rows):
            for col in range(self.size.cols):
                cell = self._cells[row][col]
                new_board._cells[row][col] = Cell(cell.value, cell.is_fixed)
        return new_board

    def _validate_position(self, position: Position) -> None:
        """Validate that a position is within board bounds.

        Args:
            position: The position to validate.

        Raises:
            IndexError: If position is out of bounds.
        """
        if not (0 <= position.row < self.size.rows):
            msg = f"Row {position.row} out of bounds (0-{self.size.rows - 1})"
            raise IndexError(
                msg
            )
        if not (0 <= position.col < self.size.cols):
            msg = f"Column {position.col} out of bounds (0-{self.size.cols - 1})"
            raise IndexError(
                msg
            )

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            String representation of the board.
        """
        lines = []
        for row_idx, row in enumerate(self._cells):
            line = " ".join(str(cell) for cell in row)
            lines.append(line)

            if (
                (row_idx + 1) % self.size.box_rows == 0
                and row_idx < self.size.rows - 1
            ):
                lines.append("-" * len(line))

        return "\n".join(lines)
