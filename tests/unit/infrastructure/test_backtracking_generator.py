"""Unit tests for the BacktrackingGenerator.

This module tests the board generation logic including puzzle creation
for different sizes and difficulty levels.
"""

import pytest

from sudoku.infrastructure.generators.backtracking_generator import (
    BacktrackingGenerator,
    create_backtracking_generator,
)


class TestBacktrackingGeneratorCreation:
    """Test generator instantiation."""

    def test_create_generator(self) -> None:
        """Test creating a backtracking generator instance."""
        generator = BacktrackingGenerator()

        assert generator is not None

    def test_create_generator_via_factory(self) -> None:
        """Test creating generator using factory function."""
        generator = create_backtracking_generator()

        assert isinstance(generator, BacktrackingGenerator)


class TestBacktrackingGenerator9x9:
    """Test generating 9x9 boards."""

    def test_generate_9x9_easy_puzzle(self) -> None:
        """Test generating a 9x9 easy puzzle."""
        generator = BacktrackingGenerator()

        board = generator.generate(box_width=3, box_height=3, difficulty="EASY")

        assert len(board) == 9
        assert all(len(row) == 9 for row in board)

    def test_generate_9x9_medium_puzzle(self) -> None:
        """Test generating a 9x9 medium puzzle."""
        generator = BacktrackingGenerator()

        board = generator.generate(box_width=3, box_height=3, difficulty="MEDIUM")

        assert len(board) == 9
        assert all(len(row) == 9 for row in board)

    def test_generate_9x9_hard_puzzle(self) -> None:
        """Test generating a 9x9 hard puzzle."""
        generator = BacktrackingGenerator()

        board = generator.generate(box_width=3, box_height=3, difficulty="HARD")

        assert len(board) == 9
        assert all(len(row) == 9 for row in board)

    def test_generated_board_has_empty_cells(self) -> None:
        """Test that generated puzzle has empty cells (zeros)."""
        generator = BacktrackingGenerator()

        board = generator.generate(box_width=3, box_height=3, difficulty="MEDIUM")

        empty_count = sum(row.count(0) for row in board)
        assert empty_count > 0

    def test_generated_board_has_filled_cells(self) -> None:
        """Test that generated puzzle has some filled cells."""
        generator = BacktrackingGenerator()

        board = generator.generate(box_width=3, box_height=3, difficulty="MEDIUM")

        filled_count = sum(1 for row in board for cell in row if cell != 0)
        assert filled_count > 0


class TestBacktrackingGenerator6x6:
    """Test generating 6x6 boards."""

    def test_generate_6x6_easy_puzzle(self) -> None:
        """Test generating a 6x6 easy puzzle."""
        generator = BacktrackingGenerator()

        board = generator.generate(box_width=3, box_height=2, difficulty="EASY")

        assert len(board) == 6
        assert all(len(row) == 6 for row in board)

    def test_generate_6x6_medium_puzzle(self) -> None:
        """Test generating a 6x6 medium puzzle."""
        generator = BacktrackingGenerator()

        board = generator.generate(box_width=3, box_height=2, difficulty="MEDIUM")

        assert len(board) == 6

    def test_generate_6x6_hard_puzzle(self) -> None:
        """Test generating a 6x6 hard puzzle."""
        generator = BacktrackingGenerator()

        board = generator.generate(box_width=3, box_height=2, difficulty="HARD")

        assert len(board) == 6


class TestBacktrackingGeneratorDifficulty:
    """Test difficulty level variations."""

    def test_easy_has_more_filled_cells_than_hard(self) -> None:
        """Test that easy puzzles have more filled cells than hard puzzles."""
        generator = BacktrackingGenerator()

        easy_board = generator.generate(3, 3, "EASY")
        hard_board = generator.generate(3, 3, "HARD")

        easy_filled = sum(1 for row in easy_board for cell in row if cell != 0)
        hard_filled = sum(1 for row in hard_board for cell in row if cell != 0)

        # Easy should have more cells filled (fewer removed)
        assert easy_filled > hard_filled

    def test_difficulty_affects_empty_cell_count(self) -> None:
        """Test that difficulty level affects number of empty cells."""
        generator = BacktrackingGenerator()

        easy = generator.generate(3, 3, "EASY")
        medium = generator.generate(3, 3, "MEDIUM")
        hard = generator.generate(3, 3, "HARD")

        easy_empty = sum(row.count(0) for row in easy)
        medium_empty = sum(row.count(0) for row in medium)
        hard_empty = sum(row.count(0) for row in hard)

        # Each difficulty should have generally more empty cells
        assert easy_empty < medium_empty < hard_empty

    def test_invalid_difficulty_raises_error(self) -> None:
        """Test that invalid difficulty raises ValueError."""
        generator = BacktrackingGenerator()

        with pytest.raises(ValueError, match="Invalid difficulty"):
            generator.generate(3, 3, "INVALID")

    @pytest.mark.parametrize(
        "difficulty",
        ["EASY", "MEDIUM", "HARD", "easy", "medium", "hard"],
    )
    def test_case_insensitive_difficulty(self, difficulty: str) -> None:
        """Test that difficulty is case-insensitive."""
        generator = BacktrackingGenerator()

        board = generator.generate(3, 3, difficulty)

        assert len(board) == 9


