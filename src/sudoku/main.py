"""Main entry point for the Sudoku TUI application.

This module initializes all dependencies and starts the Textual application
following dependency injection principles and Clean Architecture.
"""

from __future__ import annotations

import sys
from typing import NoReturn

from sudoku.application.use_cases.check_completion import CheckCompletionUseCase
from sudoku.application.use_cases.get_statistics import GetStatisticsUseCase
from sudoku.application.use_cases.make_move import MakeMoveUseCase
from sudoku.application.use_cases.start_new_game import StartNewGameUseCase
from sudoku.application.use_cases.update_statistics import UpdateStatisticsUseCase
from sudoku.infrastructure.generators.backtracking_generator import (
    BacktrackingGenerator,
)
from sudoku.infrastructure.persistence.statistics_repository import (
    StatisticsRepository,
)
from sudoku.infrastructure.solvers.backtracking_solver import BacktrackingSolver
from sudoku.infrastructure.tui.app import run_app
from sudoku.infrastructure.validators.sudoku_validator import SudokuValidator
from sudoku.presentation.controllers.app_controller import AppController


def create_app_controller() -> AppController:
    """Create and configure the application controller with all dependencies.

    This factory function follows the Dependency Injection principle by
    creating all dependencies and injecting them into the controller and
    use cases.

    Returns:
        Configured AppController instance with all dependencies.
    """
    # Initialize infrastructure dependencies
    generator = BacktrackingGenerator()
    validator = SudokuValidator()
    repository = StatisticsRepository()

    # Initialize use cases with dependencies
    start_new_game_use_case = StartNewGameUseCase(
        generator=generator,
        validator=validator,
    )
    make_move_use_case = MakeMoveUseCase(validator=validator)
    check_completion_use_case = CheckCompletionUseCase(validator=validator)
    get_statistics_use_case = GetStatisticsUseCase(repository=repository)
    update_statistics_use_case = UpdateStatisticsUseCase(repository=repository)

    # Create controller with injected use cases
    return AppController(
        start_game_use_case=start_new_game_use_case,
        make_move_use_case=make_move_use_case,
        check_completion_use_case=check_completion_use_case,
        get_statistics_use_case=get_statistics_use_case,
        update_statistics_use_case=update_statistics_use_case,
    )


def main() -> NoReturn:
    """Main entry point for the Sudoku TUI application.

    This function creates the application controller with all dependencies
    and runs the TUI application. It's the entry point defined in
    pyproject.toml for the 'sudoku' command.

    Exits:
        0 on normal termination
        1 on error
    """
    try:
        controller = create_app_controller()
        run_app(controller)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
