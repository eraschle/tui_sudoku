"""Validation strategies for Sudoku games."""

from sudoku.domain.strategies.validation_strategies import (
    NoValidation,
    RelaxedValidation,
    StrictSudokuValidation,
)
from sudoku.domain.strategies.validation_strategy import ValidationStrategy
from sudoku.infrastructure.validators.sudoku_validator import create_sudoku_validator


def create_validation_strategy(mode: str) -> ValidationStrategy:
    """Factory function to create validation strategies.

    Args:
        mode: Validation mode ('strict', 'relaxed', 'none').

    Returns:
        ValidationStrategy: Appropriate strategy for the mode.

    Raises:
        ValueError: If mode is unknown.
    """
    if mode == "strict":
        validator = create_sudoku_validator()
        return StrictSudokuValidation(validator)
    elif mode == "relaxed":
        return RelaxedValidation()
    elif mode == "none":
        return NoValidation()
    else:
        raise ValueError(f"Unknown validation mode: {mode}")


__all__ = [
    "ValidationStrategy",
    "StrictSudokuValidation",
    "NoValidation",
    "RelaxedValidation",
    "create_validation_strategy",
]
