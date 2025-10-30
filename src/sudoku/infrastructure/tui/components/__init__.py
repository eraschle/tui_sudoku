"""UI components for Sudoku TUI.

This module provides reusable UI components for the Sudoku game interface,
including board display, status bars, and other widgets.
"""

from .board_widget import BoardWidget
from .status_widget import CompactStatusWidget, StatusWidget


__all__ = [
    "BoardWidget",
    "CompactStatusWidget",
    "StatusWidget",
]
