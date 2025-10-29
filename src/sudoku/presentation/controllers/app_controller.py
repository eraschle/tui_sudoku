"""Application controller coordinating use cases and presentation.

This module provides the main application controller that coordinates
between the application layer (use cases) and the presentation layer (TUI).
"""

from sudoku.application.dto.game_state import GameStateDTO
from sudoku.application.dto.statistics_dto import AllStatisticsDTO
from sudoku.application.use_cases.check_completion import CheckCompletionUseCase
from sudoku.application.use_cases.get_statistics import GetStatisticsUseCase
from sudoku.application.use_cases.make_move import MakeMoveUseCase
from sudoku.application.use_cases.start_new_game import StartNewGameUseCase
from sudoku.application.use_cases.update_statistics import UpdateStatisticsUseCase
from sudoku.domain.entities.game import Game
from sudoku.domain.value_objects.position import Position


class AppController:
    """Application controller coordinating use cases and presentation.

    This controller acts as the intermediary between the TUI screens and
    the application layer use cases. It follows the Single Responsibility
    Principle by focusing on coordination and state management.

    The controller manages the current game state and delegates business
    logic to appropriate use cases, following the Dependency Inversion
    Principle by depending on abstractions (use cases).

    Attributes:
        current_game: The current game instance.
        current_player: The name of the current player.
    """

    def __init__(
        self,
        start_game_use_case: StartNewGameUseCase,
        make_move_use_case: MakeMoveUseCase,
        check_completion_use_case: CheckCompletionUseCase,
        get_statistics_use_case: GetStatisticsUseCase,
        update_statistics_use_case: UpdateStatisticsUseCase,
    ) -> None:
        """Initialize the application controller.

        Args:
            start_game_use_case: Use case for starting new games.
            make_move_use_case: Use case for making moves.
            check_completion_use_case: Use case for checking game completion.
            get_statistics_use_case: Use case for retrieving statistics.
            update_statistics_use_case: Use case for updating statistics.
        """
        self._start_game_use_case = start_game_use_case
        self._make_move_use_case = make_move_use_case
        self._check_completion_use_case = check_completion_use_case
        self._get_statistics_use_case = get_statistics_use_case
        self._update_statistics_use_case = update_statistics_use_case

        self._current_game: Game | None = None
        self._current_player: str = ""

    def start_new_game(self, player_name: str, difficulty: str) -> GameStateDTO:
        """Start a new game with the specified parameters.

        Args:
            player_name: The name of the player.
            difficulty: The difficulty level (easy, medium, hard).

        Returns:
            GameStateDTO representing the initial game state.

        Raises:
            ValueError: If player_name is empty or difficulty is invalid.
        """
        # Execute use case to create game and get state
        game, game_state = self._start_game_use_case.execute(
            player_name=player_name,
            difficulty=difficulty,
        )

        # Store game instance and player
        self._current_game = game
        self._current_player = player_name

        return game_state

    def make_move(self, position: Position, value: int | None) -> tuple[bool, GameStateDTO]:
        """Make a move on the current game board.

        Args:
            position: The position where to make the move.
            value: The value to place (1-9), or None to clear the cell.

        Returns:
            Tuple of (success, updated_game_state).
            success is True if the move was valid and applied.

        Raises:
            ValueError: If no game is in progress or move is invalid.
        """
        if not self._current_game:
            msg = "No game in progress"
            raise ValueError(msg)

        # Execute the move through use case
        success, game_state = self._make_move_use_case.execute(
            game=self._current_game,
            position=position,
            value=value,
        )

        # Check if game is complete after the move
        if success:
            is_complete = self._check_completion_use_case.execute(self._current_game)
            if is_complete:
                self._handle_game_completion()

        return success, game_state

    def check_game_completion(self) -> bool:
        """Check if the current game is complete.

        Returns:
            True if the game is complete and valid, False otherwise.

        Raises:
            ValueError: If no game is in progress.
        """
        if not self._current_game:
            msg = "No game in progress"
            raise ValueError(msg)

        return self._check_completion_use_case.execute(self._current_game)

    def get_player_statistics(self, player_name: str | None = None) -> AllStatisticsDTO:
        """Get statistics for a player.

        Args:
            player_name: The player name. If None, uses current player.

        Returns:
            AllStatisticsDTO containing all statistics for the player.

        Raises:
            ValueError: If player_name is not provided and no current player.
        """
        target_player = player_name or self._current_player

        if not target_player:
            msg = "No player name provided and no current player"
            raise ValueError(msg)

        return self._get_statistics_use_case.execute(target_player)

    def _handle_game_completion(self) -> None:
        """Handle game completion logic.

        Updates statistics when a game is won.
        """
        if not self._current_game:
            return

        # Update statistics through use case
        try:
            self._update_statistics_use_case.execute(
                player_name=self._current_player,
                difficulty=self._current_game.difficulty.name.lower(),
                won=True,
                time_seconds=self._current_game.elapsed_time.total_seconds(),
            )
        except Exception as e:
            # Log error but don't crash on statistics update failure
            print(f"Failed to update statistics: {e}")

    def set_current_game(self, game: Game) -> None:
        """Set the current game instance.

        This is a helper method for connecting the controller with
        the game entity when it's created by a use case.

        Args:
            game: The game instance to set as current.
        """
        self._current_game = game

    def get_current_game(self) -> Game | None:
        """Get the current game instance.

        Returns:
            The current game, or None if no game is in progress.
        """
        return self._current_game

    def get_current_player(self) -> str:
        """Get the current player name.

        Returns:
            The current player name.
        """
        return self._current_player

    def has_active_game(self) -> bool:
        """Check if there is an active game.

        Returns:
            True if a game is currently in progress, False otherwise.
        """
        return self._current_game is not None and self._current_game.is_active
