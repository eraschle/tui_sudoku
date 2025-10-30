"""Concrete board renderer implementations.

This module provides various board rendering strategies following
the Strategy Pattern for flexible visual presentation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rich.console import RenderableType
from rich.style import Style
from rich.table import Table
from rich.text import Text

from sudoku.domain.value_objects.position import Position

if TYPE_CHECKING:
    from sudoku.domain.entities.board import Board
    from sudoku.domain.entities.cell import Cell

logger = logging.getLogger(__name__)


class StandardBoardRenderer:
    """Standard board renderer with full borders and box separators.

    This renderer creates a detailed visual representation with:
    - Heavy borders for box boundaries (┃ ━)
    - Light borders for cell boundaries (│ ─)
    - Corner and intersection characters (╋ ┼ ╂ ┿)
    - Color-coded cells (fixed, user, cursor, errors)
    """

    def __init__(self, cell_width: int = 3, cell_height: int = 1) -> None:
        """Initialize the standard renderer.

        Args:
            cell_width: Width of each cell in characters.
            cell_height: Height of each cell in rows.
        """
        self._cell_width = cell_width
        self._cell_height = cell_height

    def render_board(
        self,
        board: Board,
        cursor_position: Position | None,
        error_positions: set[Position],
        cursor_opacity: int
    ) -> Table:
        """Render board with full decorations.

        Args:
            board: The board to render.
            cursor_position: Current cursor position.
            error_positions: Positions with errors.
            cursor_opacity: Cursor opacity (0-100).

        Returns:
            Richly formatted table.
        """
        table = self._create_base_table(board)
        self._add_top_border(table, board)
        self._add_board_rows(table, board, cursor_position, error_positions, cursor_opacity)
        self._add_bottom_border(table, board)
        return table

    def _create_base_table(self, board: Board) -> Table:
        """Create table with column configuration."""
        table = Table.grid(padding=0)
        for col in range(board.size.cols):
            table.add_column(justify="center", width=self._cell_width)
            if col < board.size.cols - 1:
                # All separators are 1 character wide
                table.add_column(justify="center", width=1)
        return table

    def _add_top_border(self, table: Table, board: Board) -> None:
        """Add top border row."""
        border_elements = []
        for col in range(board.size.cols):
            border_chars = "━" * self._cell_width
            border_elements.append(Text(border_chars, style="bold bright_black"))

            if col < board.size.cols - 1:
                if (col + 1) % 3 == 0:
                    # 3x3 box boundary - heavy line
                    border_elements.append(Text("┳", style="bold bright_black"))
                else:
                    # Cell boundary - light line
                    border_elements.append(Text("┯", style="dim bright_black"))

        table.add_row(*border_elements)

    def _add_board_rows(
        self,
        table: Table,
        board: Board,
        cursor_position: Position | None,
        error_positions: set[Position],
        cursor_opacity: int
    ) -> None:
        """Add all board rows with cells."""
        for row in range(board.size.rows):
            self._add_cell_row(
                table, board, row, cursor_position, error_positions, cursor_opacity
            )
            if row < board.size.rows - 1:
                self._add_separator_row(table, board, row)

    def _add_cell_row(
        self,
        table: Table,
        board: Board,
        row: int,
        cursor_position: Position | None,
        error_positions: set[Position],
        cursor_opacity: int
    ) -> None:
        """Add single cell row."""
        # For taller cells, add multiple rows per cell
        for cell_row in range(self._cell_height):
            cells = []
            for col in range(board.size.cols):
                position = Position(row, col)
                cell = board.get_cell(position)

                # Only show number in middle row of cell
                is_middle_row = cell_row == self._cell_height // 2
                formatted_cell = self._format_cell(
                    cell, position, cursor_position, error_positions, cursor_opacity, is_middle_row
                )
                cells.append(formatted_cell)

                if col < board.size.cols - 1:
                    cells.append(self._get_vertical_separator(col, board))

            table.add_row(*cells)

    def _add_separator_row(self, table: Table, board: Board, row: int) -> None:
        """Add horizontal separator row."""
        separator_elements = []
        is_box_boundary = (row + 1) % 3 == 0

        for col in range(board.size.cols):
            if is_box_boundary:
                sep_chars = "━" * self._cell_width
                separator_elements.append(Text(sep_chars, style="bold bright_black"))
            else:
                sep_chars = "─" * self._cell_width
                separator_elements.append(Text(sep_chars, style="dim bright_black"))

            if col < board.size.cols - 1:
                separator_elements.append(self._get_intersection_char(row, col, board))

        table.add_row(*separator_elements)

    def _get_vertical_separator(self, col: int, board: Board) -> Text:
        """Get vertical separator character."""
        if (col + 1) % 3 == 0:
            return Text("┃", style="bold bright_black")  # Heavy line (thick)
        return Text("│", style="dim bright_black")  # Light line (thin)

    def _get_intersection_char(self, row: int, col: int, board: Board) -> Text:
        """Get intersection character."""
        is_box_row = (row + 1) % 3 == 0
        is_box_col = (col + 1) % 3 == 0

        if is_box_row and is_box_col:
            return Text("╋", style="bold bright_black")  # Heavy cross
        elif is_box_row:
            return Text("┿", style="bold bright_black")  # Mixed junction
        elif is_box_col:
            return Text("╂", style="bold bright_black")  # Mixed junction
        else:
            return Text("┼", style="dim bright_black")  # Light cross

    def _add_bottom_border(self, table: Table, board: Board) -> None:
        """Add bottom border row."""
        border_elements = []
        for col in range(board.size.cols):
            border_chars = "━" * self._cell_width
            border_elements.append(Text(border_chars, style="bold bright_black"))

            if col < board.size.cols - 1:
                if (col + 1) % 3 == 0:
                    # 3x3 box boundary - heavy line
                    border_elements.append(Text("┻", style="bold bright_black"))
                else:
                    # Cell boundary - light line
                    border_elements.append(Text("┷", style="dim bright_black"))

        table.add_row(*border_elements)

    def _format_cell(
        self,
        cell: Cell,
        position: Position,
        cursor_position: Position | None,
        error_positions: set[Position],
        cursor_opacity: int,
        show_value: bool = True
    ) -> RenderableType:
        """Format cell with appropriate styling."""
        # Get cell value
        if show_value:
            value = cell.get_numeric_value()
            value_str = str(value) if value is not None else " "
        else:
            value_str = " "

        # Center the value within the cell width
        padded_value = value_str.center(self._cell_width)

        # Determine style
        style = self._get_cell_style(cell, position, cursor_position, error_positions, cursor_opacity)
        return Text(padded_value, style=style)

    def _get_cell_style(
        self,
        cell: Cell,
        position: Position,
        cursor_position: Position | None,
        error_positions: set[Position],
        cursor_opacity: int
    ) -> Style:
        """Determine the display style for a cell."""
        is_cursor = cursor_position and position == cursor_position
        is_error = position in error_positions

        # Cursor + Error: Show error background with cursor text color
        if is_cursor and is_error:
            return Style(
                color="bright_white",
                bgcolor="red",
                bold=True,
                underline=True,  # Extra indicator for cursor
            )

        # Cursor only: Highlighted with opacity-based transparency
        if is_cursor:
            # Adjust color brightness based on opacity
            if cursor_opacity >= 90:
                bgcolor = "cyan"
            elif cursor_opacity >= 70:
                bgcolor = "bright_cyan"
            elif cursor_opacity >= 50:
                return Style(color="black", bgcolor="cyan", bold=True, dim=True)
            else:
                # Very transparent - just underline
                return Style(color="black", underline=True, bold=True)

            return Style(color="black", bgcolor=bgcolor, bold=True)

        # Error only: Red text
        if is_error:
            return Style(color="red", bold=True)

        # Fixed cell: Orange and bold
        if cell.is_fixed:
            return Style(color="bright_yellow", bold=True)

        # User-entered value: Orange
        if not cell.is_empty():
            return Style(color="yellow")

        # Empty cell: Dimmed
        return Style(color="bright_black", dim=True)


class CompactBoardRenderer:
    """Compact board renderer with minimal decorations.

    This renderer creates a simple, space-efficient representation:
    - No fancy border characters
    - Simple grid layout
    - Minimal spacing
    - Still supports color coding
    """

    def render_board(
        self,
        board: Board,
        cursor_position: Position | None,
        error_positions: set[Position],
        cursor_opacity: int
    ) -> Table:
        """Render board in compact format.

        Args:
            board: The board to render.
            cursor_position: Current cursor position.
            error_positions: Positions with errors.
            cursor_opacity: Cursor opacity (0-100).

        Returns:
            Compact table representation.
        """
        table = Table.grid(padding=(0, 0))

        # Simple column setup
        for _ in range(board.size.cols):
            table.add_column(justify="center", width=2)

        # Add rows without decorative borders
        for row in range(board.size.rows):
            cells = []
            for col in range(board.size.cols):
                position = Position(row, col)
                cell = board.get_cell(position)
                formatted_cell = self._format_cell(
                    cell, position, cursor_position, error_positions, cursor_opacity
                )
                cells.append(formatted_cell)
            table.add_row(*cells)

        return table

    def _format_cell(
        self,
        cell: Cell,
        position: Position,
        cursor_position: Position | None,
        error_positions: set[Position],
        cursor_opacity: int
    ) -> RenderableType:
        """Format cell with basic styling."""
        value = cell.get_numeric_value()
        value_str = str(value) if value is not None else "."

        # Add visual separator for 3x3 boxes
        if position.col % 3 == 0 and position.col > 0:
            value_str = f"|{value_str}"

        # Determine style
        style = self._get_cell_style(cell, position, cursor_position, error_positions, cursor_opacity)
        return Text(value_str, style=style)

    def _get_cell_style(
        self,
        cell: Cell,
        position: Position,
        cursor_position: Position | None,
        error_positions: set[Position],
        cursor_opacity: int
    ) -> Style:
        """Determine the display style for a cell."""
        is_cursor = cursor_position and position == cursor_position
        is_error = position in error_positions

        if is_cursor and is_error:
            return Style(color="bright_white", bgcolor="red", bold=True)

        if is_cursor:
            return Style(bgcolor="yellow", color="black", bold=True)

        if is_error:
            return Style(color="red", bold=True)

        if cell.is_fixed:
            return Style(color="cyan", bold=True)

        if not cell.is_empty():
            return Style(color="white")

        return Style(color="bright_black", dim=True)
