"""Game state manager for Sudoku game screen.

This module manages game state (paused, elapsed time, etc.),
following the Single Responsibility Principle.
"""

from __future__ import annotations

from datetime import timedelta


class GameStateManager:
    """Manages game state for the game screen.

    Responsibilities:
    - Pause/resume state
    - Elapsed time tracking
    - Game state (In Progress, Won, Paused, etc.)
    """

    def __init__(
        self,
        initial_state: str = "In Progress",
        initial_time: timedelta | None = None,
    ) -> None:
        """Initialize the state manager.

        Args:
            initial_state: Initial game state.
            initial_time: Initial elapsed time.
        """
        self._is_paused = False
        self._elapsed_time = initial_time or timedelta()
        self._game_state = initial_state

    @property
    def is_paused(self) -> bool:
        """Check if game is paused."""
        return self._is_paused

    @property
    def elapsed_time(self) -> timedelta:
        """Get elapsed time."""
        return self._elapsed_time

    @property
    def game_state(self) -> str:
        """Get current game state."""
        return self._game_state

    def pause(self) -> None:
        """Pause the game."""
        self._is_paused = True
        self._game_state = "Paused"

    def resume(self) -> None:
        """Resume the game."""
        self._is_paused = False
        self._game_state = "In Progress"

    def toggle_pause(self) -> bool:
        """Toggle pause state.

        Returns:
            bool: True if now paused, False if now resumed.
        """
        if self._is_paused:
            self.resume()
        else:
            self.pause()
        return self._is_paused

    def increment_time(self, seconds: int = 1) -> None:
        """Increment elapsed time if not paused.

        Args:
            seconds: Number of seconds to add.
        """
        if not self._is_paused and self._game_state == "In Progress":
            self._elapsed_time += timedelta(seconds=seconds)

    def set_state(self, state: str) -> None:
        """Set the game state.

        Args:
            state: New game state.
        """
        self._game_state = state

    def set_elapsed_time(self, elapsed: timedelta) -> None:
        """Set the elapsed time.

        Args:
            elapsed: New elapsed time.
        """
        self._elapsed_time = elapsed
