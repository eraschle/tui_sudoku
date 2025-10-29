"""Unit tests for the Cell entity.

This module tests the Cell entity's behavior including value setting,
clearing, and validation of fixed cells.
"""

import pytest

from sudoku.domain.entities.cell import Cell
from sudoku.domain.value_objects.cell_value import CellValue


class TestCellCreation:
    """Test cell creation and initialization."""

    def test_create_empty_cell(self) -> None:
        """Test creating an empty cell."""
        value = CellValue(None, max_value=9)
        cell = Cell(value=value, is_fixed=False)

        assert cell.is_empty()
        assert not cell.is_fixed
        assert cell.get_numeric_value() is None

    def test_create_filled_cell(self) -> None:
        """Test creating a cell with a value."""
        value = CellValue(5, max_value=9)
        cell = Cell(value=value, is_fixed=False)

        assert not cell.is_empty()
        assert cell.get_numeric_value() == 5

    def test_create_fixed_cell(self) -> None:
        """Test creating a fixed cell."""
        value = CellValue(7, max_value=9)
        cell = Cell(value=value, is_fixed=True)

        assert cell.is_fixed
        assert cell.get_numeric_value() == 7


class TestCellSetValue:
    """Test setting cell values."""

    def test_set_value_on_mutable_cell(self) -> None:
        """Test setting value on a non-fixed cell succeeds."""
        cell = Cell(value=CellValue(None, max_value=9), is_fixed=False)
        new_value = CellValue(3, max_value=9)

        cell.set_value(new_value)

        assert cell.get_numeric_value() == 3
        assert not cell.is_empty()

    def test_set_value_replaces_existing_value(self) -> None:
        """Test that setting a value replaces the existing value."""
        cell = Cell(value=CellValue(5, max_value=9), is_fixed=False)
        new_value = CellValue(8, max_value=9)

        cell.set_value(new_value)

        assert cell.get_numeric_value() == 8

    def test_set_value_on_fixed_cell_raises_error(self) -> None:
        """Test that setting value on fixed cell raises ValueError."""
        cell = Cell(value=CellValue(5, max_value=9), is_fixed=True)
        new_value = CellValue(3, max_value=9)

        with pytest.raises(ValueError, match="Cannot modify a fixed cell"):
            cell.set_value(new_value)

    def test_set_value_with_different_max_value_raises_error(self) -> None:
        """Test that changing max_value raises ValueError."""
        cell = Cell(value=CellValue(5, max_value=9), is_fixed=False)
        new_value = CellValue(3, max_value=6)

        with pytest.raises(ValueError, match="Cannot change max_value"):
            cell.set_value(new_value)

    def test_set_empty_value(self) -> None:
        """Test setting an empty value (None)."""
        cell = Cell(value=CellValue(5, max_value=9), is_fixed=False)
        new_value = CellValue(None, max_value=9)

        cell.set_value(new_value)

        assert cell.is_empty()
        assert cell.get_numeric_value() is None


class TestCellClear:
    """Test clearing cell values."""

    def test_clear_mutable_cell(self) -> None:
        """Test clearing a non-fixed cell succeeds."""
        cell = Cell(value=CellValue(5, max_value=9), is_fixed=False)

        cell.clear()

        assert cell.is_empty()
        assert cell.get_numeric_value() is None

    def test_clear_already_empty_cell(self) -> None:
        """Test clearing an already empty cell is idempotent."""
        cell = Cell(value=CellValue(None, max_value=9), is_fixed=False)

        cell.clear()

        assert cell.is_empty()

    def test_clear_fixed_cell_raises_error(self) -> None:
        """Test that clearing a fixed cell raises ValueError."""
        cell = Cell(value=CellValue(5, max_value=9), is_fixed=True)

        with pytest.raises(ValueError, match="Cannot clear a fixed cell"):
            cell.clear()


class TestCellQueries:
    """Test cell query methods."""

    def test_is_empty_returns_true_for_empty_cell(self) -> None:
        """Test is_empty returns True for empty cells."""
        cell = Cell(value=CellValue(None, max_value=9), is_fixed=False)

        assert cell.is_empty()

    def test_is_empty_returns_false_for_filled_cell(self) -> None:
        """Test is_empty returns False for filled cells."""
        cell = Cell(value=CellValue(7, max_value=9), is_fixed=False)

        assert not cell.is_empty()

    def test_get_numeric_value_returns_value(self) -> None:
        """Test get_numeric_value returns the correct value."""
        cell = Cell(value=CellValue(4, max_value=9), is_fixed=False)

        assert cell.get_numeric_value() == 4

    def test_get_numeric_value_returns_none_for_empty(self) -> None:
        """Test get_numeric_value returns None for empty cells."""
        cell = Cell(value=CellValue(None, max_value=9), is_fixed=False)

        assert cell.get_numeric_value() is None


class TestCellStringRepresentation:
    """Test cell string representation."""

    def test_str_empty_cell(self) -> None:
        """Test string representation of empty cell."""
        cell = Cell(value=CellValue(None, max_value=9), is_fixed=False)

        assert str(cell) == "."

    def test_str_filled_cell(self) -> None:
        """Test string representation of filled cell."""
        cell = Cell(value=CellValue(5, max_value=9), is_fixed=False)

        assert str(cell) == "5"

    def test_str_fixed_cell(self) -> None:
        """Test string representation of fixed cell shows asterisk."""
        cell = Cell(value=CellValue(5, max_value=9), is_fixed=True)

        assert str(cell) == "5*"

    def test_str_empty_fixed_cell(self) -> None:
        """Test string representation of empty fixed cell."""
        cell = Cell(value=CellValue(None, max_value=9), is_fixed=True)

        assert str(cell) == ".*"


class TestCellEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_cell_with_max_value_6(self) -> None:
        """Test cell with 6x6 board (max_value=6)."""
        cell = Cell(value=CellValue(6, max_value=6), is_fixed=False)

        assert cell.get_numeric_value() == 6
        assert not cell.is_empty()

    def test_cell_with_value_1(self) -> None:
        """Test cell with minimum valid value (1)."""
        cell = Cell(value=CellValue(1, max_value=9), is_fixed=False)

        assert cell.get_numeric_value() == 1

    def test_cell_with_value_9(self) -> None:
        """Test cell with maximum valid value (9) for 9x9 board."""
        cell = Cell(value=CellValue(9, max_value=9), is_fixed=False)

        assert cell.get_numeric_value() == 9
