"""Unit tests for the CheckCompletionUseCase.

This module tests the CheckCompletion use case including
completion verification logic.
"""

from sudoku.application.use_cases.check_completion import CheckCompletionUseCase
from sudoku.domain.entities.board import Board
from sudoku.domain.entities.game import Game
from sudoku.domain.entities.player import Player
from sudoku.domain.value_objects.board_size import BoardSize
from sudoku.domain.value_objects.difficulty import Difficulty
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.validators.sudoku_validator import SudokuValidator


def create_incomplete_game() -> Game:
    """Create an incomplete game for testing."""
    board = Board(BoardSize(9, 9, 3, 3))
    # Leave most cells empty - incomplete
    board.set_cell_value(Position(0, 0), 1, is_fixed=True)
    return Game(board=board, player=Player("TestPlayer"), difficulty=Difficulty.EASY)


def create_filled_invalid_game() -> Game:
    """Create a filled but invalid game for testing."""
    board = Board(BoardSize(9, 9, 3, 3))
    # Fill with all 1s - invalid
    for row in range(9):
        for col in range(9):
            board.set_cell_value(Position(row, col), 1, is_fixed=False)
    return Game(board=board, player=Player("TestPlayer"), difficulty=Difficulty.EASY)


def create_complete_valid_game() -> Game:
    """Create a complete and valid game for testing."""
    board = Board(BoardSize(9, 9, 3, 3))
    # Use a valid solved board
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    for row in range(9):
        for col in range(9):
            board.set_cell_value(Position(row, col), solution[row][col], is_fixed=False)
    return Game(board=board, player=Player("TestPlayer"), difficulty=Difficulty.EASY)


class TestCheckCompletionExecution:
    """Test use case execution logic."""

    def test_execute_returns_false_for_incomplete_game(self) -> None:
        """Test that execute returns False for incomplete game."""
        validator = SudokuValidator()
        game = create_incomplete_game()
        use_case = CheckCompletionUseCase(validator)

        result = use_case.execute(game)

        assert result is False

    def test_execute_returns_true_for_complete_game(self) -> None:
        """Test that execute returns True for complete game."""
        validator = SudokuValidator()
        game = create_complete_valid_game()
        use_case = CheckCompletionUseCase(validator)

        result = use_case.execute(game)

        assert result is True

    def test_execute_returns_false_for_filled_but_invalid(self) -> None:
        """Test that execute returns False for filled but invalid board."""
        validator = SudokuValidator()
        game = create_filled_invalid_game()
        use_case = CheckCompletionUseCase(validator)

        result = use_case.execute(game)

        assert result is False
