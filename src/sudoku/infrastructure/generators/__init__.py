"""Board generators package.

This package contains implementations for generating Sudoku boards
with varying difficulty levels.
"""

from sudoku.infrastructure.generators.backtracking_generator import (
    BacktrackingGenerator,
    BoardGenerator,
    create_backtracking_generator,
)


__all__ = [
    "BacktrackingGenerator",
    "BoardGenerator",
    "create_backtracking_generator",
]
