"""Player entity representing a game player.

This module provides the Player entity which represents a user playing
the Sudoku game.
"""

from dataclasses import dataclass


@dataclass
class Player:
    """Entity representing a player in the Sudoku game.

    Attributes:
        name: The player's name.
    """

    name: str

    def __post_init__(self) -> None:
        """Validate player data after initialization.

        Raises:
            ValueError: If name is empty or contains only whitespace.
        """
        if not self.name or not self.name.strip():
            msg = "Player name cannot be empty"
            raise ValueError(msg)

        self.name = self.name.strip()

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns:
            The player's name.
        """
        return self.name

    def __eq__(self, other: object) -> bool:
        """Check equality based on player name.

        Args:
            other: Object to compare with.

        Returns:
            True if both players have the same name, False otherwise.
        """
        if not isinstance(other, Player):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        """Return hash based on player name.

        Returns:
            Hash value of the player's name.
        """
        return hash(self.name)
