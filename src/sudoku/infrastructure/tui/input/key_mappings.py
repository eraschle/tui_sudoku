"""Key mapping configuration for Sudoku TUI input handling.

This module defines the keyboard mappings for Sudoku game interaction,
including QWERTZ number input and vim-style navigation.
"""

from enum import Enum, auto


class NavigationKey(Enum):
    """Enumeration of navigation actions."""

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class GameAction(Enum):
    """Enumeration of game actions."""

    NEW_GAME = auto()
    QUIT = auto()
    CLEAR_CELL = auto()
    SHOW_STATISTICS = auto()
    BACK_TO_MENU = auto()


# QWERTZ keyboard layout mapping to numbers 1-9
QWERTZ_NUMBER_MAP: dict[str, int] = {
    "q": 1,
    "w": 2,
    "e": 3,
    "r": 4,
    "t": 5,
    "z": 6,
    "u": 7,
    "i": 8,
    "o": 9,
}

# Vim-style navigation mapping
VIM_NAVIGATION_MAP: dict[str, NavigationKey] = {
    "h": NavigationKey.LEFT,
    "j": NavigationKey.DOWN,
    "k": NavigationKey.UP,
    "l": NavigationKey.RIGHT,
}

# Arrow key navigation mapping
ARROW_NAVIGATION_MAP: dict[str, NavigationKey] = {
    "up": NavigationKey.UP,
    "down": NavigationKey.DOWN,
    "left": NavigationKey.LEFT,
    "right": NavigationKey.RIGHT,
}

# Game action key mapping
GAME_ACTION_MAP: dict[str, GameAction] = {
    "n": GameAction.NEW_GAME,
    "q": GameAction.QUIT,
    "x": GameAction.CLEAR_CELL,
    "delete": GameAction.CLEAR_CELL,
    "s": GameAction.SHOW_STATISTICS,
    "escape": GameAction.BACK_TO_MENU,
}

# Standard number keys mapping (1-9)
STANDARD_NUMBER_MAP: dict[str, int] = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
}


class KeyMapper:
    """Key mapper for translating keyboard input to game actions and values.

    This class provides a unified interface for mapping various keyboard
    inputs to game actions, numbers, and navigation commands. It supports
    multiple input styles (QWERTZ, standard numbers, vim navigation, arrows).

    Following the Single Responsibility Principle, this class focuses solely
    on key mapping logic.
    """

    def __init__(
        self,
        enable_qwertz: bool = True,
        enable_vim_navigation: bool = True,
    ) -> None:
        """Initialize the key mapper with configuration options.

        Args:
            enable_qwertz: Whether to enable QWERTZ number input (q-o for 1-9).
            enable_vim_navigation: Whether to enable vim-style navigation (hjkl).
        """
        self._enable_qwertz = enable_qwertz
        self._enable_vim_navigation = enable_vim_navigation

    def get_number(self, key: str) -> int | None:
        """Map a key to a number value (1-9).

        Args:
            key: The key that was pressed.

        Returns:
            The corresponding number (1-9), or None if not a number key.
        """
        # Try standard number keys first
        if key in STANDARD_NUMBER_MAP:
            return STANDARD_NUMBER_MAP[key]

        # Try QWERTZ mapping if enabled
        if self._enable_qwertz and key in QWERTZ_NUMBER_MAP:
            return QWERTZ_NUMBER_MAP[key]

        return None

    def get_navigation(self, key: str) -> NavigationKey | None:
        """Map a key to a navigation action.

        Args:
            key: The key that was pressed.

        Returns:
            The corresponding navigation action, or None if not a navigation key.
        """
        # Try vim navigation if enabled
        if self._enable_vim_navigation and key in VIM_NAVIGATION_MAP:
            return VIM_NAVIGATION_MAP[key]

        # Try arrow keys
        if key in ARROW_NAVIGATION_MAP:
            return ARROW_NAVIGATION_MAP[key]

        return None

    def get_game_action(self, key: str) -> GameAction | None:
        """Map a key to a game action.

        Note: Some keys may conflict with QWERTZ number input. The caller
        should determine context-appropriate handling (e.g., 'q' for quit
        vs. '1' in number input mode).

        Args:
            key: The key that was pressed.

        Returns:
            The corresponding game action, or None if not a game action key.
        """
        return GAME_ACTION_MAP.get(key)

    def is_number_key(self, key: str) -> bool:
        """Check if a key represents a number input.

        Args:
            key: The key to check.

        Returns:
            True if the key maps to a number, False otherwise.
        """
        return self.get_number(key) is not None

    def is_navigation_key(self, key: str) -> bool:
        """Check if a key represents a navigation action.

        Args:
            key: The key to check.

        Returns:
            True if the key maps to navigation, False otherwise.
        """
        return self.get_navigation(key) is not None

    def is_clear_key(self, key: str) -> bool:
        """Check if a key represents a clear cell action.

        Args:
            key: The key to check.

        Returns:
            True if the key is 'x' or 'delete', False otherwise.
        """
        action = self.get_game_action(key)
        return action == GameAction.CLEAR_CELL

    def get_all_number_keys(self) -> list[str]:
        """Get all keys that map to numbers.

        Returns:
            List of all number input keys.
        """
        keys = list(STANDARD_NUMBER_MAP.keys())
        if self._enable_qwertz:
            keys.extend(QWERTZ_NUMBER_MAP.keys())
        return keys

    def get_all_navigation_keys(self) -> list[str]:
        """Get all keys that map to navigation.

        Returns:
            List of all navigation keys.
        """
        keys = list(ARROW_NAVIGATION_MAP.keys())
        if self._enable_vim_navigation:
            keys.extend(VIM_NAVIGATION_MAP.keys())
        return keys


def format_key_help() -> str:
    """Generate a formatted help string for keyboard controls.

    Returns:
        Multi-line string describing all available keyboard controls.
    """
    lines = [
        "Keyboard Controls:",
        "",
        "Numbers:",
        "  q,w,e,r,t,z,u,i,o = 1-9 (QWERTZ)",
        "  1-9               = 1-9 (Standard)",
        "",
        "Navigation:",
        "  h,j,k,l           = Left, Down, Up, Right (Vim)",
        "  Arrow keys        = Navigate",
        "",
        "Actions:",
        "  n                 = New game",
        "  s                 = Show statistics",
        "  x, Delete         = Clear cell",
        "  Escape            = Back to menu",
        "  q                 = Quit",
    ]
    return "\n".join(lines)
