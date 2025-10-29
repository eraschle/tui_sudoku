"""Use case for making a move in a Sudoku game.

This module implements the business logic for processing a player's move
and updating the game state.
"""

from __future__ import annotations

from sudoku.application.dto import GameStateDTO
from sudoku.domain.entities.game import Game
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.validators.sudoku_validator import SudokuValidator


class MakeMoveUseCase:
    """Use case for making a move in a Sudoku game.

    This use case handles the validation and execution of a player's move,
    ensuring that the move adheres to game rules. It follows the Single
    Responsibility Principle by focusing solely on move processing.

    The game state is managed by the Game entity, while this use case
    coordinates the move operation and returns the updated state.
    """

    def __init__(self, validator: SudokuValidator) -> None:
        """Initialize the use case with a validator.

        Args:
            validator: Board validator for validating Sudoku rules.
        """
        self._validator = validator

    def execute(
        self, game: Game, position: Position, value: int | None
    ) -> tuple[bool, GameStateDTO]:
        """Execute a move at the specified position.

        Args:
            game: The current game instance.
            position: The position where to make the move.
            value: The value to place (1-9 for standard Sudoku, None to clear).

        Returns:
            tuple[bool, GameStateDTO]: A tuple containing:
                - bool: True if the move was valid and applied, False otherwise.
                - GameStateDTO: The updated game state after the move attempt.

        Raises:
            ValueError: If game is not in progress or position/value is invalid.
        """
        self._validate_input(game, position, value)

        # Get board size info
        board_size = game.board.size
        box_width = board_size.box_cols
        box_height = board_size.box_rows

        # Handle clearing a cell
        if value is None:
            try:
                game.make_move(position, None)
                updated_state = GameStateDTO.from_game(game)
                return True, updated_state
            except ValueError:
                # Cell is fixed or other error
                updated_state = GameStateDTO.from_game(game)
                return False, updated_state

        # Convert board to 2D list for validator
        current_board = self._board_to_list(game.board)

        # Validate the move using the validator
        is_valid = self._validator.is_valid_move(
            board=current_board,
            row=position.row,
            col=position.col,
            num=value,
            box_width=box_width,
            box_height=box_height,
        )

        if is_valid:
            try:
                game.make_move(position, value)
                updated_state = GameStateDTO.from_game(game)
                return True, updated_state
            except ValueError:
                # Move failed (e.g., fixed cell)
                updated_state = GameStateDTO.from_game(game)
                return False, updated_state
        else:
            # Invalid move according to Sudoku rules
            updated_state = GameStateDTO.from_game(game)
            return False, updated_state

    def _validate_input(
        self, game: Game, position: Position, value: int | None
    ) -> None:
        """Validate the input parameters for a move.

        Args:
            game: The game instance.
            position: The position where to make the move.
            value: The value to place.

        Raises:
            ValueError: If any parameter is invalid.
        """
        size = game.board.size.rows

        if not 0 <= position.row < size:
            msg = f"Row must be between 0 and {size - 1}, got {position.row}"
            raise ValueError(msg)

        if not 0 <= position.col < size:
            msg = f"Column must be between 0 and {size - 1}, got {position.col}"
            raise ValueError(msg)

        if value is not None and not 1 <= value <= size:
            msg = f"Value must be between 1 and {size}, got {value}"
            raise ValueError(msg)

    def _board_to_list(self, board) -> list[list[int]]:
        """Convert board entity to 2D list for validator.

        Args:
            board: Board entity.

        Returns:
            2D list representation of the board.
        """
        size = board.size.rows
        result = []
        for row in range(size):
            row_values = []
            for col in range(size):
                position = Position(row, col)
                cell = board.get_cell(position)
                if cell.value.value is None:
                    row_values.append(0)
                else:
                    row_values.append(cell.value.value)
            result.append(row_values)
        return result
