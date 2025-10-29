"""Data Transfer Object for player statistics.

This module provides DTOs for transferring statistics information
between the application layer and presentation layer.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StatisticsDTO:
    """Data Transfer Object representing player statistics for a difficulty level.

    This immutable object encapsulates statistics for a specific player
    and difficulty level.

    Attributes:
        player_name: The name of the player.
        difficulty: The difficulty level.
        games_played: The total number of games played.
        games_won: The total number of games won.
        total_time: The cumulative time spent on games, in seconds.
        win_rate: The percentage of games won (0-100).
        average_time: The average time per game, in seconds.
    """

    player_name: str
    difficulty: str
    games_played: int
    games_won: int
    total_time: float

    @property
    def win_rate(self) -> float:
        """Calculate the win rate as a percentage.

        Returns:
            float: The win rate (0-100), or 0 if no games played.
        """
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

    @property
    def average_time(self) -> float:
        """Calculate the average time per game.

        Returns:
            float: The average time in seconds, or 0 if no games played.
        """
        if self.games_played == 0:
            return 0.0
        return self.total_time / self.games_played

    @classmethod
    def from_dict(
        cls,
        player_name: str,
        difficulty: str,
        stats: dict[str, int | float],
    ) -> "StatisticsDTO":
        """Create a StatisticsDTO from a dictionary.

        Args:
            player_name: The name of the player.
            difficulty: The difficulty level.
            stats: A dictionary containing statistics data with keys:
                - games_played: int
                - games_won: int
                - total_time: float

        Returns:
            StatisticsDTO: A new instance with the provided statistics.
        """
        return cls(
            player_name=player_name,
            difficulty=difficulty,
            games_played=int(stats.get("games_played", 0)),
            games_won=int(stats.get("games_won", 0)),
            total_time=stats.get("total_time", 0.0),
        )


@dataclass(frozen=True)
class AllStatisticsDTO:
    """Data Transfer Object representing all statistics for a player.

    This immutable object encapsulates statistics across all difficulty levels.

    Attributes:
        player_name: The name of the player.
        statistics: A mapping of difficulty levels to their statistics.
    """

    player_name: str
    statistics: dict[str, StatisticsDTO]

    @classmethod
    def from_dict(
        cls,
        player_name: str,
        all_stats: dict[str, dict[str, int | float]],
    ) -> "AllStatisticsDTO":
        """Create an AllStatisticsDTO from a dictionary.

        Args:
            player_name: The name of the player.
            all_stats: A dictionary mapping difficulty levels to their statistics.

        Returns:
            AllStatisticsDTO: A new instance with all statistics.
        """
        statistics = {
            difficulty: StatisticsDTO.from_dict(player_name, difficulty, stats)
            for difficulty, stats in all_stats.items()
        }
        return cls(player_name=player_name, statistics=statistics)

    def get_total_games_played(self) -> int:
        """Calculate the total number of games played across all difficulties.

        Returns:
            int: The total number of games played.
        """
        return sum(stats.games_played for stats in self.statistics.values())

    def get_total_games_won(self) -> int:
        """Calculate the total number of games won across all difficulties.

        Returns:
            int: The total number of games won.
        """
        return sum(stats.games_won for stats in self.statistics.values())

    def get_overall_win_rate(self) -> float:
        """Calculate the overall win rate across all difficulties.

        Returns:
            float: The overall win rate (0-100), or 0 if no games played.
        """
        total_played = self.get_total_games_played()
        if total_played == 0:
            return 0.0
        return (self.get_total_games_won() / total_played) * 100
