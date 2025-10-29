"""Entities for the Sudoku domain.

This module exports all entities used in the domain layer.
Entities are objects with identity that can change over time.
"""

from .board import Board
from .cell import Cell
from .game import Game, GameState
from .player import Player
from .statistics import DifficultyStats, Statistics


__all__ = [
    "Board",
    "Cell",
    "DifficultyStats",
    "Game",
    "GameState",
    "Player",
    "Statistics",
]
