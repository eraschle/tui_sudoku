"""Unit tests for the StatisticsRepository.

This module tests the statistics persistence layer including
saving and retrieving player statistics.
"""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from sudoku.infrastructure.persistence.statistics_repository import (
    StatisticsRepository,
)


@pytest.fixture
def temp_stats_file() -> Generator[Path, None, None]:
    """Create a temporary statistics file for testing.

    Returns:
        Path to temporary file that will be cleaned up after test.
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def repository(temp_stats_file: Path) -> StatisticsRepository:
    """Create a StatisticsRepository with temporary file.

    Args:
        temp_stats_file: Temporary file path fixture.

    Returns:
        StatisticsRepository instance using temp file.
    """
    return StatisticsRepository(temp_stats_file)


class TestStatisticsRepositoryCreation:
    """Test repository initialization."""

    def test_create_repository_with_default_path(self) -> None:
        """Test creating repository with default path."""
        repo = StatisticsRepository()

        assert repo._stats_file == StatisticsRepository.DEFAULT_STATS_FILE

    def test_create_repository_with_custom_path(self, temp_stats_file: Path) -> None:
        """Test creating repository with custom path."""
        repo = StatisticsRepository(temp_stats_file)

        assert repo._stats_file == temp_stats_file

    def test_repository_creates_file_if_not_exists(self, temp_stats_file: Path) -> None:
        """Test that repository creates file if it doesn't exist."""
        if temp_stats_file.exists():
            temp_stats_file.unlink()

        StatisticsRepository(temp_stats_file)

        assert temp_stats_file.exists()

    def test_repository_creates_directory_if_not_exists(self) -> None:
        """Test that repository creates directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            stats_path = Path(temp_dir) / "new_dir" / "stats.json"

            StatisticsRepository(stats_path)

            assert stats_path.parent.exists()
            assert stats_path.exists()


class TestStatisticsRepositoryGetStatistics:
    """Test retrieving statistics."""

    def test_get_statistics_for_new_player(self, repository: StatisticsRepository) -> None:
        """Test getting statistics for player with no history."""
        stats = repository.get_statistics("NewPlayer", "easy")

        assert stats["games_played"] == 0
        assert stats["games_won"] == 0
        assert stats["total_time"] == 0.0

    def test_get_statistics_for_existing_player(self, repository: StatisticsRepository) -> None:
        """Test getting statistics for player with history."""
        # Add some statistics
        repository.update_statistics("Player1", "easy", won=True, time_taken=120.0)

        stats = repository.get_statistics("Player1", "easy")

        assert stats["games_played"] == 1
        assert stats["games_won"] == 1
        assert stats["total_time"] == 120.0

    def test_get_statistics_different_difficulties(self, repository: StatisticsRepository) -> None:
        """Test that statistics are separate for different difficulties."""
        repository.update_statistics("Player1", "easy", won=True, time_taken=100.0)
        repository.update_statistics("Player1", "hard", won=True, time_taken=200.0)

        easy_stats = repository.get_statistics("Player1", "easy")
        hard_stats = repository.get_statistics("Player1", "hard")

        assert easy_stats["total_time"] == 100.0
        assert hard_stats["total_time"] == 200.0


class TestStatisticsRepositoryUpdateStatistics:
    """Test updating statistics."""

    def test_update_statistics_increments_games_played(
        self, repository: StatisticsRepository
    ) -> None:
        """Test that updating increments games played."""
        repository.update_statistics("Player1", "easy", won=True, time_taken=100.0)

        stats = repository.get_statistics("Player1", "easy")

        assert stats["games_played"] == 1

    def test_update_statistics_increments_games_won(self, repository: StatisticsRepository) -> None:
        """Test that updating with won=True increments games won."""
        repository.update_statistics("Player1", "easy", won=True, time_taken=100.0)

        stats = repository.get_statistics("Player1", "easy")

        assert stats["games_won"] == 1

    def test_update_statistics_does_not_increment_won_on_loss(
        self, repository: StatisticsRepository
    ) -> None:
        """Test that updating with won=False doesn't increment wins."""
        repository.update_statistics("Player1", "easy", won=False, time_taken=100.0)

        stats = repository.get_statistics("Player1", "easy")

        assert stats["games_played"] == 1
        assert stats["games_won"] == 0

    def test_update_statistics_accumulates_time(self, repository: StatisticsRepository) -> None:
        """Test that time is accumulated across games."""
        repository.update_statistics("Player1", "easy", won=True, time_taken=100.0)
        repository.update_statistics("Player1", "easy", won=True, time_taken=150.0)

        stats = repository.get_statistics("Player1", "easy")

        assert stats["total_time"] == 250.0

    def test_update_statistics_multiple_games(self, repository: StatisticsRepository) -> None:
        """Test updating statistics for multiple games."""
        repository.update_statistics("Player1", "easy", won=True, time_taken=100.0)
        repository.update_statistics("Player1", "easy", won=False, time_taken=50.0)
        repository.update_statistics("Player1", "easy", won=True, time_taken=75.0)

        stats = repository.get_statistics("Player1", "easy")

        assert stats["games_played"] == 3
        assert stats["games_won"] == 2
        assert stats["total_time"] == 225.0

    def test_update_statistics_negative_time_raises_error(
        self, repository: StatisticsRepository
    ) -> None:
        """Test that negative time raises ValueError."""
        with pytest.raises(ValueError, match="must be non-negative"):
            repository.update_statistics("Player1", "easy", won=True, time_taken=-10.0)


