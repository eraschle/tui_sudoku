"""Use case for retrieving player statistics.

This module implements the business logic for fetching and presenting
player statistics from the repository.
"""

from __future__ import annotations

from sudoku.application.dto import AllStatisticsDTO
from sudoku.infrastructure.persistence.statistics_repository import StatisticsRepository


class GetStatisticsUseCase:
    """Use case for retrieving player statistics.

    This use case handles the retrieval of statistics for a specific player,
    either for a particular difficulty level or across all difficulties.
    It follows the Single Responsibility Principle by focusing solely on
    statistics retrieval.

    Statistics are fetched from the repository and converted to DTOs for
    presentation layer consumption.
    """

    def __init__(self, repository: StatisticsRepository) -> None:
        """Initialize the use case with a statistics repository.

        Args:
            repository: The repository for accessing statistics data.
        """
        self._repository = repository

    def execute(self, player_name: str) -> AllStatisticsDTO:
        """Retrieve all statistics for a specific player across all difficulties.

        Args:
            player_name: The name of the player.

        Returns:
            AllStatisticsDTO: All statistics for the player.

        Raises:
            ValueError: If player_name is empty.
        """
        self._validate_player_name(player_name)

        all_stats = self._repository.get_all_statistics(player_name)
        return AllStatisticsDTO.from_dict(player_name, all_stats)

    def _validate_player_name(self, player_name: str) -> None:
        """Validate the player name.

        Args:
            player_name: The name of the player.

        Raises:
            ValueError: If player_name is empty or contains only whitespace.
        """
        if not player_name or not player_name.strip():
            msg = "Player name cannot be empty"
            raise ValueError(msg)
