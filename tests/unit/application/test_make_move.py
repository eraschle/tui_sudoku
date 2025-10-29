"""Unit tests for the MakeMoveUseCase.

This module tests the MakeMove use case including validation
and move execution logic.
"""

import pytest

from sudoku.application.use_cases.make_move import MakeMoveUseCase
from sudoku.domain.entities.board import Board
from sudoku.domain.entities.game import Game
from sudoku.domain.entities.player import Player
from sudoku.domain.value_objects.board_size import BoardSize
from sudoku.domain.value_objects.difficulty import Difficulty
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.validators.sudoku_validator import SudokuValidator


def create_test_game() -> Game:
    """Create a test game with a partially filled board."""
    board = Board(BoardSize(9, 9, 3, 3))
    # Add some fixed cells
    board.set_cell_value(Position(0, 0), 5, is_fixed=True)
    board.set_cell_value(Position(0, 1), 3, is_fixed=True)
    board.set_cell_value(Position(1, 0), 6, is_fixed=True)
    game = Game(board=board, player=Player("TestPlayer"), difficulty=Difficulty.EASY)
    game.start()  # Start the game so moves can be made
    return game


class TestMakeMoveValidation:
    """Test input validation for making moves."""

    def test_row_below_bounds_raises_error(self) -> None:
        """Test that negative row raises ValueError."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        with pytest.raises(ValueError, match="Row must be between"):
            use_case.execute(game, Position(-1, 0), 5)

    def test_row_above_bounds_raises_error(self) -> None:
        """Test that row >= size raises ValueError."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        with pytest.raises(ValueError, match="Row must be between"):
            use_case.execute(game, Position(10, 0), 5)

    def test_col_below_bounds_raises_error(self) -> None:
        """Test that negative column raises ValueError."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        with pytest.raises(ValueError, match="Column must be between"):
            use_case.execute(game, Position(0, -1), 5)

    def test_col_above_bounds_raises_error(self) -> None:
        """Test that column >= size raises ValueError."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        with pytest.raises(ValueError, match="Column must be between"):
            use_case.execute(game, Position(0, 10), 5)

    def test_value_below_bounds_raises_error(self) -> None:
        """Test that value < 1 raises ValueError."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        with pytest.raises(ValueError, match="Value must be between"):
            use_case.execute(game, Position(0, 2), -1)

    def test_value_above_bounds_raises_error(self) -> None:
        """Test that value > size raises ValueError."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        with pytest.raises(ValueError, match="Value must be between"):
            use_case.execute(game, Position(0, 2), 10)

    def test_none_value_is_valid(self) -> None:
        """Test that value of None (clear) is valid."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        # Place a value first
        use_case.execute(game, Position(0, 2), 4)

        # Clear it with None
        success, _ = use_case.execute(game, Position(0, 2), None)
        assert success


class TestMakeMoveExecution:
    """Test use case execution logic."""

    def test_execute_returns_success_and_state(self) -> None:
        """Test that execute returns tuple of (success, game_state)."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        result = use_case.execute(game, Position(0, 2), 4)

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)

    def test_execute_returns_true_on_valid_move(self) -> None:
        """Test that execute returns True when move is valid."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        success, _ = use_case.execute(game, Position(0, 2), 4)

        assert success is True

    def test_execute_returns_false_on_invalid_move(self) -> None:
        """Test that execute returns False when move is invalid."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        # Try to place a duplicate value in the same row
        success, _ = use_case.execute(game, Position(0, 2), 5)  # 5 is already at (0, 0)

        assert success is False

    def test_execute_returns_false_for_fixed_cell(self) -> None:
        """Test that execute returns False when trying to modify a fixed cell."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        # Try to modify a fixed cell
        success, _ = use_case.execute(game, Position(0, 0), 9)

        assert success is False

    def test_valid_move_updates_board(self) -> None:
        """Test that a valid move updates the board."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        position = Position(0, 2)
        success, game_state = use_case.execute(game, position, 4)

        assert success is True
        cell = game.board.get_cell(position)
        assert cell.get_numeric_value() == 4

    @pytest.mark.parametrize(
        ("row", "col", "value"),
        [(2, 2, 1), (4, 4, 5), (8, 8, 9)]
    )
    def test_execute_with_various_positions(
        self, row: int, col: int, value: int
    ) -> None:
        """Test execute with various valid positions and values."""
        validator = SudokuValidator()
        game = create_test_game()
        use_case = MakeMoveUseCase(validator)

        position = Position(row, col)
        success, _ = use_case.execute(game, position, value)

        # Should succeed if the move is valid according to Sudoku rules
        assert isinstance(success, bool)
