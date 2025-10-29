"""Player input screen for collecting player information.

This module provides a screen for entering player name and selecting
game difficulty before starting a new game.
"""

from collections.abc import Callable

from rich.align import Align
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, RadioButton, RadioSet, Static


class PlayerInputScreen(Screen):
    """Screen for collecting player name and difficulty selection.

    This screen collects:
    - Player name
    - Difficulty level (Easy, Medium, Hard)

    When confirmed, it triggers the game start callback with the
    collected information.

    Attributes:
        on_confirm: Callback function called when player confirms input.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "submit", "Start Game"),
    ]

    CSS = """
    PlayerInputScreen {
        align: center middle;
    }

    #input-container {
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

    #form-container {
        height: auto;
        width: 100%;
        padding: 1;
    }

    #name-section {
        margin-bottom: 2;
    }

    #difficulty-section {
        margin-bottom: 2;
    }

    Label {
        margin-bottom: 1;
    }

    Input {
        margin-bottom: 1;
    }

    RadioSet {
        height: auto;
        margin-bottom: 1;
    }

    #button-container {
        width: 100%;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    .error-message {
        color: $error;
        text-align: center;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        on_confirm: Callable[[str, str], None] | None = None,
        default_player_name: str = "",
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize the player input screen.

        Args:
            on_confirm: Callback function(player_name, difficulty) called on confirm.
            default_player_name: Default player name to pre-fill.
            name: The name of the screen.
            id: The ID of the screen.
        """
        super().__init__(name=name, id=id)
        self._on_confirm = on_confirm
        self._default_player_name = default_player_name

    def compose(self) -> ComposeResult:
        """Compose the player input screen layout.

        Returns:
            The composed screen layout.
        """
        yield Header()

        with Container(id="input-container"):
            yield Static(self._create_title(), id="title")

            with Vertical(id="form-container"):
                with Vertical(id="name-section"):
                    yield Label("Player Name:")
                    yield Input(
                        placeholder="Enter your name",
                        value=self._default_player_name,
                        id="player-name-input",
                    )

                with Vertical(id="difficulty-section"):
                    yield Label("Select Difficulty:")
                    with RadioSet(id="difficulty-radio"):
                        yield RadioButton("Easy", value=True, id="difficulty-easy")
                        yield RadioButton("Medium", id="difficulty-medium")
                        yield RadioButton("Hard", id="difficulty-hard")

                yield Static("", id="error-message", classes="error-message")

                with Horizontal(id="button-container"):
                    yield Button("Start Game", variant="primary", id="start-btn")
                    yield Button("Cancel", variant="default", id="cancel-btn")

        yield Footer()

    def _create_title(self) -> Align:
        """Create the title text.

        Returns:
            Formatted title text.
        """
        title = Text()
        title.append("New Game Setup\n", style="bold cyan")
        title.append("Configure your game settings", style="dim italic")

        return Align.center(title)

    @on(Button.Pressed, "#start-btn")
    def handle_start_button(self) -> None:
        """Handle start game button press."""
        self.action_submit()

    @on(Button.Pressed, "#cancel-btn")
    def handle_cancel_button(self) -> None:
        """Handle cancel button press."""
        self.action_cancel()

    @on(Input.Submitted, "#player-name-input")
    def handle_input_submitted(self) -> None:
        """Handle player name input submission (Enter key)."""
        self.action_submit()

    def action_submit(self) -> None:
        """Submit the player information and start the game."""
        player_name = self._get_player_name()
        difficulty = self._get_selected_difficulty()

        # Validate input
        error_message = self._validate_input(player_name, difficulty)
        if error_message:
            self._show_error(error_message)
            return

        # Clear any previous error
        self._clear_error()

        # Call the confirmation callback if provided
        if self._on_confirm:
            self._on_confirm(player_name, difficulty)
        else:
            # Default behavior: send message to app
            self.dismiss((player_name, difficulty))

    def action_cancel(self) -> None:
        """Cancel the player input and return to previous screen."""
        self.app.pop_screen()

    def _get_player_name(self) -> str:
        """Get the entered player name.

        Returns:
            The player name from the input field.
        """
        input_widget = self.query_one("#player-name-input", Input)
        return input_widget.value.strip()

    def _get_selected_difficulty(self) -> str:
        """Get the selected difficulty level.

        Returns:
            The selected difficulty level (easy, medium, hard).
        """
        radio_set = self.query_one("#difficulty-radio", RadioSet)

        if radio_set.pressed_button is None:
            return "easy"  # Default to easy if nothing selected

        button_id = radio_set.pressed_button.id
        if button_id == "difficulty-easy":
            return "easy"
        if button_id == "difficulty-medium":
            return "medium"
        if button_id == "difficulty-hard":
            return "hard"

        return "easy"

    def _validate_input(self, player_name: str, difficulty: str) -> str | None:
        """Validate the player input.

        Args:
            player_name: The entered player name.
            difficulty: The selected difficulty.

        Returns:
            Error message if validation fails, None otherwise.
        """
        if not player_name:
            return "Please enter a player name"

        if len(player_name) > 50:
            return "Player name is too long (max 50 characters)"

        valid_difficulties = {"easy", "medium", "hard"}
        if difficulty not in valid_difficulties:
            return "Please select a valid difficulty level"

        return None

    def _show_error(self, message: str) -> None:
        """Display an error message.

        Args:
            message: The error message to display.
        """
        error_widget = self.query_one("#error-message", Static)
        error_widget.update(message)

    def _clear_error(self) -> None:
        """Clear any displayed error message."""
        error_widget = self.query_one("#error-message", Static)
        error_widget.update("")

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Focus the player name input
        input_widget = self.query_one("#player-name-input", Input)
        input_widget.focus()


class DifficultyInfo(Static):
    """Widget displaying information about difficulty levels.

    This component provides descriptions of what each difficulty level means
    in terms of puzzle complexity and pre-filled cells.
    """

    def render(self) -> Text:
        """Render the difficulty information.

        Returns:
            Formatted text with difficulty descriptions.
        """
        text = Text()

        text.append("Difficulty Levels:\n", style="bold")
        text.append("\n")

        text.append("Easy: ", style="green bold")
        text.append("Many pre-filled cells, good for beginners\n", style="dim")

        text.append("Medium: ", style="yellow bold")
        text.append("Moderate challenge, some pre-filled cells\n", style="dim")

        text.append("Hard: ", style="red bold")
        text.append("Minimal pre-filled cells, for experienced players\n", style="dim")

        return text
