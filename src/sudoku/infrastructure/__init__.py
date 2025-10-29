"""Infrastructure layer for Sudoku application.

This package contains concrete implementations of domain protocols:
- Generators: Board generation implementations
- Solvers: Board solving implementations
- Validators: Board validation implementations
- Persistence: Data storage implementations
"""

from sudoku.infrastructure.generators.backtracking_generator import (
    BacktrackingGenerator,
    create_backtracking_generator,
)
from sudoku.infrastructure.persistence.statistics_repository import (
    StatisticsRepository,
)
from sudoku.infrastructure.solvers.backtracking_solver import (
    BacktrackingSolver,
    create_backtracking_solver,
)
from sudoku.infrastructure.validators.sudoku_validator import (
    SudokuValidator,
    create_sudoku_validator,
)


__all__ = [
    # Generators
    "BacktrackingGenerator",
    # Solvers
    "BacktrackingSolver",
    # Persistence
    "StatisticsRepository",
    # Validators
    "SudokuValidator",
    "create_backtracking_generator",
    "create_backtracking_solver",
    "create_sudoku_validator",
]
