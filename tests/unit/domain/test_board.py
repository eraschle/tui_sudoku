"""Unit tests for the Board entity.

This module tests the Board entity's behavior including cell management,
position queries, and board operations.
"""

import pytest

from sudoku.domain.entities.board import Board
from sudoku.domain.value_objects.board_size import BoardSize
from sudoku.domain.value_objects.position import Position


class TestBoardCreation:
    """Test board creation and initialization."""

    def test_create_empty_9x9_board(self, board_size_9x9: BoardSize) -> None:
        """Test creating an empty 9x9 board."""
        board = Board(board_size_9x9)

        assert board.size == board_size_9x9
        assert board.count_filled_cells() == 0
        assert board.count_fixed_cells() == 0

    def test_create_empty_6x6_board(self, board_size_6x6: BoardSize) -> None:
        """Test creating an empty 6x6 board."""
        board = Board(board_size_6x6)

        assert board.size == board_size_6x6
        assert board.count_filled_cells() == 0
        assert not board.is_complete()

    def test_all_cells_are_empty_initially(self, empty_board_9x9: Board) -> None:
        """Test that all cells are empty when board is created."""
        for row in range(empty_board_9x9.size.rows):
            for col in range(empty_board_9x9.size.cols):
                cell = empty_board_9x9.get_cell(Position(row, col))
                assert cell.is_empty()


class TestBoardGetCell:
    """Test getting cells from the board."""

    def test_get_cell_valid_position(self, empty_board_9x9: Board) -> None:
        """Test getting a cell at a valid position."""
        position = Position(0, 0)
        cell = empty_board_9x9.get_cell(position)

        assert cell is not None
        assert cell.is_empty()

    def test_get_cell_out_of_bounds_row(self, empty_board_9x9: Board) -> None:
        """Test getting cell with out-of-bounds row raises IndexError."""
        position = Position(10, 0)

        with pytest.raises(IndexError, match="Row.*out of bounds"):
            empty_board_9x9.get_cell(position)

    def test_get_cell_out_of_bounds_col(self, empty_board_9x9: Board) -> None:
        """Test getting cell with out-of-bounds column raises IndexError."""
        position = Position(0, 10)

        with pytest.raises(IndexError, match="Column.*out of bounds"):
            empty_board_9x9.get_cell(position)

    def test_get_cell_negative_position(self, empty_board_9x9: Board) -> None:
        """Test that negative position raises error during Position creation."""
        with pytest.raises(ValueError, match="must be non-negative"):
            Position(-1, 0)