class TestStatisticsRepositoryGetAllStatistics:
    """Test retrieving all statistics for a player."""

    def test_get_all_statistics_for_new_player(self, repository: StatisticsRepository) -> None:
        """Test getting all statistics for player with no history."""
        all_stats = repository.get_all_statistics("NewPlayer")

        assert all_stats == {}

    def test_get_all_statistics_multiple_difficulties(
        self, repository: StatisticsRepository
    ) -> None:
        """Test getting all statistics across difficulties."""
        repository.update_statistics("Player1", "easy", won=True, time_taken=100.0)
        repository.update_statistics("Player1", "medium", won=True, time_taken=200.0)
        repository.update_statistics("Player1", "hard", won=False, time_taken=300.0)

        all_stats = repository.get_all_statistics("Player1")

        assert "easy" in all_stats
        assert "medium" in all_stats
        assert "hard" in all_stats
        assert all_stats["easy"]["games_won"] == 1
        assert all_stats["hard"]["games_won"] == 0


class TestStatisticsRepositoryDeleteStatistics:
    """Test deleting player statistics."""

    def test_delete_existing_player(self, repository: StatisticsRepository) -> None:
        """Test deleting statistics for existing player."""
        repository.update_statistics("Player1", "easy", won=True, time_taken=100.0)

        result = repository.delete_player_statistics("Player1")

        assert result is True
        stats = repository.get_statistics("Player1", "easy")
        assert stats["games_played"] == 0

    def test_delete_non_existing_player(self, repository: StatisticsRepository) -> None:
        """Test deleting statistics for non-existing player."""
        result = repository.delete_player_statistics("NonExistent")

        assert result is False


class TestStatisticsRepositoryGetAllPlayers:
    """Test listing all players."""

    def test_get_all_players_empty_repository(self, repository: StatisticsRepository) -> None:
        """Test getting all players from empty repository."""
        players = repository.get_all_players()

        assert players == []

    def test_get_all_players_with_statistics(self, repository: StatisticsRepository) -> None:
        """Test getting all players after adding statistics."""
        repository.update_statistics("Player1", "easy", won=True, time_taken=100.0)
        repository.update_statistics("Player2", "medium", won=True, time_taken=200.0)
        repository.update_statistics("Player3", "hard", won=False, time_taken=300.0)

        players = repository.get_all_players()

        assert len(players) == 3
        assert "Player1" in players
        assert "Player2" in players
        assert "Player3" in players


class TestStatisticsRepositoryPersistence:
    """Test data persistence across repository instances."""

    def test_statistics_persist_across_instances(self, temp_stats_file: Path) -> None:
        """Test that statistics persist when creating new repository instance."""
        # Create first repository and add data
        repo1 = StatisticsRepository(temp_stats_file)
        repo1.update_statistics("Player1", "easy", won=True, time_taken=100.0)

        # Create second repository and check data
        repo2 = StatisticsRepository(temp_stats_file)
        stats = repo2.get_statistics("Player1", "easy")

        assert stats["games_played"] == 1
        assert stats["total_time"] == 100.0

    def test_file_contains_valid_json(
        self, repository: StatisticsRepository, temp_stats_file: Path
    ) -> None:
        """Test that statistics file contains valid JSON."""
        repository.update_statistics("Player1", "easy", won=True, time_taken=100.0)

        with temp_stats_file.open() as f:
            data = json.load(f)

        assert "Player1" in data
        assert "easy" in data["Player1"]


class TestStatisticsRepositoryErrorHandling:
    """Test error handling scenarios."""

    def test_corrupted_json_file_raises_error(self, temp_stats_file: Path) -> None:
        """Test that corrupted JSON file raises ValueError."""
        # Write invalid JSON
        with open(temp_stats_file, "w") as f:
            f.write("{ invalid json")

        repo = StatisticsRepository(temp_stats_file)

        with pytest.raises(ValueError, match="invalid JSON"):
            repo.get_statistics("Player1", "easy")
