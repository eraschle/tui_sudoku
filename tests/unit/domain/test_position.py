"""Unit tests for the Position value object.

This module tests the Position value object including creation,
validation, and immutability.
"""

import pytest

from sudoku.domain.value_objects.position import Position


class TestPositionCreation:
    """Test position creation and initialization."""

    def test_create_position(self) -> None:
        """Test creating a valid position."""
        pos = Position(row=0, col=0)

        assert pos.row == 0
        assert pos.col == 0

    def test_create_position_with_values(self) -> None:
        """Test creating a position with specific values."""
        pos = Position(row=5, col=7)

        assert pos.row == 5
        assert pos.col == 7

    def test_position_is_immutable(self) -> None:
        """Test that Position is immutable (frozen dataclass)."""
        pos = Position(row=0, col=0)

        with pytest.raises(Exception):  # FrozenInstanceError
            pos.row = 5  # type: ignore[misc]


class TestPositionValidation:
    """Test position validation rules."""

    def test_negative_row_raises_error(self) -> None:
        """Test that negative row raises ValueError."""
        with pytest.raises(ValueError, match="Row must be non-negative"):
            Position(row=-1, col=0)

    def test_negative_col_raises_error(self) -> None:
        """Test that negative column raises ValueError."""
        with pytest.raises(ValueError, match="Column must be non-negative"):
            Position(row=0, col=-1)

    def test_both_negative_raises_error(self) -> None:
        """Test that both negative coordinates raise ValueError."""
        with pytest.raises(ValueError, match="must be non-negative"):
            Position(row=-1, col=-1)


class TestPositionEquality:
    """Test position equality comparison."""

    def test_equal_positions(self) -> None:
        """Test that positions with same coordinates are equal."""
        pos1 = Position(row=3, col=5)
        pos2 = Position(row=3, col=5)

        assert pos1 == pos2

    def test_unequal_positions_different_row(self) -> None:
        """Test that positions with different rows are not equal."""
        pos1 = Position(row=3, col=5)
        pos2 = Position(row=4, col=5)

        assert pos1 != pos2

    def test_unequal_positions_different_col(self) -> None:
        """Test that positions with different columns are not equal."""
        pos1 = Position(row=3, col=5)
        pos2 = Position(row=3, col=6)

        assert pos1 != pos2

    def test_position_hashable(self) -> None:
        """Test that Position can be used as dictionary key."""
        pos = Position(row=3, col=5)
        pos_dict = {pos: "cell_value"}

        assert pos_dict[pos] == "cell_value"


class TestPositionStringRepresentation:
    """Test position string representation."""

    def test_str_position(self) -> None:
        """Test string representation of position."""
        pos = Position(row=3, col=5)

        assert str(pos) == "(3, 5)"

    def test_str_position_zero(self) -> None:
        """Test string representation of (0, 0)."""
        pos = Position(row=0, col=0)

        assert str(pos) == "(0, 0)"


class TestPositionEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_position_zero_zero(self) -> None:
        """Test position at origin (0, 0)."""
        pos = Position(row=0, col=0)

        assert pos.row == 0
        assert pos.col == 0

    def test_position_large_values(self) -> None:
        """Test position with large coordinate values."""
        pos = Position(row=100, col=200)

        assert pos.row == 100
        assert pos.col == 200

    def test_position_in_set(self) -> None:
        """Test that positions can be used in sets."""
        positions = {
            Position(0, 0),
            Position(0, 1),
            Position(1, 0),
            Position(0, 0),  # Duplicate
        }

        assert len(positions) == 3  # No duplicate

    def test_position_sorting(self) -> None:
        """Test that positions can be sorted."""
        positions = [
            Position(2, 3),
            Position(0, 0),
            Position(1, 5),
        ]

        # Positions should be comparable for sorting (by default tuple ordering)
        sorted_positions = sorted(positions, key=lambda p: (p.row, p.col))

        assert sorted_positions[0] == Position(0, 0)
        assert sorted_positions[1] == Position(1, 5)
        assert sorted_positions[2] == Position(2, 3)


class TestPositionUsage:
    """Test practical usage scenarios."""

    @pytest.mark.parametrize(
        ("row", "col", "expected_str"),
        [
            (0, 0, "(0, 0)"),
            (3, 5, "(3, 5)"),
            (8, 8, "(8, 8)"),
        ],
    )
    def test_position_string_parametrized(
        self, row: int, col: int, expected_str: str
    ) -> None:
        """Test parametrized position string representation."""
        pos = Position(row=row, col=col)

        assert str(pos) == expected_str

    def test_position_unpacking(self) -> None:
        """Test that position can be unpacked (though not recommended)."""
        pos = Position(row=3, col=5)

        # Positions are dataclasses and support attribute access
        row, col = pos.row, pos.col

        assert row == 3
        assert col == 5