class TestBoardSetCellValue:
    """Test setting cell values on the board."""

    def test_set_cell_value_valid(self, empty_board_9x9: Board) -> None:
        """Test setting a valid value at a position."""
        position = Position(0, 0)

        empty_board_9x9.set_cell_value(position, 5)

        cell = empty_board_9x9.get_cell(position)
        assert cell.get_numeric_value() == 5
        assert not cell.is_fixed

    def test_set_cell_value_as_fixed(self, empty_board_9x9: Board) -> None:
        """Test setting a value as fixed."""
        position = Position(0, 0)

        empty_board_9x9.set_cell_value(position, 5, is_fixed=True)

        cell = empty_board_9x9.get_cell(position)
        assert cell.is_fixed
        assert cell.get_numeric_value() == 5

    def test_set_cell_value_updates_count(self, empty_board_9x9: Board) -> None:
        """Test that setting values updates filled cell count."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(1, 1), 3)

        assert empty_board_9x9.count_filled_cells() == 2

    def test_set_cell_value_replaces_existing(self, empty_board_9x9: Board) -> None:
        """Test that setting a value replaces existing value."""
        position = Position(0, 0)
        empty_board_9x9.set_cell_value(position, 5)

        empty_board_9x9.set_cell_value(position, 8)

        cell = empty_board_9x9.get_cell(position)
        assert cell.get_numeric_value() == 8

    def test_cannot_modify_fixed_cell(self, empty_board_9x9: Board) -> None:
        """Test that modifying a fixed cell raises ValueError."""
        position = Position(0, 0)
        empty_board_9x9.set_cell_value(position, 5, is_fixed=True)

        with pytest.raises(ValueError, match="Cannot modify a fixed cell"):
            empty_board_9x9.set_cell_value(position, 8)

    def test_set_cell_value_out_of_bounds(self, empty_board_9x9: Board) -> None:
        """Test setting value at out-of-bounds position raises IndexError."""
        position = Position(10, 10)

        with pytest.raises(IndexError):
            empty_board_9x9.set_cell_value(position, 5)


class TestBoardClearCell:
    """Test clearing cell values."""

    def test_clear_cell_with_value(self, empty_board_9x9: Board) -> None:
        """Test clearing a cell that has a value."""
        position = Position(0, 0)
        empty_board_9x9.set_cell_value(position, 5)

        empty_board_9x9.clear_cell(position)

        cell = empty_board_9x9.get_cell(position)
        assert cell.is_empty()

    def test_clear_already_empty_cell(self, empty_board_9x9: Board) -> None:
        """Test clearing an already empty cell is idempotent."""
        position = Position(0, 0)

        empty_board_9x9.clear_cell(position)

        cell = empty_board_9x9.get_cell(position)
        assert cell.is_empty()

    def test_cannot_clear_fixed_cell(self, empty_board_9x9: Board) -> None:
        """Test that clearing a fixed cell raises ValueError."""
        position = Position(0, 0)
        empty_board_9x9.set_cell_value(position, 5, is_fixed=True)

        with pytest.raises(ValueError, match="Cannot clear a fixed cell"):
            empty_board_9x9.clear_cell(position)


class TestBoardGetRow:
    """Test getting rows from the board."""

    def test_get_row_valid(self, empty_board_9x9: Board) -> None:
        """Test getting a valid row."""
        row = empty_board_9x9.get_row(0)

        assert len(row) == 9
        assert all(cell.is_empty() for cell in row)

    def test_get_row_with_values(self, partially_filled_board_9x9: Board) -> None:
        """Test getting a row that has values."""
        row = partially_filled_board_9x9.get_row(0)

        values = [cell.get_numeric_value() for cell in row]
        assert values[0] == 5
        assert values[1] == 3
        assert values[2] == 4

    def test_get_row_out_of_bounds(self, empty_board_9x9: Board) -> None:
        """Test getting row with invalid index raises IndexError."""
        with pytest.raises(IndexError, match="Row index.*out of bounds"):
            empty_board_9x9.get_row(10)

    def test_get_row_returns_copy(self, empty_board_9x9: Board) -> None:
        """Test that get_row returns a copy, not the original list."""
        row1 = empty_board_9x9.get_row(0)
        row2 = empty_board_9x9.get_row(0)

        assert row1 is not row2


class TestBoardGetColumn:
    """Test getting columns from the board."""

    def test_get_column_valid(self, empty_board_9x9: Board) -> None:
        """Test getting a valid column."""
        col = empty_board_9x9.get_column(0)

        assert len(col) == 9
        assert all(cell.is_empty() for cell in col)

    def test_get_column_with_values(self, partially_filled_board_9x9: Board) -> None:
        """Test getting a column that has values."""
        col = partially_filled_board_9x9.get_column(0)

        values = [cell.get_numeric_value() for cell in col]
        assert values[0] == 5
        assert values[1] == 6

    def test_get_column_out_of_bounds(self, empty_board_9x9: Board) -> None:
        """Test getting column with invalid index raises IndexError."""
        with pytest.raises(IndexError, match="Column index.*out of bounds"):
            empty_board_9x9.get_column(10)


class TestBoardGetBox:
    """Test getting boxes from the board."""

    def test_get_box_top_left(self, empty_board_9x9: Board) -> None:
        """Test getting the top-left box."""
        box = empty_board_9x9.get_box(Position(0, 0))

        assert len(box) == 9  # 3x3 box
        assert all(cell.is_empty() for cell in box)

    def test_get_box_with_values(self, partially_filled_board_9x9: Board) -> None:
        """Test getting a box that has values."""
        box = partially_filled_board_9x9.get_box(Position(0, 0))

        values = [cell.get_numeric_value() for cell in box if not cell.is_empty()]
        assert 5 in values
        assert 3 in values
        assert 4 in values

    def test_get_box_middle(self, empty_board_9x9: Board) -> None:
        """Test getting a middle box."""
        box = empty_board_9x9.get_box(Position(4, 4))

        assert len(box) == 9

    def test_get_box_6x6_board(self, empty_board_6x6: Board) -> None:
        """Test getting a box from 6x6 board (2x3 boxes)."""
        box = empty_board_6x6.get_box(Position(0, 0))

        assert len(box) == 6  # 2x3 box


class TestBoardQueries:
    """Test board query methods."""

    def test_is_complete_empty_board(self, empty_board_9x9: Board) -> None:
        """Test that empty board is not complete."""
        assert not empty_board_9x9.is_complete()

    def test_is_complete_partially_filled(
        self, partially_filled_board_9x9: Board
    ) -> None:
        """Test that partially filled board is not complete."""
        assert not partially_filled_board_9x9.is_complete()

    def test_is_complete_fully_filled(self, board_size_9x9: BoardSize) -> None:
        """Test that fully filled board is complete."""
        board = Board(board_size_9x9)
        # Fill all cells
        for row in range(9):
            for col in range(9):
                board.set_cell_value(Position(row, col), 1)

        assert board.is_complete()

    def test_count_filled_cells(self, partially_filled_board_9x9: Board) -> None:
        """Test counting filled cells."""
        count = partially_filled_board_9x9.count_filled_cells()

        assert count == 5

    def test_count_fixed_cells(self, partially_filled_board_9x9: Board) -> None:
        """Test counting fixed cells."""
        count = partially_filled_board_9x9.count_fixed_cells()

        assert count == 5


class TestBoardPositions:
    """Test board position operations."""

    def test_get_all_positions(self, board_size_9x9: BoardSize) -> None:
        """Test getting all positions on the board."""
        board = Board(board_size_9x9)
        positions = board.get_all_positions()

        assert len(positions) == 81  # 9x9
        assert Position(0, 0) in positions
        assert Position(8, 8) in positions

    def test_get_empty_positions_empty_board(self, empty_board_9x9: Board) -> None:
        """Test getting empty positions on empty board."""
        positions = empty_board_9x9.get_empty_positions()

        assert len(positions) == 81

    def test_get_empty_positions_partially_filled(
        self, partially_filled_board_9x9: Board
    ) -> None:
        """Test getting empty positions on partially filled board."""
        positions = partially_filled_board_9x9.get_empty_positions()

        assert len(positions) == 81 - 5  # 5 cells are filled


class TestBoardClone:
    """Test board cloning."""

    def test_clone_creates_independent_copy(
        self, partially_filled_board_9x9: Board
    ) -> None:
        """Test that clone creates an independent copy."""
        cloned = partially_filled_board_9x9.clone()

        assert cloned is not partially_filled_board_9x9
        assert cloned.size == partially_filled_board_9x9.size

    def test_clone_preserves_values(self, partially_filled_board_9x9: Board) -> None:
        """Test that clone preserves cell values."""
        cloned = partially_filled_board_9x9.clone()

        original_cell = partially_filled_board_9x9.get_cell(Position(0, 0))
        cloned_cell = cloned.get_cell(Position(0, 0))

        assert original_cell.get_numeric_value() == cloned_cell.get_numeric_value()
        assert original_cell.is_fixed == cloned_cell.is_fixed

    def test_clone_modifications_dont_affect_original(
        self, partially_filled_board_9x9: Board
    ) -> None:
        """Test that modifying clone doesn't affect original."""
        cloned = partially_filled_board_9x9.clone()

        cloned.set_cell_value(Position(5, 5), 9)

        original_cell = partially_filled_board_9x9.get_cell(Position(5, 5))
        assert original_cell.is_empty()


class TestBoardStringRepresentation:
    """Test board string representation."""

    def test_str_empty_board(self, empty_board_9x9: Board) -> None:
        """Test string representation of empty board."""
        board_str = str(empty_board_9x9)

        assert "." in board_str
        assert board_str.count(".") == 81

    def test_str_board_with_values(self, partially_filled_board_9x9: Board) -> None:
        """Test string representation of board with values."""
        board_str = str(partially_filled_board_9x9)

        assert "5" in board_str
        assert "3" in board_str
        assert "*" in board_str  # Fixed cells marked with asterisk
