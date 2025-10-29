"""Board widget for rendering the Sudoku game board.

This module provides a Textual widget for displaying the Sudoku board
with cursor highlighting, cell formatting, and error visualization.
"""


from rich.console import RenderableType
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual.widget import Widget

from sudoku.domain.entities.board import Board
from sudoku.domain.entities.cell import Cell
from sudoku.domain.value_objects.position import Position


class BoardWidget(Widget):
    """Widget for rendering the Sudoku game board.

    This widget displays the game board with:
    - Fixed cells (puzzle givens) in a distinct style
    - Editable cells in another style
    - Cursor highlighting for the selected cell
    - Error highlighting for invalid placements
    - Grid lines separating 3x3 boxes

    Attributes:
        board: The Sudoku board to render.
        cursor_position: The current cursor position.
        errors: Set of positions with validation errors.
    """

    DEFAULT_CSS = """
    BoardWidget {
        border: solid $primary;
        height: auto;
        width: auto;
        padding: 1;
    }
    """

    def __init__(
        self,
        board: Board | None = None,
        cursor_position: Position | None = None,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize the board widget.

        Args:
            board: The Sudoku board to render.
            cursor_position: Initial cursor position.
            name: The name of the widget.
            id: The ID of the widget.
        """
        super().__init__(name=name, id=id)
        self._board = board
        self._cursor_position = cursor_position or Position(0, 0)
        self._errors: set[Position] = set()

    def set_board(self, board: Board) -> None:
        """Update the board to display.

        Args:
            board: The new board to render.
        """
        self._board = board
        self.refresh()

    def set_cursor_position(self, position: Position) -> None:
        """Update the cursor position.

        Args:
            position: The new cursor position.
        """
        self._cursor_position = position
        self.refresh()

    def add_error(self, position: Position) -> None:
        """Mark a position as having an error.

        Args:
            position: The position with an error.
        """
        self._errors.add(position)
        self.refresh()

    def clear_error(self, position: Position) -> None:
        """Clear an error at a position.

        Args:
            position: The position to clear the error from.
        """
        self._errors.discard(position)
        self.refresh()

    def clear_all_errors(self) -> None:
        """Clear all error markers."""
        self._errors.clear()
        self.refresh()

    def render(self) -> RenderableType:
        """Render the board widget.

        Returns:
            A Rich renderable representing the board.
        """
        if self._board is None:
            return Text("No board loaded", style="dim italic")

        return self._create_board_table()

    def _create_board_table(self) -> Table:
        """Create a Rich table representing the board.

        Returns:
            A formatted Rich Table with the board contents.
        """
        if self._board is None:
            return Table()

        table = Table.grid(padding=(0, 1))

        # Add columns for the 9x9 board
        for col in range(self._board.size.cols):
            table.add_column(justify="center", width=3)

        # Add rows with cells
        for row in range(self._board.size.rows):
            cells = []
            for col in range(self._board.size.cols):
                position = Position(row, col)
                cell = self._board.get_cell(position)
                cells.append(self._format_cell(cell, position))

            table.add_row(*cells)

            # Add separator after every 3rd row (except the last)
            if (row + 1) % 3 == 0 and row < self._board.size.rows - 1:
                separator_cells = [Text("---", style="dim") for _ in range(self._board.size.cols)]
                table.add_row(*separator_cells)

        return table

    def _format_cell(self, cell: Cell, position: Position) -> Text:
        """Format a single cell with appropriate styling.

        Args:
            cell: The cell to format.
            position: The position of the cell.

        Returns:
            Formatted Text object for the cell.
        """
        value = cell.get_numeric_value()
        value_str = str(value) if value is not None else " "

        # Add visual separator for 3x3 boxes
        if position.col % 3 == 0 and position.col > 0:
            value_str = f"| {value_str}"
        else:
            value_str = f" {value_str}"

        style = self._get_cell_style(cell, position)
        return Text(value_str, style=style)

    def _get_cell_style(self, cell: Cell, position: Position) -> Style:
        """Determine the display style for a cell.

        Args:
            cell: The cell to style.
            position: The position of the cell.

        Returns:
            Rich Style object for the cell.
        """
        # Priority: cursor > error > fixed > editable

        if position == self._cursor_position:
            # Cursor position - highlighted
            return Style(
                color="black",
                bgcolor="cyan",
                bold=True,
            )

        if position in self._errors:
            # Error position - red
            return Style(
                color="red",
                bold=True,
            )

        if cell.is_fixed:
            # Fixed cell (puzzle given) - blue and bold
            return Style(
                color="blue",
                bold=True,
            )

        if not cell.is_empty():
            # User-entered value - white
            return Style(
                color="white",
            )

        # Empty cell - dimmed
        return Style(
            color="dim",
        )

    @property
    def cursor_position(self) -> Position:
        """Get the current cursor position.

        Returns:
            The current cursor position.
        """
        return self._cursor_position

    @property
    def board(self) -> Board | None:
        """Get the current board.

        Returns:
            The current board, or None if not set.
        """
        return self._board

    @property
    def errors(self) -> set[Position]:
        """Get all error positions.

        Returns:
            Set of positions with errors.
        """
        return self._errors.copy()


class CompactBoardWidget(BoardWidget):
    """Compact variant of the board widget with minimal spacing.

    This variant is useful for smaller terminal windows or when
    displaying multiple boards side-by-side.
    """

    DEFAULT_CSS = """
    CompactBoardWidget {
        border: solid $primary;
        height: auto;
        width: auto;
        padding: 0;
    }
    """

    def _create_board_table(self) -> Table:
        """Create a compact Rich table representing the board.

        Returns:
            A formatted Rich Table with minimal padding.
        """
        if self._board is None:
            return Table()

        table = Table.grid(padding=(0, 0))

        # Add columns for the 9x9 board
        for col in range(self._board.size.cols):
            table.add_column(justify="center", width=2)

        # Add rows with cells
        for row in range(self._board.size.rows):
            cells = []
            for col in range(self._board.size.cols):
                position = Position(row, col)
                cell = self._board.get_cell(position)
                cells.append(self._format_compact_cell(cell, position))

            table.add_row(*cells)

        return table

    def _format_compact_cell(self, cell: Cell, position: Position) -> Text:
        """Format a single cell in compact mode.

        Args:
            cell: The cell to format.
            position: The position of the cell.

        Returns:
            Formatted Text object for the cell.
        """
        value = cell.get_numeric_value()
        value_str = str(value) if value is not None else "."

        # Add visual separator for 3x3 boxes
        if position.col % 3 == 0 and position.col > 0:
            value_str = f"|{value_str}"

        style = self._get_cell_style(cell, position)
        return Text(value_str, style=style)
