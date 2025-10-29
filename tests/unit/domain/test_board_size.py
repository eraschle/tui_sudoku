"""Unit tests for the BoardSize value object.

This module tests the BoardSize value object including creation,
validation, and factory methods.
"""

import pytest

from sudoku.domain.value_objects.board_size import BoardSize


class TestBoardSizeCreation:
    """Test board size creation and validation."""

    def test_create_valid_9x9_board_size(self) -> None:
        """Test creating a valid 9x9 board size."""
        size = BoardSize(rows=9, cols=9, box_rows=3, box_cols=3)

        assert size.rows == 9
        assert size.cols == 9
        assert size.box_rows == 3
        assert size.box_cols == 3

    def test_create_valid_6x6_board_size(self) -> None:
        """Test creating a valid 6x6 board size."""
        size = BoardSize(rows=6, cols=6, box_rows=2, box_cols=3)

        assert size.rows == 6
        assert size.cols == 6
        assert size.box_rows == 2
        assert size.box_cols == 3

    def test_board_size_is_immutable(self) -> None:
        """Test that BoardSize is immutable (frozen dataclass)."""
        size = BoardSize(rows=9, cols=9, box_rows=3, box_cols=3)

        with pytest.raises(Exception):  # FrozenInstanceError
            size.rows = 6  # type: ignore[misc]


class TestBoardSizeValidation:
    """Test board size validation rules."""

    def test_negative_rows_raises_error(self) -> None:
        """Test that negative rows raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            BoardSize(rows=-1, cols=9, box_rows=3, box_cols=3)

    def test_zero_rows_raises_error(self) -> None:
        """Test that zero rows raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            BoardSize(rows=0, cols=9, box_rows=3, box_cols=3)

    def test_negative_cols_raises_error(self) -> None:
        """Test that negative columns raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            BoardSize(rows=9, cols=-1, box_rows=3, box_cols=3)

    def test_zero_box_rows_raises_error(self) -> None:
        """Test that zero box rows raises ValueError."""
        with pytest.raises(ValueError, match="Box dimensions must be positive"):
            BoardSize(rows=9, cols=9, box_rows=0, box_cols=3)

    def test_zero_box_cols_raises_error(self) -> None:
        """Test that zero box columns raises ValueError."""
        with pytest.raises(ValueError, match="Box dimensions must be positive"):
            BoardSize(rows=9, cols=9, box_rows=3, box_cols=0)

    def test_rows_not_divisible_by_box_rows_raises_error(self) -> None:
        """Test that rows must be divisible by box_rows."""
        with pytest.raises(ValueError, match="must be divisible by box_rows"):
            BoardSize(rows=9, cols=9, box_rows=4, box_cols=3)

    def test_cols_not_divisible_by_box_cols_raises_error(self) -> None:
        """Test that columns must be divisible by box_cols."""
        with pytest.raises(ValueError, match="must be divisible by box_cols"):
            BoardSize(rows=9, cols=9, box_rows=3, box_cols=4)

    def test_box_size_not_equal_to_board_size_raises_error(self) -> None:
        """Test that box_rows * box_cols must equal rows (and cols)."""
        with pytest.raises(ValueError, match="Box size.*must equal"):
            BoardSize(rows=9, cols=9, box_rows=2, box_cols=3)


class TestBoardSizeProperties:
    """Test board size computed properties."""

    def test_total_cells_9x9(self) -> None:
        """Test total_cells property for 9x9 board."""
        size = BoardSize.standard_9x9()

        assert size.total_cells == 81

    def test_total_cells_6x6(self) -> None:
        """Test total_cells property for 6x6 board."""
        size = BoardSize.mini_6x6()

        assert size.total_cells == 36


class TestBoardSizeFactoryMethods:
    """Test factory methods for creating standard sizes."""

    def test_standard_9x9_factory(self) -> None:
        """Test standard_9x9 factory method."""
        size = BoardSize.standard_9x9()

        assert size.rows == 9
        assert size.cols == 9
        assert size.box_rows == 3
        assert size.box_cols == 3

    def test_mini_6x6_factory(self) -> None:
        """Test mini_6x6 factory method."""
        size = BoardSize.mini_6x6()

        assert size.rows == 6
        assert size.cols == 6
        assert size.box_rows == 2
        assert size.box_cols == 3


class TestBoardSizeEquality:
    """Test board size equality comparison."""

    def test_equal_board_sizes(self) -> None:
        """Test that two board sizes with same values are equal."""
        size1 = BoardSize(rows=9, cols=9, box_rows=3, box_cols=3)
        size2 = BoardSize(rows=9, cols=9, box_rows=3, box_cols=3)

        assert size1 == size2

    def test_unequal_board_sizes(self) -> None:
        """Test that board sizes with different values are not equal."""
        size1 = BoardSize.standard_9x9()
        size2 = BoardSize.mini_6x6()

        assert size1 != size2

    def test_board_size_hashable(self) -> None:
        """Test that BoardSize can be used as dictionary key."""
        size = BoardSize.standard_9x9()
        size_dict = {size: "9x9 board"}

        assert size_dict[size] == "9x9 board"


class TestBoardSizeStringRepresentation:
    """Test board size string representation."""

    def test_str_9x9_board(self) -> None:
        """Test string representation of 9x9 board."""
        size = BoardSize.standard_9x9()

        assert "9x9" in str(size)
        assert "3x3" in str(size)

    def test_str_6x6_board(self) -> None:
        """Test string representation of 6x6 board."""
        size = BoardSize.mini_6x6()

        assert "6x6" in str(size)
        assert "2x3" in str(size)


class TestBoardSizeEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimum_valid_board_4x4(self) -> None:
        """Test creating a minimal valid 4x4 board (2x2 boxes)."""
        size = BoardSize(rows=4, cols=4, box_rows=2, box_cols=2)

        assert size.rows == 4
        assert size.total_cells == 16

    def test_non_square_valid_board(self) -> None:
        """Test that non-square boards work if constraints are met."""
        # This would require rows != cols but box constraints still satisfied
        # Current implementation requires box_rows * box_cols == rows
        # So truly non-square boards aren't supported, but 6x6 with 2x3 boxes is
        size = BoardSize.mini_6x6()

        assert size.box_rows != size.box_cols  # Non-square boxes
        assert size.rows == size.cols  # But board is square
