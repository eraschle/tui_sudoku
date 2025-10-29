"""Use cases for the Sudoku application.

This module exports all use cases that implement the business logic
of the application. Each use case follows the Single Responsibility
Principle and uses dependency injection for loose coupling.
"""

from .check_completion import CheckCompletionUseCase
from .get_statistics import GetStatisticsUseCase
from .make_move import MakeMoveUseCase
from .start_new_game import StartNewGameUseCase
from .update_statistics import UpdateStatisticsUseCase


__all__ = [
    "CheckCompletionUseCase",
    "GetStatisticsUseCase",
    "MakeMoveUseCase",
    "StartNewGameUseCase",
    "UpdateStatisticsUseCase",
]
