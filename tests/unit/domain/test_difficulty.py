"""Unit tests for the Difficulty enum.

This module tests the Difficulty enumeration including its values
and string representation.
"""

import pytest

from sudoku.domain.value_objects.difficulty import Difficulty


class TestDifficultyEnum:
    """Test Difficulty enum values."""

    def test_difficulty_has_easy(self) -> None:
        """Test that Difficulty has EASY level."""
        assert Difficulty.EASY is not None

    def test_difficulty_has_medium(self) -> None:
        """Test that Difficulty has MEDIUM level."""
        assert Difficulty.MEDIUM is not None

    def test_difficulty_has_hard(self) -> None:
        """Test that Difficulty has HARD level."""
        assert Difficulty.HARD is not None

    def test_all_difficulty_levels(self) -> None:
        """Test that there are exactly three difficulty levels."""
        levels = list(Difficulty)

        assert len(levels) == 3
        assert Difficulty.EASY in levels
        assert Difficulty.MEDIUM in levels
        assert Difficulty.HARD in levels


class TestDifficultyComparison:
    """Test difficulty comparison and equality."""

    def test_difficulty_equality(self) -> None:
        """Test that difficulty levels are equal to themselves."""
        assert Difficulty.EASY == Difficulty.EASY
        assert Difficulty.MEDIUM == Difficulty.MEDIUM
        assert Difficulty.HARD == Difficulty.HARD

    def test_difficulty_inequality(self) -> None:
        """Test that different difficulty levels are not equal."""
        assert Difficulty.EASY != Difficulty.MEDIUM
        assert Difficulty.MEDIUM != Difficulty.HARD
        assert Difficulty.EASY != Difficulty.HARD

    def test_difficulty_hashable(self) -> None:
        """Test that Difficulty can be used as dictionary key."""
        difficulty_dict = {
            Difficulty.EASY: "beginner",
            Difficulty.MEDIUM: "intermediate",
            Difficulty.HARD: "expert",
        }

        assert difficulty_dict[Difficulty.EASY] == "beginner"
        assert difficulty_dict[Difficulty.MEDIUM] == "intermediate"
        assert difficulty_dict[Difficulty.HARD] == "expert"


class TestDifficultyStringRepresentation:
    """Test difficulty string representation."""

    def test_str_easy(self) -> None:
        """Test string representation of EASY difficulty."""
        assert str(Difficulty.EASY) == "Easy"

    def test_str_medium(self) -> None:
        """Test string representation of MEDIUM difficulty."""
        assert str(Difficulty.MEDIUM) == "Medium"

    def test_str_hard(self) -> None:
        """Test string representation of HARD difficulty."""
        assert str(Difficulty.HARD) == "Hard"

    def test_name_attribute(self) -> None:
        """Test that difficulty levels have correct name attribute."""
        assert Difficulty.EASY.name == "EASY"
        assert Difficulty.MEDIUM.name == "MEDIUM"
        assert Difficulty.HARD.name == "HARD"


class TestDifficultyUsage:
    """Test practical usage of Difficulty enum."""

    def test_difficulty_in_set(self) -> None:
        """Test that difficulties can be used in sets."""
        difficulties = {Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD}

        assert len(difficulties) == 3
        assert Difficulty.EASY in difficulties

    def test_difficulty_in_list(self) -> None:
        """Test that difficulties can be iterated."""
        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

        assert difficulties[0] == Difficulty.EASY
        assert difficulties[1] == Difficulty.MEDIUM
        assert difficulties[2] == Difficulty.HARD

    @pytest.mark.parametrize(
        ("difficulty", "expected_str"),
        [
            (Difficulty.EASY, "Easy"),
            (Difficulty.MEDIUM, "Medium"),
            (Difficulty.HARD, "Hard"),
        ],
    )
    def test_difficulty_string_conversion(
        self, difficulty: Difficulty, expected_str: str
    ) -> None:
        """Test parametrized string conversion for all difficulties."""
        assert str(difficulty) == expected_str
