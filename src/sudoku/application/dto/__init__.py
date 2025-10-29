"""Data Transfer Objects for the application layer."""

from .game_state import GameStateDTO
from .statistics_dto import AllStatisticsDTO, StatisticsDTO


__all__ = [
    "AllStatisticsDTO",
    "GameStateDTO",
    "StatisticsDTO",
]
