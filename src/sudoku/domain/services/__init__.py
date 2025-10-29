"""Domain services for the Sudoku game.

This module exports all domain services.
Domain services contain business logic that doesn't naturally fit
within a single entity or value object.
"""

from .game_rules import GameRules


__all__ = [
    "GameRules",
]
