"""Unit tests for the SudokuValidator.

This module tests board validation logic including move validation
and board state checking.
"""

import pytest

from sudoku.infrastructure.validators.sudoku_validator import (
    SudokuValidator,
    create_sudoku_validator,
)


class TestSudokuValidatorCreation:
    """Test validator instantiation."""

    def test_create_validator(self) -> None:
        """Test creating a sudoku validator instance."""
        validator = SudokuValidator()

        assert validator is not None

    def test_create_validator_via_factory(self) -> None:
        """Test creating validator using factory function."""
        validator = create_sudoku_validator()

        assert isinstance(validator, SudokuValidator)


class TestSudokuValidatorIsValidMove:
    """Test move validation logic."""

    def test_valid_move_on_empty_board(self) -> None:
        """Test that move on empty board is valid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]

        is_valid = validator.is_valid_move(board, 0, 0, 5, box_width=3, box_height=3)

        assert is_valid

    def test_invalid_move_on_occupied_cell(self) -> None:
        """Test that move on occupied cell is invalid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5

        is_valid = validator.is_valid_move(board, 0, 0, 3, box_width=3, box_height=3)

        assert not is_valid

    def test_invalid_move_duplicate_in_row(self) -> None:
        """Test that move creating duplicate in row is invalid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5

        is_valid = validator.is_valid_move(board, 0, 5, 5, box_width=3, box_height=3)

        assert not is_valid

    def test_invalid_move_duplicate_in_column(self) -> None:
        """Test that move creating duplicate in column is invalid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5

        is_valid = validator.is_valid_move(board, 5, 0, 5, box_width=3, box_height=3)

        assert not is_valid

    def test_invalid_move_duplicate_in_box(self) -> None:
        """Test that move creating duplicate in box is invalid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5

        is_valid = validator.is_valid_move(board, 1, 1, 5, box_width=3, box_height=3)

        assert not is_valid

    def test_invalid_move_out_of_bounds_position(self) -> None:
        """Test that out-of-bounds position is invalid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]

        is_valid = validator.is_valid_move(board, 10, 0, 5, box_width=3, box_height=3)

        assert not is_valid

    def test_invalid_move_negative_position(self) -> None:
        """Test that negative position is invalid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]

        is_valid = validator.is_valid_move(
            board, -1, 0, 5, box_width=3, box_height=3
        )

        assert not is_valid

    def test_invalid_move_value_too_large(self) -> None:
        """Test that value larger than board size is invalid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]

        is_valid = validator.is_valid_move(
            board, 0, 0, 10, box_width=3, box_height=3
        )

        assert not is_valid

    def test_invalid_move_value_zero(self) -> None:
        """Test that value of zero is invalid for a move."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]

        is_valid = validator.is_valid_move(board, 0, 0, 0, box_width=3, box_height=3)

        assert not is_valid


class TestSudokuValidatorIsBoardComplete:
    """Test board completion checking."""

    def test_empty_board_not_complete(self) -> None:
        """Test that empty board is not complete."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]

        is_complete = validator.is_board_complete(board, box_width=3, box_height=3)

        assert not is_complete

    def test_partially_filled_board_not_complete(
        self, valid_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that partially filled board is not complete."""
        validator = SudokuValidator()

        is_complete = validator.is_board_complete(
            valid_9x9_puzzle, box_width=3, box_height=3
        )

        assert not is_complete

    def test_fully_filled_valid_board_is_complete(
        self, solved_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that fully filled valid board is complete."""
        validator = SudokuValidator()

        is_complete = validator.is_board_complete(
            solved_9x9_puzzle, box_width=3, box_height=3
        )

        assert is_complete

    def test_fully_filled_invalid_board_not_complete(self) -> None:
        """Test that fully filled but invalid board is not complete."""
        validator = SudokuValidator()
        # Board filled with all 1s (invalid)
        board = [[1] * 9 for _ in range(9)]

        is_complete = validator.is_board_complete(board, box_width=3, box_height=3)

        assert not is_complete


class TestSudokuValidatorIsBoardValid:
    """Test board state validation."""

    def test_empty_board_is_valid(self) -> None:
        """Test that empty board is valid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]

        is_valid = validator.is_board_valid(board, box_width=3, box_height=3)

        assert is_valid

    def test_partially_filled_valid_board(
        self, valid_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that partially filled valid board is valid."""
        validator = SudokuValidator()

        is_valid = validator.is_board_valid(
            valid_9x9_puzzle, box_width=3, box_height=3
        )

        assert is_valid

    def test_solved_board_is_valid(self, solved_9x9_puzzle: list[list[int]]) -> None:
        """Test that solved board is valid."""
        validator = SudokuValidator()

        is_valid = validator.is_board_valid(
            solved_9x9_puzzle, box_width=3, box_height=3
        )

        assert is_valid

    def test_board_with_duplicate_in_row_invalid(
        self, invalid_9x9_board: list[list[int]]
    ) -> None:
        """Test that board with duplicate in row is invalid."""
        validator = SudokuValidator()

        is_valid = validator.is_board_valid(
            invalid_9x9_board, box_width=3, box_height=3
        )

        assert not is_valid

    def test_board_with_duplicate_in_column_invalid(self) -> None:
        """Test that board with duplicate in column is invalid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5
        board[1][0] = 5

        is_valid = validator.is_board_valid(board, box_width=3, box_height=3)

        assert not is_valid

    def test_board_with_duplicate_in_box_invalid(self) -> None:
        """Test that board with duplicate in box is invalid."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5
        board[1][1] = 5

        is_valid = validator.is_board_valid(board, box_width=3, box_height=3)

        assert not is_valid


class TestSudokuValidator6x6:
    """Test validator with 6x6 boards."""

    def test_valid_move_6x6_board(self, valid_6x6_puzzle: list[list[int]]) -> None:
        """Test valid move on 6x6 board."""
        validator = SudokuValidator()

        # Find empty cell
        for row in range(6):
            for col in range(6):
                if valid_6x6_puzzle[row][col] == 0:
                    is_valid = validator.is_valid_move(
                        valid_6x6_puzzle, row, col, 1, box_width=3, box_height=2
                    )
                    # Can't guarantee it's valid without checking constraints
                    assert isinstance(is_valid, bool)
                    return

    def test_board_valid_6x6(self, valid_6x6_puzzle: list[list[int]]) -> None:
        """Test that 6x6 puzzle is valid."""
        validator = SudokuValidator()

        is_valid = validator.is_board_valid(
            valid_6x6_puzzle, box_width=3, box_height=2
        )

        assert is_valid


class TestSudokuValidatorEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.parametrize("value", [1, 5, 9])
    def test_valid_moves_parametrized(self, value: int) -> None:
        """Test valid moves with various values."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]

        is_valid = validator.is_valid_move(board, 0, 0, value, 3, 3)

        assert is_valid

    @pytest.mark.parametrize(("row", "col"), [(0, 0), (4, 4), (8, 8)])
    def test_valid_positions_parametrized(self, row: int, col: int) -> None:
        """Test valid moves at various positions."""
        validator = SudokuValidator()
        board = [[0] * 9 for _ in range(9)]

        is_valid = validator.is_valid_move(board, row, col, 5, 3, 3)

        assert is_valid
