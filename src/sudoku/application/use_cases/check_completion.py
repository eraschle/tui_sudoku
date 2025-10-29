"""Use case for checking if a Sudoku game is complete.

This module implements the business logic for verifying whether
a game has been successfully completed.
"""

from __future__ import annotations

from sudoku.domain.entities.game import Game
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.validators.sudoku_validator import SudokuValidator


class CheckCompletionUseCase:
    """Use case for checking if a Sudoku game is complete.

    This use case handles the verification of game completion, determining
    whether all cells are filled and the solution is correct according to
    Sudoku rules. It follows the Single Responsibility Principle by focusing
    solely on completion verification.

    The actual validation logic is delegated to the validator, while
    this use case provides a clean interface for the application layer.
    """

    def __init__(self, validator: SudokuValidator) -> None:
        """Initialize the use case with a validator.

        Args:
            validator: Board validator for validating Sudoku rules.
        """
        self._validator = validator

    def execute(self, game: Game) -> bool:
        """Check if the game is complete and correctly solved.

        Args:
            game: The current game instance.

        Returns:
            bool: True if the game is complete and correctly solved,
                False otherwise.
        """
        # Check if board is filled
        if not game.board.is_complete():
            return False

        # Convert board to 2D list for validator
        board_list = self._board_to_list(game.board)

        # Get board size info
        board_size = game.board.size
        box_width = board_size.box_cols
        box_height = board_size.box_rows

        # Validate the complete board
        return self._validator.is_board_complete(
            board=board_list, box_width=box_width, box_height=box_height
        )

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
