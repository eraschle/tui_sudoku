"""Use case for updating player statistics after game completion.

This module implements the business logic for persisting game results
and updating player statistics.
"""

from __future__ import annotations

from sudoku.infrastructure.persistence.statistics_repository import StatisticsRepository


class UpdateStatisticsUseCase:
    """Use case for updating player statistics after a game.

    This use case handles the persistence of game results by updating
    the player's statistics in the repository. It follows the Single
    Responsibility Principle by focusing solely on statistics updates.

    The use case delegates the actual persistence to the repository.
    """

    def __init__(self, repository: StatisticsRepository) -> None:
        """Initialize the use case with a statistics repository.

        Args:
            repository: The repository for persisting statistics.
        """
        self._repository = repository

    def execute(
        self, player_name: str, difficulty: str, won: bool, time_seconds: float
    ) -> None:
        """Update statistics after a game completion.

        Args:
            player_name: The name of the player.
            difficulty: The difficulty level.
            won: Whether the game was won (correctly solved).
            time_seconds: The time taken to complete the game in seconds.

        Raises:
            ValueError: If any parameter is invalid.
        """
        self._validate_input(player_name, difficulty, time_seconds)

        self._repository.update_statistics(
            player_name=player_name,
            difficulty=difficulty,
            won=won,
            time_taken=time_seconds,
        )

    def _validate_input(
        self, player_name: str, difficulty: str, time_seconds: float
    ) -> None:
        """Validate input parameters.

        Args:
            player_name: The name of the player.
            difficulty: The difficulty level.
            time_seconds: The time taken in seconds.

        Raises:
            ValueError: If any parameter is invalid.
        """
        if not player_name or not player_name.strip():
            msg = "Player name cannot be empty"
            raise ValueError(msg)

        valid_difficulties = {"easy", "medium", "hard"}
        if difficulty.lower() not in valid_difficulties:
            msg = (
                f"Invalid difficulty '{difficulty}'. "
                f"Must be one of: {', '.join(valid_difficulties)}"
            )
            raise ValueError(msg)

        if time_seconds < 0:
            msg = "Time taken cannot be negative"
            raise ValueError(msg)
