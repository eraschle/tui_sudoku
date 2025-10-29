"""Board solvers package.

This package contains implementations for solving Sudoku boards
and verifying solution uniqueness.
"""

from sudoku.infrastructure.solvers.backtracking_solver import (
    BacktrackingSolver,
    BoardSolver,
    create_backtracking_solver,
)


__all__ = [
    "BacktrackingSolver",
    "BoardSolver",
    "create_backtracking_solver",
]
