"""Board widget for rendering the Sudoku game board.

This module provides a Textual widget for displaying the Sudoku board
with cursor highlighting, cell formatting, and error visualization.
"""

import logging

from rich.console import RenderableType
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual.widget import Widget

from sudoku.domain.entities.board import Board
from sudoku.domain.entities.cell import Cell
from sudoku.domain.value_objects.position import Position

logger = logging.getLogger(__name__)


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
        border: none;
        height: 100%;
        width: 100%;
        padding: 0;
        align: center middle;
    }
    """

    def __init__(
        self,
        board: Board | None = None,
        cursor_position: Position | None = None,
        name: str | None = None,
        id: str | None = None,
        cursor_opacity: int = 80,
        margin: int = 2,
    ) -> None:
        """Initialize the board widget.

        Args:
            board: The Sudoku board to render.
            cursor_position: Initial cursor position.
            name: The name of the widget.
            id: The ID of the widget.
            cursor_opacity: Cursor background opacity (0-100).
            margin: Margin around the board in characters.
        """
        super().__init__(name=name, id=id)
        self._board = board
        self._cursor_position = cursor_position or Position(0, 0)
        self._errors: set[Position] = set()
        self._cursor_opacity = cursor_opacity
        self._margin = margin
        self._cell_width = 3  # Will be calculated dynamically
        self._cell_height = 1  # Will be calculated dynamically

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

        # Calculate optimal cell size based on available space
        self._calculate_cell_size()

        return self._create_board_table()

    def _calculate_cell_size(self) -> None:
        """Calculate optimal cell size based on available terminal space."""
        if self._board is None:
            return

        # Get available size from container
        try:
            available_width = self.size.width if self.size and self.size.width > 0 else 80
            available_height = self.size.height if self.size and self.size.height > 0 else 24
        except AttributeError:
            # Size attribute not yet available (widget not mounted)
            logger.debug("Widget size not yet available, using default dimensions")
            available_width = 80
            available_height = 24
        except Exception as e:
            # Unexpected error accessing size
            logger.warning(
                "Unexpected error accessing widget size, using defaults: %s",
                e,
                exc_info=True,
            )
            available_width = 80
            available_height = 24

        # Account for margins (reduced margin for better space usage)
        usable_width = max(30, available_width - (2 * self._margin))
        usable_height = max(15, available_height - (2 * self._margin))

        # Calculate grid dimensions for 9x9 board
        # We need space for: 9 cells + 8 separators (all 1 char wide)
        # Thick separators use heavy line style, thin use light line style
        num_cells = self._board.size.cols

        # For width: Calculate max cell width
        # All separators are 1 character wide now
        separator_width = num_cells - 1  # 8 separators for 9 cells
        available_for_cells_width = usable_width - separator_width
        max_cell_width = max(3, available_for_cells_width // num_cells)

        # For height: Terminal chars are ~2:1 (height:width ratio)
        # To make a visual square, we need fewer rows than columns
        # We also need space for horizontal separators
        num_horiz_seps = num_cells - 1
        available_for_cells_height = usable_height - num_horiz_seps
        max_cell_height = max(1, available_for_cells_height // num_cells)

        # For square appearance: width should be ~2x height (accounting for char aspect)
        # If we have width=6, we want height=3 to look square
        ideal_height_for_width = max(1, max_cell_width // 2)

        # Choose the limiting dimension
        if ideal_height_for_width <= max_cell_height:
            # Width is limiting
            self._cell_width = max_cell_width
            self._cell_height = ideal_height_for_width
        else:
            # Height is limiting
            self._cell_height = max_cell_height
            self._cell_width = max_cell_height * 2  # Double for square appearance

        # Ensure minimum and maximum sizes
        self._cell_width = max(3, min(self._cell_width, 20))
        self._cell_height = max(1, min(self._cell_height, 5))

    def _create_board_table(self) -> Table:
        """Create a Rich table representing the board.

        Returns:
            A formatted Rich Table with the board contents.
        """
        if self._board is None:
            return Table()

        # Create table with box drawing characters
        table = Table.grid(padding=0)

        # Add columns: cell + separator for each column (use calculated cell width)
        for col in range(self._board.size.cols):
            table.add_column(justify="center", width=self._cell_width)
            if col < self._board.size.cols - 1:
                # All separators are 1 character wide (heavy vs light line style)
                table.add_column(justify="center", width=1)

        # Top border
        border_row = self._create_border_row("top")
        table.add_row(*border_row)

        # Add rows with cells and separators
        for row in range(self._board.size.rows):
            # For taller cells, add multiple rows per cell
            for cell_row in range(self._cell_height):
                cells = []
                for col in range(self._board.size.cols):
                    position = Position(row, col)
                    cell = self._board.get_cell(position)

                    # Only show number in middle row of cell
                    is_middle_row = cell_row == self._cell_height // 2
                    cells.append(self._format_cell(cell, position, is_middle_row))

                    # Add vertical separator after each column except the last
                    if col < self._board.size.cols - 1:
                        # Heavy line for 3x3 boxes, light line for cells
                        if (col + 1) % 3 == 0:
                            cells.append(Text("┃", style="bold bright_black"))  # Heavy line (thick)
                        else:
                            cells.append(Text("│", style="dim bright_black"))  # Light line (thin)

                table.add_row(*cells)

            # Add horizontal separator after each row except the last
            if row < self._board.size.rows - 1:
                separator_row = self._create_separator_row(row)
                table.add_row(*separator_row)

        # Bottom border
        border_row = self._create_border_row("bottom")
        table.add_row(*border_row)

        return table

    def _create_border_row(self, position: str) -> list[Text]:
        """Create top or bottom border row.

        Args:
            position: Either "top" or "bottom".

        Returns:
            List of Text objects for the border row.
        """
        if self._board is None:
            return []

        cells = []
        for col in range(self._board.size.cols):
            # Dark borders for all cells - adjust to cell width
            border_chars = "━" * self._cell_width
            cells.append(Text(border_chars, style="bold bright_black"))

            # Add corner/junction after each column except the last
            if col < self._board.size.cols - 1:
                if (col + 1) % 3 == 0:
                    # 3x3 box boundary - heavy line
                    if position == "top":
                        cells.append(Text("┳", style="bold bright_black"))  # Heavy T-junction
                    else:
                        cells.append(Text("┻", style="bold bright_black"))  # Heavy T-junction
                else:
                    # Cell boundary - light line
                    if position == "top":
                        cells.append(Text("┯", style="dim bright_black"))  # Light T-junction
                    else:
                        cells.append(Text("┷", style="dim bright_black"))  # Light T-junction

        return cells

    def _create_separator_row(self, row: int) -> list[Text]:
        """Create horizontal separator row between cells.

        Args:
            row: The row number (0-indexed) after which this separator appears.

        Returns:
            List of Text objects for the separator row.
        """
        if self._board is None:
            return []

        cells = []
        # Check if this is a 3x3 box boundary
        is_box_boundary = (row + 1) % 3 == 0

        for col in range(self._board.size.cols):
            # Horizontal line - darker colors, adjusted to cell width
            if is_box_boundary:
                sep_chars = "━" * self._cell_width
                cells.append(Text(sep_chars, style="bold bright_black"))
            else:
                sep_chars = "─" * self._cell_width
                cells.append(Text(sep_chars, style="dim bright_black"))

            # Add junction after each column except the last
            if col < self._board.size.cols - 1:
                # Determine junction style based on boundaries
                is_col_boundary = (col + 1) % 3 == 0

                if is_box_boundary and is_col_boundary:
                    # Box intersection - heavy cross
                    cells.append(Text("╋", style="bold bright_black"))  # Heavy cross
                elif is_box_boundary:
                    # Box horizontal with cell vertical - heavy horizontal, light vertical
                    cells.append(Text("┿", style="bold bright_black"))  # Mixed junction
                elif is_col_boundary:
                    # Cell horizontal with box vertical - light horizontal, heavy vertical
                    cells.append(Text("╂", style="bold bright_black"))  # Mixed junction
                else:
                    # Cell intersection - light cross
                    cells.append(Text("┼", style="dim bright_black"))  # Light cross

        return cells

    def _format_cell(self, cell: Cell, position: Position, show_value: bool = True) -> Text:
        """Format a single cell with appropriate styling.

        Args:
            cell: The cell to format.
            position: The position of the cell.
            show_value: Whether to show the number (only in middle row of multi-row cells).

        Returns:
            Formatted Text object for the cell.
        """
        if show_value:
            value = cell.get_numeric_value()
            value_str = str(value) if value is not None else " "
        else:
            value_str = " "

        # Center the value within the cell width
        padded_value = value_str.center(self._cell_width)

        style = self._get_cell_style(cell, position)
        return Text(padded_value, style=style)

    def _get_cell_style(self, cell: Cell, position: Position) -> Style:
        """Determine the display style for a cell.

        Args:
            cell: The cell to style.
            position: The position of the cell.

        Returns:
            Rich Style object for the cell.
        """
        # Check both cursor and error status
        is_cursor = position == self._cursor_position
        is_error = position in self._errors

        # Cursor + Error: Show error background with cursor text color
        if is_cursor and is_error:
            # Red background to show error, bright text for cursor visibility
            # Opacity effect simulated with color="bright_white"
            return Style(
                color="bright_white",
                bgcolor="red",
                bold=True,
                underline=True,  # Extra indicator for cursor
            )

        # Cursor only: Highlighted with opacity-based transparency
        if is_cursor:
            # Adjust color brightness based on opacity
            # Higher opacity = darker/more opaque, lower = lighter/more transparent
            if self._cursor_opacity >= 90:
                bgcolor = "cyan"
            elif self._cursor_opacity >= 70:
                bgcolor = "bright_cyan"
            elif self._cursor_opacity >= 50:
                bgcolor = "cyan"
                return Style(color="black", bgcolor=bgcolor, bold=True, dim=True)
            else:
                # Very transparent - just underline
                return Style(color="black", underline=True, bold=True)

            return Style(
                color="black",
                bgcolor=bgcolor,
                bold=True,
            )

        # Error only: Red text
        if is_error:
            return Style(
                color="red",
                bold=True,
            )

        # Fixed cell: Orange and bold
        if cell.is_fixed:
            return Style(
                color="bright_yellow",  # Orange-ish
                bold=True,
            )

        # User-entered value: Orange
        if not cell.is_empty():
            return Style(
                color="yellow",  # Orange text
            )

        # Empty cell: Dimmed
        return Style(
            color="bright_black",
            dim=True,
        )

    def set_cursor_opacity(self, opacity: int) -> None:
        """Set cursor background opacity.

        Args:
            opacity: Opacity percentage (0-100).
        """
        self._cursor_opacity = max(0, min(100, opacity))
        self.refresh()

    def on_resize(self) -> None:
        """Handle widget resize events to recalculate cell sizes."""
        self.refresh()

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
