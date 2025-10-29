"""Terminal User Interface (TUI) for Sudoku application.

This module provides a complete TUI implementation using the Textual library,
including screens, widgets, and input handling for an interactive Sudoku game.
"""

from .app import DemoSudokuApp, SudokuApp, run_app


__all__ = [
    "DemoSudokuApp",
    "SudokuApp",
    "run_app",
]
