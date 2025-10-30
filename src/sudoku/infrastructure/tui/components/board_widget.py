"""Board widget for rendering the Sudoku game board.

This module provides a Textual widget for displaying the Sudoku board
with cursor highlighting, cell formatting, and error visualization.

The widget uses the Strategy Pattern to delegate rendering logic to
specialized renderer implementations (BoardRenderer protocol).
"""

import logging

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual.widget import Widget

from sudoku.domain.entities.board import Board
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.tui.renderers import BoardRenderer, create_board_renderer

logger = logging.getLogger(__name__)


class BoardWidget(Widget):
    """Widget for rendering the Sudoku game board using Strategy Pattern.

    This widget displays the game board with:
    - Fixed cells (puzzle givens) in a distinct style
    - Editable cells in another style
    - Cursor highlighting for the selected cell
    - Error highlighting for invalid placements
    - Pluggable rendering strategies via BoardRenderer protocol

    The rendering logic is delegated to a BoardRenderer implementation,
    allowing different visual styles (standard, compact, etc.) without
    modifying the widget logic itself.

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
        padding: 2;
        align: center middle;
        content-align: center middle;
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
        renderer: BoardRenderer | None = None,
    ) -> None:
        """Initialize the board widget.

        Args:
            board: The Sudoku board to render.
            cursor_position: Initial cursor position.
            name: The name of the widget.
            id: The ID of the widget.
            cursor_opacity: Cursor background opacity (0-100).
            margin: Margin around the board in characters.
            renderer: Board renderer strategy. If None, uses standard renderer.
        """
        super().__init__(name=name, id=id)
        self._board = board
        self._cursor_position = cursor_position or Position(0, 0)
        self._errors: set[Position] = set()
        self._cursor_opacity = cursor_opacity
        self._margin = margin
        self._cell_width = 5  # Will be calculated dynamically (larger default)
        self._cell_height = 2  # Will be calculated dynamically (larger default)

        # Use provided renderer or default to standard
        # This is the Strategy Pattern in action - composition over inheritance
        self._renderer = renderer or create_board_renderer("standard")

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

        # Update renderer with calculated cell dimensions
        self._update_renderer_dimensions()

        return self._create_board_table()

    def _calculate_cell_size(self) -> None:
        """Calculate optimal cell size based on available terminal space."""
        if self._board is None:
            return

        available_width, available_height = self._get_available_dimensions()
        usable_width, usable_height = self._calculate_usable_space(available_width, available_height)
        max_cell_width = self._calculate_max_cell_width(usable_width)
        max_cell_height = self._calculate_max_cell_height(usable_height)
        self._set_optimal_cell_dimensions(max_cell_width, max_cell_height)

    def _get_available_dimensions(self) -> tuple[int, int]:
        """Get available widget dimensions with error handling.

        Returns:
            Tuple of (width, height) in characters.
        """
        try:
            width = self.size.width if self.size and self.size.width > 0 else 80
            height = self.size.height if self.size and self.size.height > 0 else 24
            return width, height
        except AttributeError:
            logger.debug("Widget size not yet available, using default dimensions")
            return 80, 24
        except Exception as e:
            logger.warning(
                "Unexpected error accessing widget size, using defaults: %s",
                e,
                exc_info=True,
            )
            return 80, 24

    def _calculate_usable_space(self, available_width: int, available_height: int) -> tuple[int, int]:
        """Calculate usable space after accounting for margins.

        Args:
            available_width: Available width in characters.
            available_height: Available height in characters.

        Returns:
            Tuple of (usable_width, usable_height).
        """
        usable_width = max(30, available_width - (2 * self._margin))
        usable_height = max(15, available_height - (2 * self._margin))
        return usable_width, usable_height

    def _calculate_max_cell_width(self, usable_width: int) -> int:
        """Calculate maximum cell width based on usable space.

        Args:
            usable_width: Usable width in characters.

        Returns:
            Maximum cell width in characters.
        """
        num_cells = self._board.size.cols
        separator_width = num_cells - 1
        available_for_cells_width = usable_width - separator_width
        return max(3, available_for_cells_width // num_cells)

    def _calculate_max_cell_height(self, usable_height: int) -> int:
        """Calculate maximum cell height based on usable space.

        Args:
            usable_height: Usable height in characters.

        Returns:
            Maximum cell height in characters.
        """
        num_cells = self._board.size.rows
        num_horiz_seps = num_cells - 1
        available_for_cells_height = usable_height - num_horiz_seps
        return max(1, available_for_cells_height // num_cells)

    def _set_optimal_cell_dimensions(self, max_cell_width: int, max_cell_height: int) -> None:
        """Set optimal cell dimensions for square appearance.

        Terminal characters are typically ~2x taller than wide, so we aim for
        width ≈ 2 * height to create visually square cells.

        Args:
            max_cell_width: Maximum available cell width.
            max_cell_height: Maximum available cell height.
        """
        # Terminal characters are typically 2:1 (height:width ratio)
        # For square cells: cell_width should be approximately 2 * cell_height
        ideal_height_for_width = max(1, max_cell_width // 2)
        ideal_width_for_height = max_cell_height * 2

        # Choose the combination that fits better
        if ideal_height_for_width <= max_cell_height:
            # Width-constrained: use maximum available width
            self._cell_width = max_cell_width
            self._cell_height = ideal_height_for_width
        elif ideal_width_for_height <= max_cell_width:
            # Height-constrained: use maximum available height
            self._cell_height = max_cell_height
            self._cell_width = ideal_width_for_height
        else:
            # Neither fits perfectly, use the smaller of both options
            if max_cell_width * max_cell_height >= ideal_width_for_height * ideal_height_for_width:
                self._cell_height = max_cell_height
                self._cell_width = ideal_width_for_height
            else:
                self._cell_width = max_cell_width
                self._cell_height = ideal_height_for_width

        self._apply_dimension_constraints()

    def _apply_dimension_constraints(self) -> None:
        """Apply minimum and maximum constraints to cell dimensions."""
        # Increased minimum dimensions for larger, more readable numbers
        self._cell_width = max(5, min(self._cell_width, 20))
        self._cell_height = max(2, min(self._cell_height, 8))

    def _update_renderer_dimensions(self) -> None:
        """Update renderer with current cell dimensions if supported."""
        # Only update if renderer supports it (StandardBoardRenderer does)
        if hasattr(self._renderer, '_cell_width'):
            self._renderer._cell_width = self._cell_width
        if hasattr(self._renderer, '_cell_height'):
            self._renderer._cell_height = self._cell_height

    def _create_board_table(self) -> Table:
        """Create board table using the current renderer strategy.

        This method delegates to the renderer, implementing the Strategy Pattern.
        Different renderers provide different visual representations without
        changing this widget's logic.

        Returns:
            Formatted table with board content.
        """
        if not self._board:
            return Table()

        return self._renderer.render_board(
            self._board,
            self._cursor_position,
            self._errors,
            self._cursor_opacity
        )

    def set_cursor_opacity(self, opacity: int) -> None:
        """Set cursor background opacity.

        Args:
            opacity: Opacity percentage (0-100).
        """
        self._cursor_opacity = max(0, min(100, opacity))
        self.refresh()

    def set_renderer(self, renderer: BoardRenderer) -> None:
        """Change the rendering strategy at runtime.

        This demonstrates the Strategy Pattern's flexibility - the rendering
        behavior can be changed dynamically without modifying the widget.

        Args:
            renderer: New renderer strategy to use.
        """
        self._renderer = renderer
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
