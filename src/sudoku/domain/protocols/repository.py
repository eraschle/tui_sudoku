"""Repository protocols for persistence layer.

This module defines the protocols that repositories must implement
for persisting and retrieving game data and statistics.
"""

from typing import Protocol

from sudoku.domain.entities.game import Game
from sudoku.domain.entities.statistics import Statistics


class GameRepository(Protocol):
    """Protocol for persisting and retrieving games.

    Implementations should handle storage and retrieval of game instances,
    allowing games to be saved and loaded.
    """

    def save(self, game: Game) -> None:
        """Save a game instance.

        Args:
            game: The game to save.

        Raises:
            IOError: If unable to save the game.
        """
        ...

    def load(self, game_id: str) -> Game | None:
        """Load a game instance by ID.

        Args:
            game_id: The unique identifier of the game to load.

        Returns:
            The loaded Game instance or None if not found.

        Raises:
            IOError: If unable to load the game.
        """
        ...

    def delete(self, game_id: str) -> bool:
        """Delete a game instance.

        Args:
            game_id: The unique identifier of the game to delete.

        Returns:
            True if the game was deleted, False if not found.

        Raises:
            IOError: If unable to delete the game.
        """
        ...

    def list_saved_games(self, player_name: str) -> list[str]:
        """List all saved games for a player.

        Args:
            player_name: The name of the player.

        Returns:
            List of game IDs for the player's saved games.

        Raises:
            IOError: If unable to list games.
        """
        ...


class StatisticsRepository(Protocol):
    """Protocol for persisting and retrieving player statistics.

    Implementations should handle storage and retrieval of player statistics,
    aggregating data across multiple game sessions.
    """

    def save(self, statistics: Statistics) -> None:
        """Save player statistics.

        Args:
            statistics: The statistics to save.

        Raises:
            IOError: If unable to save the statistics.
        """
        ...

    def load(self, player_name: str) -> Statistics | None:
        """Load statistics for a player.

        Args:
            player_name: The name of the player.

        Returns:
            The Statistics instance or None if not found.

        Raises:
            IOError: If unable to load the statistics.
        """
        ...

    def delete(self, player_name: str) -> bool:
        """Delete statistics for a player.

        Args:
            player_name: The name of the player.

        Returns:
            True if statistics were deleted, False if not found.

        Raises:
            IOError: If unable to delete the statistics.
        """
        ...

    def list_all_players(self) -> list[str]:
        """List all players with saved statistics.

        Returns:
            List of player names.

        Raises:
            IOError: If unable to list players.
        """
        ...
