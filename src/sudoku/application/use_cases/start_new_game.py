"""Use case for starting a new Sudoku game.

This module implements the business logic for creating and initializing
a new game with specified parameters.
"""

from __future__ import annotations

from sudoku.application.dto import GameStateDTO
from sudoku.domain.entities.board import Board
from sudoku.domain.entities.game import Game
from sudoku.domain.entities.player import Player
from sudoku.domain.value_objects.board_size import BoardSize
from sudoku.domain.value_objects.difficulty import Difficulty
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.generators.backtracking_generator import BacktrackingGenerator
from sudoku.infrastructure.validators.sudoku_validator import SudokuValidator


class StartNewGameUseCase:
    """Use case for starting a new Sudoku game.

    This use case handles the creation of a new game with the specified
    difficulty, size, and player information. It follows the Single
    Responsibility Principle by focusing solely on game initialization.

    The use case uses dependency injection to receive a board generator
    and validator, promoting loose coupling and testability.
    """

    def __init__(
        self, generator: BacktrackingGenerator, validator: SudokuValidator
    ) -> None:
        """Initialize the use case with dependencies.

        Args:
            generator: Board generator for creating Sudoku puzzles.
            validator: Board validator for validating Sudoku rules.
        """
        self._generator = generator
        self._validator = validator

    def execute(
        self,
        player_name: str,
        difficulty: str,
        size: int = 9,
    ) -> tuple[Game, GameStateDTO]:
        """Start a new game with the specified parameters.

        Args:
            player_name: The name of the player.
            difficulty: The difficulty level (e.g., 'easy', 'medium', 'hard').
            size: The size of the Sudoku grid (default: 9 for 9x9).

        Returns:
            tuple[Game, GameStateDTO]: A tuple containing:
                - Game: The created game entity.
                - GameStateDTO: The initial state of the newly created game.

        Raises:
            ValueError: If player_name is empty, difficulty is invalid,
                or size is not supported.
        """
        self._validate_input(player_name, difficulty, size)

        # Create player
        player = Player(name=player_name)

        # Map difficulty string to Difficulty enum
        difficulty_enum = self._map_difficulty(difficulty)

        # Create board size
        board_size = self._create_board_size(size)

        # Generate puzzle using backtracking generator
        puzzle_grid = self._generator.generate(
            box_width=board_size.box_cols,
            box_height=board_size.box_rows,
            difficulty=difficulty.upper(),
        )

        # Create board and set initial values
        board = Board(board_size)
        for row in range(board_size.rows):
            for col in range(board_size.cols):
                value = puzzle_grid[row][col]
                if value != 0:
                    position = Position(row, col)
                    board.set_cell_value(position, value, is_fixed=True)

        # Create game
        game = Game(board=board, player=player, difficulty=difficulty_enum)
        game.start()

        return game, GameStateDTO.from_game(game)

    def _validate_input(self, player_name: str, difficulty: str, size: int) -> None:
        """Validate the input parameters for starting a new game.

        Args:
            player_name: The name of the player.
            difficulty: The difficulty level.
            size: The size of the Sudoku grid.

        Raises:
            ValueError: If any parameter is invalid.
        """
        if not player_name or not player_name.strip():
            msg = "Player name cannot be empty"
            raise ValueError(msg)

        valid_difficulties = {"easy", "medium", "hard"}
        if difficulty.lower() not in valid_difficulties:
            msg = (
                f"Invalid difficulty '{difficulty}'. "
                f"Must be one of: {', '.join(valid_difficulties)}"
            )
            raise ValueError(msg)

        valid_sizes = {4, 9, 16}
        if size not in valid_sizes:
            msg = f"Invalid size {size}. Must be one of: {', '.join(map(str, valid_sizes))}"
            raise ValueError(msg)

    def _map_difficulty(self, difficulty: str) -> Difficulty:
        """Map difficulty string to Difficulty enum.

        Args:
            difficulty: The difficulty string.

        Returns:
            Difficulty enum value.
        """
        difficulty_map = {
            "easy": Difficulty.EASY,
            "medium": Difficulty.MEDIUM,
            "hard": Difficulty.HARD,
        }
        return difficulty_map[difficulty.lower()]

    def _create_board_size(self, size: int) -> BoardSize:
        """Create board size configuration based on total size.

        Args:
            size: Total board size (e.g., 9 for 9x9).

        Returns:
            BoardSize configuration.

        Raises:
            ValueError: If size is not supported.
        """
        if size == 4:
            return BoardSize(rows=4, cols=4, box_rows=2, box_cols=2)
        elif size == 9:
            return BoardSize(rows=9, cols=9, box_rows=3, box_cols=3)
        elif size == 16:
            return BoardSize(rows=16, cols=16, box_rows=4, box_cols=4)
        else:
            msg = f"Unsupported board size: {size}"
            raise ValueError(msg)
