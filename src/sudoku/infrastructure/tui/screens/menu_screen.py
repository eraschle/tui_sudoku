"""Main menu screen for the Sudoku application.

This module provides the main menu screen where users can start a new game,
view statistics, or quit the application.
"""


from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class MenuScreen(Screen):
    """Main menu screen for the Sudoku application.

    This screen provides options to:
    - Start a new game
    - View player statistics
    - Quit the application

    The screen follows the Single Responsibility Principle by focusing
    solely on menu presentation and navigation.
    """

    BINDINGS = [
        ("n", "new_game", "New Game"),
        ("s", "statistics", "Statistics"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    MenuScreen {
        align: center middle;
    }

    #menu-container {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }

    #title {
        text-align: center;
        margin-bottom: 2;
    }

    #menu-buttons {
        align: center middle;
        height: auto;
        width: 100%;
    }

    Button {
        width: 30;
        margin: 1;
    }

    #footer-help {
        text-align: center;
        margin-top: 2;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize the menu screen.

        Args:
            name: The name of the screen.
            id: The ID of the screen.
        """
        super().__init__(name=name, id=id)

    def compose(self) -> ComposeResult:
        """Compose the menu screen layout.

        Returns:
            The composed screen layout.
        """
        yield Header()

        with Container(id="menu-container"):
            yield Static(self._create_title(), id="title")

            with Vertical(id="menu-buttons"):
                yield Button("New Game", variant="primary", id="new-game-btn")
                yield Button("Statistics", variant="default", id="statistics-btn")
                yield Button("Quit", variant="error", id="quit-btn")

            yield Static(self._create_help_text(), id="footer-help")

        yield Footer()

    def _create_title(self) -> RenderableType:
        """Create the title text for the menu.

        Returns:
            Formatted title text.
        """
        title = Text()
        title.append("SUDOKU\n", style="bold cyan")
        title.append("Terminal Edition", style="dim italic")

        return Align.center(title)

    def _create_help_text(self) -> RenderableType:
        """Create help text showing keyboard shortcuts.

        Returns:
            Formatted help text.
        """
        help_text = Text()
        help_text.append("Keyboard: ", style="dim")
        help_text.append("n", style="bold")
        help_text.append("=New Game  ", style="dim")
        help_text.append("s", style="bold")
        help_text.append("=Statistics  ", style="dim")
        help_text.append("q", style="bold")
        help_text.append("=Quit", style="dim")

        return Align.center(help_text)

    @on(Button.Pressed, "#new-game-btn")
    def handle_new_game_button(self) -> None:
        """Handle new game button press."""
        self.action_new_game()

    @on(Button.Pressed, "#statistics-btn")
    def handle_statistics_button(self) -> None:
        """Handle statistics button press."""
        self.action_statistics()

    @on(Button.Pressed, "#quit-btn")
    def handle_quit_button(self) -> None:
        """Handle quit button press."""
        self.action_quit()

    def action_new_game(self) -> None:
        """Action to start a new game.

        This action posts a custom message that the app will handle
        to navigate to player input screen.
        """
        self.app.push_screen("player_input")

    def action_statistics(self) -> None:
        """Action to view statistics.

        This action posts a custom message that the app will handle
        to navigate to statistics screen.
        """
        self.app.push_screen("statistics")

    def action_quit(self) -> None:
        """Action to quit the application."""
        self.app.exit()


class WelcomePanel(Static):
    """Welcome panel component for the menu screen.

    This component displays a welcome message and game information.
    It demonstrates the composition principle by being a reusable
    component that can be used in multiple screens.
    """

    def __init__(
        self,
        player_name: str | None = None,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize the welcome panel.

        Args:
            player_name: Optional player name to personalize the welcome.
            name: The name of the widget.
            id: The ID of the widget.
        """
        super().__init__(name=name, id=id)
        self._player_name = player_name

    def render(self) -> RenderableType:
        """Render the welcome panel.

        Returns:
            A Rich renderable with welcome message.
        """
        text = Text()

        if self._player_name:
            text.append(f"Welcome back, {self._player_name}!\n\n", style="bold cyan")
        else:
            text.append("Welcome to Sudoku!\n\n", style="bold cyan")

        text.append(
            "Select an option below to begin, or use keyboard shortcuts.\n",
            style="dim",
        )

        return Panel(
            Align.center(text),
            title="Welcome",
            border_style="cyan",
        )

    def set_player_name(self, player_name: str) -> None:
        """Update the player name displayed in the welcome.

        Args:
            player_name: The new player name.
        """
        self._player_name = player_name
        self.refresh()
