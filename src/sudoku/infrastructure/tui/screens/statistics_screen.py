"""Statistics screen for displaying player statistics.

This module provides a screen for viewing player game statistics
across different difficulty levels.
"""

from datetime import timedelta

from rich.align import Align
from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from sudoku.application.dto.statistics_dto import AllStatisticsDTO, StatisticsDTO


class StatisticsScreen(Screen):
    """Screen for displaying player statistics.

    This screen shows:
    - Overall statistics (total games, win rate)
    - Statistics per difficulty level
    - Best times and achievements

    Attributes:
        statistics: The statistics data to display.
    """

    BINDINGS = [
        ("escape", "back", "Back to Menu"),
        ("q", "back", "Back to Menu"),
    ]

    CSS = """
    StatisticsScreen {
        align: center middle;
    }

    #stats-container {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }

    #title {
        text-align: center;
        margin-bottom: 2;
    }

    #stats-content {
        height: auto;
        width: 100%;
        padding: 1;
    }

    #button-container {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 2;
    }

    .stats-table {
        margin-bottom: 2;
    }

    .no-stats-message {
        text-align: center;
        color: $warning;
        margin: 2 0;
    }
    """

    def __init__(
        self,
        statistics: AllStatisticsDTO | None = None,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize the statistics screen.

        Args:
            statistics: The statistics data to display.
            name: The name of the screen.
            id: The ID of the screen.
        """
        super().__init__(name=name, id=id)
        self._statistics = statistics

    def compose(self) -> ComposeResult:
        """Compose the statistics screen layout.

        Returns:
            The composed screen layout.
        """
        yield Header()

        with Container(id="stats-container"):
            yield Static(self._create_title(), id="title")

            with Vertical(id="stats-content"):
                if self._statistics and self._statistics.get_total_games_played() > 0:
                    yield Static(
                        self._create_overall_stats(),
                        id="overall-stats",
                        classes="stats-table",
                    )
                    yield Static(
                        self._create_difficulty_stats(),
                        id="difficulty-stats",
                        classes="stats-table",
                    )
                else:
                    yield Static(
                        self._create_no_stats_message(),
                        id="no-stats",
                        classes="no-stats-message",
                    )

            with Vertical(id="button-container"):
                yield Button("Back to Menu", variant="default", id="back-btn")

        yield Footer()

    def _create_title(self) -> RenderableType:
        """Create the title text.

        Returns:
            Formatted title text.
        """
        title = Text()
        title.append("Player Statistics\n", style="bold cyan")

        if self._statistics:
            title.append(
                f"Player: {self._statistics.player_name}",
                style="dim italic",
            )

        return Align.center(title)

    def _create_overall_stats(self) -> RenderableType:
        """Create the overall statistics table.

        Returns:
            Formatted statistics table.
        """
        if not self._statistics:
            return Text("")

        table = Table(title="Overall Statistics", title_style="bold yellow")

        table.add_column("Metric", style="cyan", justify="left")
        table.add_column("Value", style="white", justify="right")

        total_played = self._statistics.get_total_games_played()
        total_won = self._statistics.get_total_games_won()
        win_rate = self._statistics.get_overall_win_rate()

        table.add_row("Total Games Played", str(total_played))
        table.add_row("Total Games Won", str(total_won))
        table.add_row("Overall Win Rate", f"{win_rate:.1f}%")

        return table

    def _create_difficulty_stats(self) -> RenderableType:
        """Create the per-difficulty statistics table.

        Returns:
            Formatted statistics table.
        """
        if not self._statistics:
            return Text("")

        table = Table(title="Statistics by Difficulty", title_style="bold yellow")

        table.add_column("Difficulty", style="cyan", justify="left")
        table.add_column("Played", justify="right")
        table.add_column("Won", justify="right")
        table.add_column("Win Rate", justify="right")
        table.add_column("Avg Time", justify="right")

        # Sort by difficulty: easy, medium, hard
        difficulty_order = ["easy", "medium", "hard"]
        sorted_difficulties = sorted(
            self._statistics.statistics.items(),
            key=lambda x: difficulty_order.index(x[0])
            if x[0] in difficulty_order
            else 999,
        )

        for difficulty, stats in sorted_difficulties:
            difficulty_display = self._format_difficulty(difficulty)
            played = str(stats.games_played)
            won = str(stats.games_won)
            win_rate = f"{stats.win_rate:.1f}%"
            avg_time = self._format_time(stats.average_time)

            # Color code the win rate
            win_rate_style = self._get_win_rate_style(stats.win_rate)

            table.add_row(
                difficulty_display,
                played,
                won,
                Text(win_rate, style=win_rate_style),
                avg_time,
            )

        return table

    def _create_no_stats_message(self) -> RenderableType:
        """Create a message when no statistics are available.

        Returns:
            Formatted message text.
        """
        text = Text()
        text.append("No statistics available yet.\n\n", style="bold yellow")
        text.append(
            "Play some games to see your statistics here!",
            style="dim",
        )

        return Align.center(text)

    def _format_difficulty(self, difficulty: str) -> Text:
        """Format difficulty level with color.

        Args:
            difficulty: The difficulty level.

        Returns:
            Formatted Text with color.
        """
        difficulty_lower = difficulty.lower()
        difficulty_display = difficulty.capitalize()

        if difficulty_lower == "easy":
            style = "green bold"
        elif difficulty_lower == "medium":
            style = "yellow bold"
        elif difficulty_lower == "hard":
            style = "red bold"
        else:
            style = "white"

        return Text(difficulty_display, style=style)

    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to a readable string.

        Args:
            seconds: Time in seconds.

        Returns:
            Formatted time string.
        """
        if seconds == 0:
            return "N/A"

        td = timedelta(seconds=int(seconds))
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def _get_win_rate_style(self, win_rate: float) -> str:
        """Get the style for win rate display.

        Args:
            win_rate: The win rate percentage.

        Returns:
            Rich style string.
        """
        if win_rate >= 80:
            return "bold green"
        if win_rate >= 50:
            return "bold yellow"
        if win_rate > 0:
            return "bold red"
        return "dim"

    @on(Button.Pressed, "#back-btn")
    def handle_back_button(self) -> None:
        """Handle back button press."""
        self.action_back()

    def action_back(self) -> None:
        """Return to the previous screen."""
        self.app.pop_screen()

    def set_statistics(self, statistics: AllStatisticsDTO) -> None:
        """Update the statistics data to display.

        Args:
            statistics: The new statistics data.
        """
        self._statistics = statistics
        self.refresh()


class StatsSummaryWidget(Static):
    """Compact statistics summary widget.

    This widget displays a brief summary of statistics that can be
    embedded in other screens (e.g., showing stats in the game screen).
    """

    def __init__(
        self,
        stats: StatisticsDTO | None = None,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize the stats summary widget.

        Args:
            stats: Statistics data to display.
            name: The name of the widget.
            id: The ID of the widget.
        """
        super().__init__(name=name, id=id)
        self._stats = stats

    def render(self) -> RenderableType:
        """Render the stats summary.

        Returns:
            Formatted statistics summary.
        """
        if not self._stats or self._stats.games_played == 0:
            return Text("No games played yet", style="dim italic")

        text = Text()
        text.append(f"{self._stats.difficulty.capitalize()}: ", style="bold")
        text.append(f"{self._stats.games_played} played, ", style="dim")
        text.append(f"{self._stats.games_won} won ", style="green")
        text.append(f"({self._stats.win_rate:.1f}%)", style="dim")

        return text

    def set_stats(self, stats: StatisticsDTO) -> None:
        """Update the statistics data.

        Args:
            stats: The new statistics data.
        """
        self._stats = stats
        self.refresh()
