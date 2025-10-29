"""Data Transfer Object for game state.

This module provides a DTO for transferring game state information
between the application layer and presentation layer.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GameStateDTO:
    """Data Transfer Object representing the state of a Sudoku game.

    This immutable object encapsulates all information needed to represent
    the current state of a game to the presentation layer.

    Attributes:
        player_name: The name of the player.
        difficulty: The difficulty level of the game.
        size: The size of the Sudoku grid (e.g., 9 for 9x9).
        current_board: A 2D list representing the current board state.
        initial_board: A 2D list representing the initial puzzle state.
        elapsed_time: The time elapsed since the game started, in seconds.
        is_complete: Whether the game has been successfully completed.
    """

    player_name: str
    difficulty: str
    size: int
    current_board: tuple[tuple[int, ...], ...]
    initial_board: tuple[tuple[int, ...], ...]
    elapsed_time: float
    is_complete: bool

    @classmethod
    def from_game(cls, game) -> "GameStateDTO":
        """Create a GameStateDTO from a Game entity.

        Args:
            game: A Game entity.

        Returns:
            GameStateDTO: A new instance containing the game's current state.
        """
        current_board = game.get_board_state()
        initial_board = game.get_initial_board_state()

        # Convert difficulty enum to string
        if hasattr(game.difficulty, 'name'):
            difficulty_str = game.difficulty.name.lower()
        else:
            difficulty_str = str(game.difficulty).lower()

        # Convert timedelta to seconds
        elapsed_seconds = game.elapsed_time.total_seconds()

        return cls(
            player_name=game.player_name,
            difficulty=difficulty_str,
            size=game.size,
            current_board=tuple(tuple(row) for row in current_board),
            initial_board=tuple(tuple(row) for row in initial_board),
            elapsed_time=elapsed_seconds,
            is_complete=game.is_complete(),
        )

    def get_cell_value(self, row: int, col: int) -> int:
        """Get the value at a specific cell in the current board.

        Args:
            row: The row index (0-based).
            col: The column index (0-based).

        Returns:
            int: The value at the specified cell (0 for empty).

        Raises:
            IndexError: If row or col is out of bounds.
        """
        return self.current_board[row][col]

    def is_initial_cell(self, row: int, col: int) -> bool:
        """Check if a cell was part of the initial puzzle.

        Args:
            row: The row index (0-based).
            col: The column index (0-based).

        Returns:
            bool: True if the cell is part of the initial puzzle, False otherwise.

        Raises:
            IndexError: If row or col is out of bounds.
        """
        return self.initial_board[row][col] != 0
