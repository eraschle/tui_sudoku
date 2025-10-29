"""Unit tests for the StartNewGameUseCase.

This module tests the StartNewGame use case including validation
and game creation logic.
"""

import pytest

from sudoku.application.use_cases.start_new_game import StartNewGameUseCase
from sudoku.infrastructure.generators.backtracking_generator import BacktrackingGenerator
from sudoku.infrastructure.validators.sudoku_validator import SudokuValidator


class TestStartNewGameValidation:
    """Test input validation for starting new games."""

    def test_empty_player_name_raises_error(self) -> None:
        """Test that empty player name raises ValueError."""
        generator = BacktrackingGenerator()
        validator = SudokuValidator()
        use_case = StartNewGameUseCase(generator, validator)

        with pytest.raises(ValueError, match="Player name cannot be empty"):
            use_case.execute(player_name="", difficulty="easy", size=9)

    def test_whitespace_player_name_raises_error(self) -> None:
        """Test that whitespace-only player name raises ValueError."""
        generator = BacktrackingGenerator()
        validator = SudokuValidator()
        use_case = StartNewGameUseCase(generator, validator)

        with pytest.raises(ValueError, match="Player name cannot be empty"):
            use_case.execute(player_name="   ", difficulty="easy", size=9)

    def test_invalid_difficulty_raises_error(self) -> None:
        """Test that invalid difficulty raises ValueError."""
        generator = BacktrackingGenerator()
        validator = SudokuValidator()
        use_case = StartNewGameUseCase(generator, validator)

        with pytest.raises(ValueError, match="Invalid difficulty"):
            use_case.execute(
                player_name="Player1", difficulty="impossible", size=9
            )

    def test_invalid_size_raises_error(self) -> None:
        """Test that invalid size raises ValueError."""
        generator = BacktrackingGenerator()
        validator = SudokuValidator()
        use_case = StartNewGameUseCase(generator, validator)

        with pytest.raises(ValueError, match="Invalid size"):
            use_case.execute(player_name="Player1", difficulty="easy", size=10)

    @pytest.mark.parametrize(
        "difficulty", ["easy", "EASY", "Easy", "medium", "MEDIUM", "hard", "HARD"]
    )
    def test_case_insensitive_difficulty(self, difficulty: str) -> None:
        """Test that difficulty is case-insensitive."""
        generator = BacktrackingGenerator()
        validator = SudokuValidator()
        use_case = StartNewGameUseCase(generator, validator)

        # Should not raise error
        game, game_state = use_case.execute(player_name="Player1", difficulty=difficulty, size=9)
        assert game is not None
        assert game_state is not None


class TestStartNewGameExecution:
    """Test use case execution logic."""

    def test_execute_returns_game_and_state(self) -> None:
        """Test that execute returns a game and game state."""
        generator = BacktrackingGenerator()
        validator = SudokuValidator()
        use_case = StartNewGameUseCase(generator, validator)

        result = use_case.execute(player_name="Player1", difficulty="easy", size=9)

        assert isinstance(result, tuple)
        assert len(result) == 2
        game, game_state = result
        assert game is not None
        assert game_state is not None

    def test_execute_with_default_size(self) -> None:
        """Test execute with default size parameter."""
        generator = BacktrackingGenerator()
        validator = SudokuValidator()
        use_case = StartNewGameUseCase(generator, validator)

        game, game_state = use_case.execute(player_name="Player1", difficulty="easy")

        assert game.board.size.rows == 9  # Default size

    @pytest.mark.parametrize("size", [4, 9, 16])
    def test_execute_with_valid_sizes(self, size: int) -> None:
        """Test execute with different valid sizes."""
        generator = BacktrackingGenerator()
        validator = SudokuValidator()
        use_case = StartNewGameUseCase(generator, validator)

        game, game_state = use_case.execute(player_name="Player1", difficulty="easy", size=size)

        assert game.board.size.rows == size

    def test_created_game_is_started(self) -> None:
        """Test that the created game is started automatically."""
        generator = BacktrackingGenerator()
        validator = SudokuValidator()
        use_case = StartNewGameUseCase(generator, validator)

        game, _ = use_case.execute(player_name="Player1", difficulty="easy", size=9)

        assert game.is_active
