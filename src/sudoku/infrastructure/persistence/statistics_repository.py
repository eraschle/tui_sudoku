"""File-based repository for persisting player statistics.

This module implements statistics persistence using JSON files stored
in the user's home directory.
"""

import json
from pathlib import Path
from typing import Any


class StatisticsRepository:
    """File-based repository for storing and retrieving player statistics.

    Statistics are stored in JSON format at ~/.sudoku/statistics.json.
    The structure is:
    {
        "player_name": {
            "difficulty": {
                "games_played": int,
                "games_won": int,
                "total_time": float
            }
        }
    }

    This class follows the Repository pattern and implements
    StatisticsRepositoryProtocol.
    """

    DEFAULT_STATS_DIR = Path.home() / ".sudoku"
    DEFAULT_STATS_FILE = DEFAULT_STATS_DIR / "statistics.json"

    def __init__(self, stats_file_path: Path | None = None) -> None:
        """Initialize the statistics repository.

        Args:
            stats_file_path: Optional custom path for the statistics file.
                If None, uses the default path (~/.sudoku/statistics.json).
        """
        self._stats_file = stats_file_path or self.DEFAULT_STATS_FILE
        self._ensure_stats_file_exists()

    def _ensure_stats_file_exists(self) -> None:
        """Ensure the statistics directory and file exist.

        Creates the directory and file if they don't exist, initializing
        the file with an empty JSON object.
        """
        self._stats_file.parent.mkdir(parents=True, exist_ok=True)

        if not self._stats_file.exists():
            self._write_statistics({})

    def _read_statistics(self) -> dict[str, Any]:
        """Read the statistics from the JSON file.

        Returns:
            dict[str, Any]: The complete statistics dictionary.

        Raises:
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        try:
            with self._stats_file.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as error:
            msg = f"Statistics file at {self._stats_file} contains invalid JSON"
            raise ValueError(
                msg
            ) from error

    def _write_statistics(self, statistics: dict[str, Any]) -> None:
        """Write the statistics to the JSON file.

        Args:
            statistics: The complete statistics dictionary to write.
        """
        with self._stats_file.open("w", encoding="utf-8") as file:
            json.dump(statistics, file, indent=2, ensure_ascii=False)

    def get_statistics(
        self, player_name: str, difficulty: str
    ) -> dict[str, int | float]:
        """Retrieve statistics for a specific player and difficulty.

        Args:
            player_name: The name of the player.
            difficulty: The difficulty level.

        Returns:
            dict[str, int | float]: A dictionary containing:
                - games_played: int (defaults to 0)
                - games_won: int (defaults to 0)
                - total_time: float (defaults to 0.0)
        """
        all_stats = self._read_statistics()

        player_stats = all_stats.get(player_name, {})
        difficulty_stats = player_stats.get(difficulty, {})

        return {
            "games_played": difficulty_stats.get("games_played", 0),
            "games_won": difficulty_stats.get("games_won", 0),
            "total_time": difficulty_stats.get("total_time", 0.0),
        }

    def update_statistics(
        self,
        player_name: str,
        difficulty: str,
        won: bool,
        time_taken: float,
    ) -> None:
        """Update statistics after a game is completed.

        Args:
            player_name: The name of the player.
            difficulty: The difficulty level.
            won: Whether the game was won.
            time_taken: The time taken to complete the game in seconds.

        Raises:
            ValueError: If time_taken is negative.
        """
        if time_taken < 0:
            msg = "time_taken must be non-negative"
            raise ValueError(msg)

        all_stats = self._read_statistics()

        # Ensure player exists in statistics
        if player_name not in all_stats:
            all_stats[player_name] = {}

        # Ensure difficulty exists for player
        if difficulty not in all_stats[player_name]:
            all_stats[player_name][difficulty] = {
                "games_played": 0,
                "games_won": 0,
                "total_time": 0.0,
            }

        # Update statistics
        difficulty_stats = all_stats[player_name][difficulty]
        difficulty_stats["games_played"] += 1
        if won:
            difficulty_stats["games_won"] += 1
        difficulty_stats["total_time"] += time_taken

        self._write_statistics(all_stats)

    def get_all_statistics(
        self, player_name: str
    ) -> dict[str, dict[str, int | float]]:
        """Retrieve all statistics for a specific player across all difficulties.

        Args:
            player_name: The name of the player.

        Returns:
            dict[str, dict[str, int | float]]: A dictionary mapping difficulty
                levels to their respective statistics. Returns an empty dict
                if the player has no statistics.
        """
        all_stats = self._read_statistics()
        player_stats = all_stats.get(player_name, {})

        # Ensure all difficulty stats have the correct structure
        result = {}
        for difficulty, stats in player_stats.items():
            result[difficulty] = {
                "games_played": stats.get("games_played", 0),
                "games_won": stats.get("games_won", 0),
                "total_time": stats.get("total_time", 0.0),
            }

        return result

    def delete_player_statistics(self, player_name: str) -> bool:
        """Delete all statistics for a specific player.

        Args:
            player_name: The name of the player whose statistics to delete.

        Returns:
            bool: True if statistics were deleted, False if player not found.
        """
        all_stats = self._read_statistics()

        if player_name in all_stats:
            del all_stats[player_name]
            self._write_statistics(all_stats)
            return True

        return False

    def get_all_players(self) -> list[str]:
        """Get a list of all players with statistics.

        Returns:
            list[str]: A list of player names.
        """
        all_stats = self._read_statistics()
        return list(all_stats.keys())
