"""Game entity orchestrating the Sudoku game session.

This module provides the Game entity which represents a single game session,
coordinating the board, player, difficulty, and timing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto

from sudoku.domain.value_objects.difficulty import Difficulty
from sudoku.domain.value_objects.position import Position

from .board import Board
from .player import Player


class GameState(Enum):
    """Enumeration of possible game states."""

    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    WON = auto()
    LOST = auto()
    PAUSED = auto()


@dataclass
class Game:
    """Entity representing a Sudoku game session.

    Orchestrates the game board, player, difficulty level, and timer.
    Manages the game lifecycle from start to completion.

    Attributes:
        board: The game board.
        player: The player playing the game.
        difficulty: The difficulty level.
        state: Current state of the game.
    """

    board: Board
    player: Player
    difficulty: Difficulty
    state: GameState = field(default=GameState.NOT_STARTED)
    _start_time: datetime | None = field(default=None, init=False)
    _end_time: datetime | None = field(default=None, init=False)
    _pause_time: datetime | None = field(default=None, init=False)
    _total_paused_duration: timedelta = field(
        default_factory=lambda: timedelta(), init=False
    )

    def start(self) -> None:
        """Start the game.

        Raises:
            ValueError: If game has already been started.
        """
        if self.state != GameState.NOT_STARTED:
            msg = "Game has already been started"
            raise ValueError(msg)

        self.state = GameState.IN_PROGRESS
        self._start_time = datetime.now()

    def pause(self) -> None:
        """Pause the game.

        Raises:
            ValueError: If game is not in progress.
        """
        if self.state != GameState.IN_PROGRESS:
            msg = "Can only pause a game in progress"
            raise ValueError(msg)

        self.state = GameState.PAUSED
        self._pause_time = datetime.now()

    def resume(self) -> None:
        """Resume a paused game.

        Raises:
            ValueError: If game is not paused.
        """
        if self.state != GameState.PAUSED:
            msg = "Can only resume a paused game"
            raise ValueError(msg)

        if self._pause_time is not None:
            pause_duration = datetime.now() - self._pause_time
            self._total_paused_duration += pause_duration
            self._pause_time = None

        self.state = GameState.IN_PROGRESS

    def make_move(self, position: Position, value: int | None) -> None:
        """Make a move by placing or clearing a value on the board.

        Args:
            position: The position to modify.
            value: The value to place (None to clear).

        Raises:
            ValueError: If game is not in progress.
            IndexError: If position is out of bounds.
        """
        if self.state != GameState.IN_PROGRESS:
            msg = "Cannot make moves when game is not in progress"
            raise ValueError(msg)

        if value is None:
            self.board.clear_cell(position)
        else:
            self.board.set_cell_value(position, value)

    def mark_as_won(self) -> None:
        """Mark the game as won.

        Raises:
            ValueError: If game is not in progress.
        """
        if self.state != GameState.IN_PROGRESS:
            msg = "Can only win a game in progress"
            raise ValueError(msg)

        self.state = GameState.WON
        self._end_time = datetime.now()

    def mark_as_lost(self) -> None:
        """Mark the game as lost.

        Raises:
            ValueError: If game is not in progress.
        """
        if self.state != GameState.IN_PROGRESS:
            msg = "Can only lose a game in progress"
            raise ValueError(msg)

        self.state = GameState.LOST
        self._end_time = datetime.now()

    @property
    def elapsed_time(self) -> timedelta:
        """Calculate the elapsed game time excluding pauses.

        Returns:
            Time elapsed since game started, excluding paused time.
            Returns zero if game hasn't started.
        """
        if self._start_time is None:
            return timedelta()

        if self.state == GameState.PAUSED and self._pause_time is not None:
            end_time = self._pause_time
        elif self._end_time is not None:
            end_time = self._end_time
        else:
            end_time = datetime.now()

        total_time = end_time - self._start_time
        return total_time - self._total_paused_duration

    @property
    def is_active(self) -> bool:
        """Check if the game is currently active (in progress or paused).

        Returns:
            True if game is in progress or paused, False otherwise.
        """
        return self.state in (GameState.IN_PROGRESS, GameState.PAUSED)

    @property
    def is_finished(self) -> bool:
        """Check if the game has finished (won or lost).

        Returns:
            True if game is won or lost, False otherwise.
        """
        return self.state in (GameState.WON, GameState.LOST)

    @property
    def player_name(self) -> str:
        """Get the player's name.

        Returns:
            The player's name.
        """
        return self.player.name

    @property
    def size(self) -> int:
        """Get the board size.

        Returns:
            The board size (e.g., 9 for 9x9).
        """
        return self.board.size.rows

    def get_board_state(self) -> list[list[int]]:
        """Get the current board state as a 2D list.

        Returns:
            2D list representing current board state with 0 for empty cells.
        """
        size = self.board.size.rows
        result = []
        for row in range(size):
            row_values = []
            for col in range(size):
                position = Position(row, col)
                cell = self.board.get_cell(position)
                if cell.value.value is None:
                    row_values.append(0)
                else:
                    row_values.append(cell.value.value)
            result.append(row_values)
        return result

    def get_initial_board_state(self) -> list[list[int]]:
        """Get the initial puzzle state as a 2D list.

        Returns:
            2D list representing initial puzzle with 0 for empty cells.
        """
        size = self.board.size.rows
        result = []
        for row in range(size):
            row_values = []
            for col in range(size):
                position = Position(row, col)
                cell = self.board.get_cell(position)
                # Fixed cells are part of the initial puzzle
                if cell.is_fixed:
                    if cell.value.value is None:
                        row_values.append(0)
                    else:
                        row_values.append(cell.value.value)
                else:
                    row_values.append(0)
            result.append(row_values)
        return result

    def is_complete(self) -> bool:
        """Check if the game is complete.

        Note: This only checks if the board is filled.
        Use a validator to check if the solution is correct.

        Returns:
            True if all cells are filled, False otherwise.
        """
        return self.board.is_complete()

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            String representation of the game.
        """
        return (
            f"Game({self.player.name}, {self.difficulty}, "
            f"{self.state.name}, {self.elapsed_time})"
        )
