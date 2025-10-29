"""Unit tests for the CellValue value object.

This module tests the CellValue value object including creation,
validation, and value constraints.
"""

import pytest

from sudoku.domain.value_objects.cell_value import CellValue


class TestCellValueCreation:
    """Test cell value creation and initialization."""

    def test_create_empty_cell_value(self) -> None:
        """Test creating an empty cell value."""
        cell_value = CellValue(value=None, max_value=9)

        assert cell_value.value is None
        assert cell_value.max_value == 9
        assert cell_value.is_empty()

    def test_create_cell_value_with_number(self) -> None:
        """Test creating a cell value with a number."""
        cell_value = CellValue(value=5, max_value=9)

        assert cell_value.value == 5
        assert not cell_value.is_empty()

    def test_cell_value_is_immutable(self) -> None:
        """Test that CellValue is immutable (frozen dataclass)."""
        cell_value = CellValue(value=5, max_value=9)

        with pytest.raises(Exception):  # FrozenInstanceError
            cell_value.value = 8  # type: ignore[misc]


class TestCellValueValidation:
    """Test cell value validation rules."""

    def test_negative_max_value_raises_error(self) -> None:
        """Test that negative max_value raises ValueError."""
        with pytest.raises(ValueError, match="max_value must be positive"):
            CellValue(value=None, max_value=-1)

    def test_zero_max_value_raises_error(self) -> None:
        """Test that zero max_value raises ValueError."""
        with pytest.raises(ValueError, match="max_value must be positive"):
            CellValue(value=None, max_value=0)

    def test_value_below_minimum_raises_error(self) -> None:
        """Test that value below 1 raises ValueError."""
        with pytest.raises(ValueError, match="must be between 1 and"):
            CellValue(value=0, max_value=9)

    def test_value_above_maximum_raises_error(self) -> None:
        """Test that value above max_value raises ValueError."""
        with pytest.raises(ValueError, match="must be between 1 and 9"):
            CellValue(value=10, max_value=9)

    def test_non_integer_value_raises_error(self) -> None:
        """Test that non-integer value raises ValueError."""
        with pytest.raises(ValueError, match="must be an integer"):
            CellValue(value="5", max_value=9)  # type: ignore


class TestCellValueBoundaries:
    """Test boundary values for cell values."""

    def test_minimum_valid_value(self) -> None:
        """Test creating cell value with minimum valid value (1)."""
        cell_value = CellValue(value=1, max_value=9)

        assert cell_value.value == 1

    def test_maximum_valid_value_9x9(self) -> None:
        """Test creating cell value with maximum valid value for 9x9."""
        cell_value = CellValue(value=9, max_value=9)

        assert cell_value.value == 9

    def test_maximum_valid_value_6x6(self) -> None:
        """Test creating cell value with maximum valid value for 6x6."""
        cell_value = CellValue(value=6, max_value=6)

        assert cell_value.value == 6


class TestCellValueIsEmpty:
    """Test is_empty method."""

    def test_is_empty_returns_true_for_none(self) -> None:
        """Test is_empty returns True when value is None."""
        cell_value = CellValue(value=None, max_value=9)

        assert cell_value.is_empty()

    def test_is_empty_returns_false_for_value(self) -> None:
        """Test is_empty returns False when value is set."""
        cell_value = CellValue(value=5, max_value=9)

        assert not cell_value.is_empty()


class TestCellValueStringRepresentation:
    """Test cell value string representation."""

    def test_str_empty_value(self) -> None:
        """Test string representation of empty value."""
        cell_value = CellValue(value=None, max_value=9)

        assert str(cell_value) == "."

    def test_str_numeric_value(self) -> None:
        """Test string representation of numeric value."""
        cell_value = CellValue(value=5, max_value=9)

        assert str(cell_value) == "5"

    def test_str_single_digit(self) -> None:
        """Test string representation for single digit."""
        cell_value = CellValue(value=1, max_value=9)

        assert str(cell_value) == "1"


class TestCellValueIntConversion:
    """Test conversion to integer."""

    def test_int_conversion_valid_value(self) -> None:
        """Test converting valid cell value to int."""
        cell_value = CellValue(value=7, max_value=9)

        assert int(cell_value) == 7

    def test_int_conversion_empty_raises_error(self) -> None:
        """Test that converting empty value to int raises ValueError."""
        cell_value = CellValue(value=None, max_value=9)

        with pytest.raises(ValueError, match="Cannot convert empty cell"):
            int(cell_value)


class TestCellValueEquality:
    """Test cell value equality comparison."""

    def test_equal_cell_values(self) -> None:
        """Test that cell values with same properties are equal."""
        cv1 = CellValue(value=5, max_value=9)
        cv2 = CellValue(value=5, max_value=9)

        assert cv1 == cv2

    def test_unequal_values(self) -> None:
        """Test that cell values with different values are not equal."""
        cv1 = CellValue(value=5, max_value=9)
        cv2 = CellValue(value=6, max_value=9)

        assert cv1 != cv2

    def test_unequal_max_values(self) -> None:
        """Test that cell values with different max_values are not equal."""
        cv1 = CellValue(value=5, max_value=9)
        cv2 = CellValue(value=5, max_value=6)

        assert cv1 != cv2

    def test_empty_cell_values_equal(self) -> None:
        """Test that empty cell values with same max_value are equal."""
        cv1 = CellValue(value=None, max_value=9)
        cv2 = CellValue(value=None, max_value=9)

        assert cv1 == cv2


class TestCellValueEdgeCases:
    """Test edge cases and special scenarios."""

    def test_cell_value_with_max_value_1(self) -> None:
        """Test cell value with max_value of 1."""
        cell_value = CellValue(value=1, max_value=1)

        assert cell_value.value == 1
        assert cell_value.max_value == 1

    def test_cell_value_different_board_sizes(self) -> None:
        """Test cell values for different board sizes."""
        cv_9x9 = CellValue(value=9, max_value=9)
        cv_6x6 = CellValue(value=6, max_value=6)

        assert cv_9x9.value == 9
        assert cv_6x6.value == 6

    @pytest.mark.parametrize(
        ("value", "max_value"),
        [
            (1, 9),
            (5, 9),
            (9, 9),
            (1, 6),
            (3, 6),
            (6, 6),
        ],
    )
    def test_valid_cell_values_parametrized(
        self, value: int, max_value: int
    ) -> None:
        """Test creating valid cell values with various parameters."""
        cell_value = CellValue(value=value, max_value=max_value)

        assert cell_value.value == value
        assert cell_value.max_value == max_value

    @pytest.mark.parametrize(
        ("value", "max_value"),
        [
            (0, 9),
            (10, 9),
            (-1, 9),
            (7, 6),
        ],
    )
    def test_invalid_cell_values_parametrized(
        self, value: int, max_value: int
    ) -> None:
        """Test that invalid cell values raise ValueError."""
        with pytest.raises(ValueError):
            CellValue(value=value, max_value=max_value)
