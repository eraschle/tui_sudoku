"""Domain protocols for dependency injection and type safety.

This module exports all protocols used in the domain layer.
Protocols define interfaces for external dependencies.
"""

from .board_generator import BoardGenerator
from .board_solver import BoardSolver
from .board_validator import BoardValidator
from .repository import GameRepository, StatisticsRepository


__all__ = [
    "BoardGenerator",
    "BoardSolver",
    "BoardValidator",
    "GameRepository",
    "StatisticsRepository",
]
