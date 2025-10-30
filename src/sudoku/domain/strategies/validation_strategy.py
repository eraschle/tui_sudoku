"""Validation strategy protocol for Sudoku games.

This module defines the validation strategy interface following
the Strategy Pattern and Open/Closed Principle.
"""

from __future__ import annotations

from typing import Protocol

from sudoku.domain.entities.board import Board
from sudoku.domain.value_objects.position import Position


class ValidationStrategy(Protocol):
    """Protocol for validation strategies.

    Implementations can provide different validation modes:
    - Strict: Full Sudoku rule validation
    - Relaxed: Partial validation (e.g., box-only)
    - None: No validation (practice mode)
    """

    def validate_move(
        self, board: Board, position: Position, value: int
    ) -> bool:
        """Validate if a move is allowed according to this strategy.

        Args:
            board: The game board.
            position: Position where move will be made.
            value: Value to place (1-9).

        Returns:
            bool: True if move is valid according to this strategy.
        """
        ...