class TestBacktrackingGeneratorValidation:
    """Test that generated boards are valid."""

    def test_generated_board_values_in_range(self) -> None:
        """Test that all values are within valid range (0-9 for 9x9)."""
        generator = BacktrackingGenerator()

        board = generator.generate(3, 3, "MEDIUM")

        for row in board:
            for cell in row:
                assert 0 <= cell <= 9

    def test_generated_6x6_values_in_range(self) -> None:
        """Test that all values are within valid range (0-6 for 6x6)."""
        generator = BacktrackingGenerator()

        board = generator.generate(3, 2, "MEDIUM")

        for row in board:
            for cell in row:
                assert 0 <= cell <= 6

    def test_generated_board_no_duplicates_in_rows(self) -> None:
        """Test that generated board has no duplicates in rows."""
        generator = BacktrackingGenerator()

        board = generator.generate(3, 3, "EASY")

        for row in board:
            non_zero = [cell for cell in row if cell != 0]
            assert len(non_zero) == len(set(non_zero))

    def test_generated_board_no_duplicates_in_columns(self) -> None:
        """Test that generated board has no duplicates in columns."""
        generator = BacktrackingGenerator()

        board = generator.generate(3, 3, "EASY")

        for col_idx in range(9):
            column = [board[row][col_idx] for row in range(9)]
            non_zero = [cell for cell in column if cell != 0]
            assert len(non_zero) == len(set(non_zero))

    def test_generated_board_no_duplicates_in_boxes(self) -> None:
        """Test that generated board has no duplicates in boxes."""
        generator = BacktrackingGenerator()

        board = generator.generate(3, 3, "EASY")

        # Check each 3x3 box
        for box_row in range(3):
            for box_col in range(3):
                box_values = []
                for r in range(box_row * 3, (box_row + 1) * 3):
                    for c in range(box_col * 3, (box_col + 1) * 3):
                        if board[r][c] != 0:
                            box_values.append(board[r][c])

                assert len(box_values) == len(set(box_values))


class TestBacktrackingGeneratorConsistency:
    """Test consistency and reliability of generation."""

    def test_multiple_generations_produce_valid_boards(self) -> None:
        """Test that multiple generations all produce valid boards."""
        generator = BacktrackingGenerator()

        for _ in range(5):
            board = generator.generate(3, 3, "MEDIUM")

            assert len(board) == 9
            assert all(len(row) == 9 for row in board)

    def test_generated_boards_are_different(self) -> None:
        """Test that multiple generations produce different boards."""
        generator = BacktrackingGenerator()

        board1 = generator.generate(3, 3, "MEDIUM")
        board2 = generator.generate(3, 3, "MEDIUM")

        # Boards should be different (very unlikely to be identical)
        assert board1 != board2


class TestBacktrackingGeneratorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_generate_with_default_difficulty(self) -> None:
        """Test generation with default difficulty parameter."""
        generator = BacktrackingGenerator()

        board = generator.generate(3, 3)  # Default is MEDIUM

        assert len(board) == 9

    def test_difficulty_removal_rates_defined(self) -> None:
        """Test that difficulty removal rates are properly configured."""
        generator = BacktrackingGenerator()

        assert "EASY" in generator._difficulty_removal_rates
        assert "MEDIUM" in generator._difficulty_removal_rates
        assert "HARD" in generator._difficulty_removal_rates

    def test_removal_rates_are_tuples(self) -> None:
        """Test that removal rates are tuples with two values."""
        generator = BacktrackingGenerator()

        for _difficulty, rates in generator._difficulty_removal_rates.items():
            assert isinstance(rates, tuple)
            assert len(rates) == 2
            assert rates[0] < rates[1]
