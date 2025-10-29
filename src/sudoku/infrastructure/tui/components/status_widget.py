"""Status bar widget for displaying game information.

This module provides a status bar widget showing player name, difficulty,
timer, and other game status information.
"""

from datetime import timedelta

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual.widget import Widget


class StatusWidget(Widget):
    """Widget for displaying game status information.

    This widget shows:
    - Player name
    - Difficulty level
    - Elapsed time
    - Game state (in progress, paused, won, etc.)
    - Optional messages

    Attributes:
        player_name: The name of the current player.
        difficulty: The difficulty level.
        elapsed_time: Time elapsed in the current game.
        game_state: Current state of the game.
        message: Optional status message to display.
    """

    DEFAULT_CSS = """
    StatusWidget {
        background: $panel;
        height: 3;
        width: 100%;
        border: solid $primary;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        player_name: str = "",
        difficulty: str = "",
        elapsed_time: timedelta = timedelta(),
        game_state: str = "",
        message: str = "",
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize the status widget.

        Args:
            player_name: The name of the current player.
            difficulty: The difficulty level.
            elapsed_time: Time elapsed in the current game.
            game_state: Current state of the game.
            message: Optional status message to display.
            name: The name of the widget.
            id: The ID of the widget.
        """
        super().__init__(name=name, id=id)
        self._player_name = player_name
        self._difficulty = difficulty
        self._elapsed_time = elapsed_time
        self._game_state = game_state
        self._message = message

    def update_status(
        self,
        player_name: str | None = None,
        difficulty: str | None = None,
        elapsed_time: timedelta | None = None,
        game_state: str | None = None,
        message: str | None = None,
    ) -> None:
        """Update status information.

        Args:
            player_name: The name of the current player.
            difficulty: The difficulty level.
            elapsed_time: Time elapsed in the current game.
            game_state: Current state of the game.
            message: Optional status message to display.
        """
        if player_name is not None:
            self._player_name = player_name
        if difficulty is not None:
            self._difficulty = difficulty
        if elapsed_time is not None:
            self._elapsed_time = elapsed_time
        if game_state is not None:
            self._game_state = game_state
        if message is not None:
            self._message = message

        self.refresh()

    def set_message(self, message: str) -> None:
        """Set a status message.

        Args:
            message: The message to display.
        """
        self._message = message
        self.refresh()

    def clear_message(self) -> None:
        """Clear the status message."""
        self._message = ""
        self.refresh()

    def render(self) -> RenderableType:
        """Render the status widget.

        Returns:
            A Rich renderable representing the status bar.
        """
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="center", ratio=1)
        table.add_column(justify="right", ratio=1)

        # Left: Player and difficulty
        left_text = self._format_player_info()

        # Center: Timer
        center_text = self._format_timer()

        # Right: Game state
        right_text = self._format_game_state()

        table.add_row(left_text, center_text, right_text)

        # Add message row if there's a message
        if self._message:
            message_text = Text(self._message, style="bold yellow")
            table.add_row(message_text)

        return table

    def _format_player_info(self) -> Text:
        """Format player name and difficulty.

        Returns:
            Formatted Text with player info.
        """
        if not self._player_name:
            return Text("")

        text = Text()
        text.append("Player: ", style="dim")
        text.append(self._player_name, style="bold cyan")

        if self._difficulty:
            text.append(" | ", style="dim")
            text.append("Difficulty: ", style="dim")
            text.append(
                self._difficulty.capitalize(),
                style=self._get_difficulty_style(),
            )

        return text

    def _format_timer(self) -> Text:
        """Format elapsed time.

        Returns:
            Formatted Text with timer.
        """
        if self._elapsed_time.total_seconds() == 0:
            return Text("")

        formatted_time = self._format_timedelta(self._elapsed_time)
        text = Text()
        text.append("Time: ", style="dim")
        text.append(formatted_time, style="bold white")

        return text

    def _format_game_state(self) -> Text:
        """Format game state.

        Returns:
            Formatted Text with game state.
        """
        if not self._game_state:
            return Text("")

        style = self._get_game_state_style()
        return Text(self._game_state, style=style)

    def _format_timedelta(self, td: timedelta) -> str:
        """Format a timedelta as HH:MM:SS.

        Args:
            td: The timedelta to format.

        Returns:
            Formatted time string.
        """
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def _get_difficulty_style(self) -> str:
        """Get the style for difficulty display.

        Returns:
            Rich style string based on difficulty.
        """
        difficulty_lower = self._difficulty.lower()

        if difficulty_lower == "easy":
            return "green"
        if difficulty_lower == "medium":
            return "yellow"
        if difficulty_lower == "hard":
            return "red"

        return "white"

    def _get_game_state_style(self) -> str:
        """Get the style for game state display.

        Returns:
            Rich style string based on game state.
        """
        state_lower = self._game_state.lower()

        if "won" in state_lower or "complete" in state_lower:
            return "bold green"
        if "paused" in state_lower:
            return "yellow"
        if "progress" in state_lower:
            return "cyan"
        if "lost" in state_lower:
            return "red"

        return "white"

    @property
    def player_name(self) -> str:
        """Get the current player name.

        Returns:
            The player name.
        """
        return self._player_name

    @property
    def difficulty(self) -> str:
        """Get the current difficulty.

        Returns:
            The difficulty level.
        """
        return self._difficulty

    @property
    def elapsed_time(self) -> timedelta:
        """Get the elapsed time.

        Returns:
            The elapsed time.
        """
        return self._elapsed_time

    @property
    def game_state(self) -> str:
        """Get the current game state.

        Returns:
            The game state.
        """
        return self._game_state

    @property
    def message(self) -> str:
        """Get the current message.

        Returns:
            The status message.
        """
        return self._message


class CompactStatusWidget(StatusWidget):
    """Compact variant of the status widget with minimal height.

    This variant is useful for maximizing board display space.
    """

    DEFAULT_CSS = """
    CompactStatusWidget {
        background: $panel;
        height: 1;
        width: 100%;
        padding: 0 1;
    }
    """

    def render(self) -> RenderableType:
        """Render the compact status widget.

        Returns:
            A Rich renderable representing the compact status bar.
        """
        text = Text()

        # Player name
        if self._player_name:
            text.append(self._player_name, style="bold cyan")
            text.append(" | ", style="dim")

        # Difficulty
        if self._difficulty:
            text.append(
                self._difficulty.capitalize(),
                style=self._get_difficulty_style(),
            )
            text.append(" | ", style="dim")

        # Timer
        if self._elapsed_time.total_seconds() > 0:
            formatted_time = self._format_timedelta(self._elapsed_time)
            text.append(formatted_time, style="bold white")
            text.append(" | ", style="dim")

        # Game state
        if self._game_state:
            text.append(self._game_state, style=self._get_game_state_style())

        # Message (overwrites other info if present)
        if self._message:
            return Text(self._message, style="bold yellow")

        return text
