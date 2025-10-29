"""Unit tests for the GameRules service.

This module tests the GameRules service including validation of rows,
columns, boxes, and complete board states.
"""

import pytest

from sudoku.domain.entities.board import Board
from sudoku.domain.services.game_rules import GameRules
from sudoku.domain.value_objects.board_size import BoardSize
from sudoku.domain.value_objects.position import Position


class TestGameRulesValidRow:
    """Test row validation logic."""

    def test_valid_empty_row(self, empty_board_9x9: Board) -> None:
        """Test that an empty row is valid."""
        assert GameRules.is_valid_row(empty_board_9x9, 0)

    def test_valid_row_with_unique_values(self, empty_board_9x9: Board) -> None:
        """Test that a row with unique values is valid."""
        for col in range(5):
            empty_board_9x9.set_cell_value(Position(0, col), col + 1)

        assert GameRules.is_valid_row(empty_board_9x9, 0)

    def test_invalid_row_with_duplicate(self, empty_board_9x9: Board) -> None:
        """Test that a row with duplicate values is invalid."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(0, 1), 5)

        assert not GameRules.is_valid_row(empty_board_9x9, 0)

    def test_valid_partially_filled_row(self, empty_board_9x9: Board) -> None:
        """Test that partially filled row with no duplicates is valid."""
        empty_board_9x9.set_cell_value(Position(0, 0), 1)
        empty_board_9x9.set_cell_value(Position(0, 5), 7)

        assert GameRules.is_valid_row(empty_board_9x9, 0)

    def test_invalid_row_index_raises_error(self, empty_board_9x9: Board) -> None:
        """Test that invalid row index raises IndexError."""
        with pytest.raises(IndexError):
            GameRules.is_valid_row(empty_board_9x9, 10)


class TestGameRulesValidColumn:
    """Test column validation logic."""

    def test_valid_empty_column(self, empty_board_9x9: Board) -> None:
        """Test that an empty column is valid."""
        assert GameRules.is_valid_column(empty_board_9x9, 0)

    def test_valid_column_with_unique_values(self, empty_board_9x9: Board) -> None:
        """Test that a column with unique values is valid."""
        for row in range(5):
            empty_board_9x9.set_cell_value(Position(row, 0), row + 1)

        assert GameRules.is_valid_column(empty_board_9x9, 0)

    def test_invalid_column_with_duplicate(self, empty_board_9x9: Board) -> None:
        """Test that a column with duplicate values is invalid."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(1, 0), 5)

        assert not GameRules.is_valid_column(empty_board_9x9, 0)

    def test_invalid_column_index_raises_error(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that invalid column index raises IndexError."""
        with pytest.raises(IndexError):
            GameRules.is_valid_column(empty_board_9x9, 10)


class TestGameRulesValidBox:
    """Test box validation logic."""

    def test_valid_empty_box(self, empty_board_9x9: Board) -> None:
        """Test that an empty box is valid."""
        assert GameRules.is_valid_box(empty_board_9x9, Position(0, 0))

    def test_valid_box_with_unique_values(self, empty_board_9x9: Board) -> None:
        """Test that a box with unique values is valid."""
        # Fill top-left 3x3 box
        empty_board_9x9.set_cell_value(Position(0, 0), 1)
        empty_board_9x9.set_cell_value(Position(0, 1), 2)
        empty_board_9x9.set_cell_value(Position(1, 0), 3)

        assert GameRules.is_valid_box(empty_board_9x9, Position(0, 0))

    def test_invalid_box_with_duplicate(self, empty_board_9x9: Board) -> None:
        """Test that a box with duplicate values is invalid."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(1, 1), 5)

        assert not GameRules.is_valid_box(empty_board_9x9, Position(0, 0))

    def test_box_validation_different_positions_same_box(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that different positions in same box give same result."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(2, 2), 5)

        # All positions in top-left box should report invalid
        assert not GameRules.is_valid_box(empty_board_9x9, Position(0, 0))
        assert not GameRules.is_valid_box(empty_board_9x9, Position(1, 1))
        assert not GameRules.is_valid_box(empty_board_9x9, Position(2, 2))

    def test_box_validation_6x6_board(self, empty_board_6x6: Board) -> None:
        """Test box validation for 6x6 board (2x3 boxes)."""
        # Fill some values in top-left 2x3 box
        empty_board_6x6.set_cell_value(Position(0, 0), 1)
        empty_board_6x6.set_cell_value(Position(0, 1), 2)

        assert GameRules.is_valid_box(empty_board_6x6, Position(0, 0))


class TestGameRulesValidPlacement:
    """Test valid placement checking."""

    def test_valid_placement_empty_board(self, empty_board_9x9: Board) -> None:
        """Test that any placement is valid on empty board."""
        assert GameRules.is_valid_placement(
            empty_board_9x9, Position(0, 0), 5
        )

    def test_invalid_placement_duplicate_in_row(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that placement fails if value exists in row."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)

        assert not GameRules.is_valid_placement(
            empty_board_9x9, Position(0, 5), 5
        )

    def test_invalid_placement_duplicate_in_column(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that placement fails if value exists in column."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)

        assert not GameRules.is_valid_placement(
            empty_board_9x9, Position(5, 0), 5
        )

    def test_invalid_placement_duplicate_in_box(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that placement fails if value exists in box."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)

        assert not GameRules.is_valid_placement(
            empty_board_9x9, Position(1, 1), 5
        )

    def test_valid_placement_value_elsewhere(self, empty_board_9x9: Board) -> None:
        """Test that placement is valid if value exists in different region."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)

        # Position (5, 5) is in different row, column, and box
        assert GameRules.is_valid_placement(
            empty_board_9x9, Position(5, 5), 5
        )

    def test_invalid_placement_zero_value(self, empty_board_9x9: Board) -> None:
        """Test that placing zero raises ValueError."""
        with pytest.raises(ValueError, match="Value must be positive"):
            GameRules.is_valid_placement(empty_board_9x9, Position(0, 0), 0)

    def test_invalid_placement_negative_value(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that placing negative value raises ValueError."""
        with pytest.raises(ValueError, match="Value must be positive"):
            GameRules.is_valid_placement(empty_board_9x9, Position(0, 0), -5)


class TestGameRulesValidBoard:
    """Test complete board validation."""

    def test_valid_empty_board(self, empty_board_9x9: Board) -> None:
        """Test that empty board is valid."""
        assert GameRules.is_valid_board(empty_board_9x9)

    def test_valid_partially_filled_board(
        self, partially_filled_board_9x9: Board
    ) -> None:
        """Test that partially filled valid board is valid."""
        assert GameRules.is_valid_board(partially_filled_board_9x9)

    def test_invalid_board_duplicate_in_row(self, empty_board_9x9: Board) -> None:
        """Test that board with duplicate in row is invalid."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(0, 1), 5)

        assert not GameRules.is_valid_board(empty_board_9x9)

    def test_invalid_board_duplicate_in_column(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that board with duplicate in column is invalid."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(1, 0), 5)

        assert not GameRules.is_valid_board(empty_board_9x9)

    def test_invalid_board_duplicate_in_box(self, empty_board_9x9: Board) -> None:
        """Test that board with duplicate in box is invalid."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(2, 2), 5)

        assert not GameRules.is_valid_board(empty_board_9x9)


class TestGameRulesIsSolved:
    """Test solved board checking."""

    def test_empty_board_not_solved(self, empty_board_9x9: Board) -> None:
        """Test that empty board is not solved."""
        assert not GameRules.is_solved(empty_board_9x9)

    def test_partially_filled_board_not_solved(
        self, partially_filled_board_9x9: Board
    ) -> None:
        """Test that partially filled board is not solved."""
        assert not GameRules.is_solved(partially_filled_board_9x9)

    def test_complete_valid_board_is_solved(
        self, board_size_9x9: BoardSize, solved_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that completely filled valid board is solved."""
        board = Board(board_size_9x9)

        # Fill board with solution
        for row in range(9):
            for col in range(9):
                board.set_cell_value(
                    Position(row, col), solved_9x9_puzzle[row][col]
                )

        assert GameRules.is_solved(board)

    def test_complete_invalid_board_not_solved(
        self, board_size_9x9: BoardSize
    ) -> None:
        """Test that completely filled but invalid board is not solved."""
        board = Board(board_size_9x9)

        # Fill board with all 1s (invalid)
        for row in range(9):
            for col in range(9):
                board.set_cell_value(Position(row, col), 1)

        assert not GameRules.is_solved(board)


class TestGameRulesGetCandidates:
    """Test getting candidate values for a position."""

    def test_get_candidates_empty_board(self, empty_board_9x9: Board) -> None:
        """Test that empty position on empty board has all candidates."""
        candidates = GameRules.get_candidates(empty_board_9x9, Position(0, 0))

        assert len(candidates) == 9
        assert candidates == {1, 2, 3, 4, 5, 6, 7, 8, 9}

    def test_get_candidates_filled_cell(self, empty_board_9x9: Board) -> None:
        """Test that filled cell has no candidates."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)

        candidates = GameRules.get_candidates(empty_board_9x9, Position(0, 0))

        assert len(candidates) == 0

    def test_get_candidates_excludes_row_values(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that candidates exclude values in the same row."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(0, 1), 3)

        candidates = GameRules.get_candidates(empty_board_9x9, Position(0, 8))

        assert 5 not in candidates
        assert 3 not in candidates
        assert len(candidates) == 7

    def test_get_candidates_excludes_column_values(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that candidates exclude values in the same column."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(1, 0), 7)

        candidates = GameRules.get_candidates(empty_board_9x9, Position(8, 0))

        assert 5 not in candidates
        assert 7 not in candidates

    def test_get_candidates_excludes_box_values(
        self, empty_board_9x9: Board
    ) -> None:
        """Test that candidates exclude values in the same box."""
        empty_board_9x9.set_cell_value(Position(0, 0), 5)
        empty_board_9x9.set_cell_value(Position(2, 2), 3)

        candidates = GameRules.get_candidates(empty_board_9x9, Position(1, 1))

        assert 5 not in candidates
        assert 3 not in candidates

    def test_get_candidates_constrained_position(
        self, empty_board_9x9: Board
    ) -> None:
        """Test candidates for highly constrained position."""
        # Fill row, column, and box to leave minimal candidates
        for i in range(9):
            if i != 4:
                empty_board_9x9.set_cell_value(Position(0, i), i + 1)

        # Position(0, 4) can only be 5 (the missing value)
        candidates = GameRules.get_candidates(empty_board_9x9, Position(0, 4))

        assert candidates == {5}


class TestGameRulesEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_game_rules_6x6_board(self, empty_board_6x6: Board) -> None:
        """Test that game rules work correctly for 6x6 board."""
        empty_board_6x6.set_cell_value(Position(0, 0), 3)

        assert GameRules.is_valid_row(empty_board_6x6, 0)
        assert GameRules.is_valid_column(empty_board_6x6, 0)
        assert GameRules.is_valid_box(empty_board_6x6, Position(0, 0))

        candidates = GameRules.get_candidates(empty_board_6x6, Position(0, 1))
        assert 3 not in candidates
        assert len(candidates) == 5  # 6 total - 1 used

    @pytest.mark.parametrize("position", [
        Position(0, 0),
        Position(4, 4),
        Position(8, 8),
    ])
    def test_valid_placement_parametrized(
        self, empty_board_9x9: Board, position: Position
    ) -> None:
        """Test valid placement at various positions."""
        assert GameRules.is_valid_placement(empty_board_9x9, position, 5)
