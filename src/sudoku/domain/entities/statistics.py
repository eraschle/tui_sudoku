"""Statistics entity for tracking game performance.

This module provides the Statistics entity which tracks player performance
across different difficulty levels.
"""

from dataclasses import dataclass, field
from datetime import timedelta

from sudoku.domain.value_objects.difficulty import Difficulty


@dataclass
class DifficultyStats:
    """Statistics for a specific difficulty level.

    Attributes:
        games_played: Total number of games played.
        games_won: Total number of games won.
        games_lost: Total number of games lost.
        total_time: Total time spent playing.
        best_time: Best completion time (for won games).
    """

    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    total_time: timedelta = field(default_factory=lambda: timedelta())
    best_time: timedelta | None = None

    @property
    def win_rate(self) -> float:
        """Calculate win rate as a percentage.

        Returns:
            Win rate (0-100) or 0 if no games played.
        """
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

    @property
    def average_time(self) -> timedelta | None:
        """Calculate average time per game.

        Returns:
            Average time or None if no games played.
        """
        if self.games_played == 0:
            return None
        return self.total_time / self.games_played

    def record_win(self, completion_time: timedelta) -> None:
        """Record a won game.

        Args:
            completion_time: Time taken to complete the game.
        """
        self.games_played += 1
        self.games_won += 1
        self.total_time += completion_time

        if self.best_time is None or completion_time < self.best_time:
            self.best_time = completion_time

    def record_loss(self, play_time: timedelta) -> None:
        """Record a lost game.

        Args:
            play_time: Time spent on the game before losing.
        """
        self.games_played += 1
        self.games_lost += 1
        self.total_time += play_time


class Statistics:
    """Entity representing player statistics across all difficulty levels.

    Tracks game performance metrics for each difficulty level separately.

    Attributes:
        player_name: Name of the player these statistics belong to.
    """

    def __init__(self, player_name: str) -> None:
        """Initialize statistics for a player.

        Args:
            player_name: Name of the player.

        Raises:
            ValueError: If player_name is empty.
        """
        if not player_name or not player_name.strip():
            msg = "Player name cannot be empty"
            raise ValueError(msg)

        self.player_name = player_name.strip()
        self._stats: dict[Difficulty, DifficultyStats] = {
            Difficulty.EASY: DifficultyStats(),
            Difficulty.MEDIUM: DifficultyStats(),
            Difficulty.HARD: DifficultyStats(),
        }

    def get_stats(self, difficulty: Difficulty) -> DifficultyStats:
        """Get statistics for a specific difficulty level.

        Args:
            difficulty: The difficulty level.

        Returns:
            Statistics for the specified difficulty.
        """
        return self._stats[difficulty]

    def record_win(self, difficulty: Difficulty, completion_time: timedelta) -> None:
        """Record a won game for a specific difficulty.

        Args:
            difficulty: The difficulty level.
            completion_time: Time taken to complete the game.
        """
        self._stats[difficulty].record_win(completion_time)

    def record_loss(self, difficulty: Difficulty, play_time: timedelta) -> None:
        """Record a lost game for a specific difficulty.

        Args:
            difficulty: The difficulty level.
            play_time: Time spent on the game before losing.
        """
        self._stats[difficulty].record_loss(play_time)

    @property
    def total_games_played(self) -> int:
        """Get total number of games played across all difficulties.

        Returns:
            Total number of games played.
        """
        return sum(stats.games_played for stats in self._stats.values())

    @property
    def total_games_won(self) -> int:
        """Get total number of games won across all difficulties.

        Returns:
            Total number of games won.
        """
        return sum(stats.games_won for stats in self._stats.values())

    @property
    def total_games_lost(self) -> int:
        """Get total number of games lost across all difficulties.

        Returns:
            Total number of games lost.
        """
        return sum(stats.games_lost for stats in self._stats.values())

    @property
    def overall_win_rate(self) -> float:
        """Calculate overall win rate across all difficulties.

        Returns:
            Overall win rate (0-100) or 0 if no games played.
        """
        if self.total_games_played == 0:
            return 0.0
        return (self.total_games_won / self.total_games_played) * 100

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            String representation of statistics.
        """
        return (
            f"Statistics for {self.player_name}: "
            f"{self.total_games_played} games, "
            f"{self.total_games_won} wins, "
            f"{self.overall_win_rate:.1f}% win rate"
        )
