"""Board renderer protocol for Sudoku boards.

This module defines the board rendering interface following
the Strategy Pattern and Interface Segregation Principle.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from rich.table import Table

if TYPE_CHECKING:
    from sudoku.domain.entities.board import Board
    from sudoku.domain.value_objects.position import Position


class BoardRenderer(Protocol):
    """Protocol for board rendering strategies.

    Different renderers can provide different visual styles:
    - Standard: Full borders with box separators
    - Compact: Minimal borders, simple grid
    - ASCII: Pure text without special characters
    """

    def render_board(
        self,
        board: Board,
        cursor_position: Position | None,
        error_positions: set[Position],
        cursor_opacity: int
    ) -> Table:
        """Render board as a Rich Table.

        Args:
            board: The board to render.
            cursor_position: Current cursor position (if any).
            error_positions: Set of positions with errors.
            cursor_opacity: Cursor opacity percentage (0-100).

        Returns:
            Rich Table with rendered board.
        """
        ...
