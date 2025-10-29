"""Input handling module for Sudoku TUI.

This module provides keyboard input handling, including key mappings
and input processing for the Sudoku game interface.
"""

from .key_mappings import (
    ARROW_NAVIGATION_MAP,
    GAME_ACTION_MAP,
    QWERTZ_NUMBER_MAP,
    STANDARD_NUMBER_MAP,
    VIM_NAVIGATION_MAP,
    GameAction,
    KeyMapper,
    NavigationKey,
    format_key_help,
)


__all__ = [
    "ARROW_NAVIGATION_MAP",
    "GAME_ACTION_MAP",
    "QWERTZ_NUMBER_MAP",
    "STANDARD_NUMBER_MAP",
    "VIM_NAVIGATION_MAP",
    "GameAction",
    "KeyMapper",
    "NavigationKey",
    "format_key_help",
]
