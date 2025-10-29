"""Unit tests for the Game entity.

This module tests the Game entity's behavior including state transitions,
timer functionality, and move handling.
"""

from datetime import timedelta
from time import sleep

import pytest

from sudoku.domain.entities.game import Game, GameState
from sudoku.domain.value_objects.difficulty import Difficulty
from sudoku.domain.value_objects.position import Position


class TestGameCreation:
    """Test game creation and initialization."""

    def test_create_game(self, sample_game: Game) -> None:
        """Test creating a game instance."""
        assert sample_game.state == GameState.NOT_STARTED
        assert sample_game.difficulty == Difficulty.MEDIUM
        assert sample_game.elapsed_time == timedelta()

    def test_game_starts_not_active(self, sample_game: Game) -> None:
        """Test that new game is not active."""
        assert not sample_game.is_active
        assert not sample_game.is_finished


class TestGameStart:
    """Test starting a game."""

    def test_start_game(self, sample_game: Game) -> None:
        """Test starting a game changes state to IN_PROGRESS."""
        sample_game.start()

        assert sample_game.state == GameState.IN_PROGRESS
        assert sample_game.is_active

    def test_start_game_initializes_timer(self, sample_game: Game) -> None:
        """Test that starting a game initializes the timer."""
        sample_game.start()
        sleep(0.1)  # Wait a bit

        assert sample_game.elapsed_time > timedelta()

    def test_start_already_started_game_raises_error(self, sample_game: Game) -> None:
        """Test that starting an already started game raises ValueError."""
        sample_game.start()

        with pytest.raises(ValueError, match="already been started"):
            sample_game.start()

    def test_cannot_start_finished_game(self, sample_game: Game) -> None:
        """Test that finished game cannot be restarted."""
        sample_game.start()
        sample_game.mark_as_won()

        with pytest.raises(ValueError, match="already been started"):
            sample_game.start()


class TestGamePauseResume:
    """Test pausing and resuming a game."""

    def test_pause_game(self, sample_game: Game) -> None:
        """Test pausing a game in progress."""
        sample_game.start()

        sample_game.pause()

        assert sample_game.state == GameState.PAUSED
        assert sample_game.is_active

    def test_pause_not_started_game_raises_error(self, sample_game: Game) -> None:
        """Test that pausing a not-started game raises ValueError."""
        with pytest.raises(ValueError, match="Can only pause a game in progress"):
            sample_game.pause()

    def test_resume_paused_game(self, sample_game: Game) -> None:
        """Test resuming a paused game."""
        sample_game.start()
        sample_game.pause()

        sample_game.resume()

        assert sample_game.state == GameState.IN_PROGRESS

    def test_resume_not_paused_game_raises_error(self, sample_game: Game) -> None:
        """Test that resuming a non-paused game raises ValueError."""
        sample_game.start()

        with pytest.raises(ValueError, match="Can only resume a paused game"):
            sample_game.resume()

    def test_pause_resume_timer_excludes_pause_time(self, sample_game: Game) -> None:
        """Test that paused time is not counted in elapsed time."""
        sample_game.start()
        sleep(0.1)
        elapsed_before_pause = sample_game.elapsed_time

        sample_game.pause()
        sleep(0.1)  # Paused for 100ms
        sample_game.resume()

        # Elapsed time should be roughly the same as before pause
        # (within small margin for test execution time)
        elapsed_after_resume = sample_game.elapsed_time
        difference = elapsed_after_resume - elapsed_before_pause

        assert difference < timedelta(milliseconds=50)


class TestGameMakeMove:
    """Test making moves in a game."""

    def test_make_move_sets_value(self, sample_game: Game) -> None:
        """Test that making a move sets the value on the board."""
        sample_game.start()
        position = Position(0, 0)

        sample_game.make_move(position, 5)

        cell = sample_game.board.get_cell(position)
        assert cell.get_numeric_value() == 5

    def test_make_move_clears_value_when_none(self, sample_game: Game) -> None:
        """Test that making a move with None clears the cell."""
        sample_game.start()
        position = Position(0, 0)
        sample_game.board.set_cell_value(position, 5)

        sample_game.make_move(position, None)

        cell = sample_game.board.get_cell(position)
        assert cell.is_empty()

    def test_make_move_when_not_in_progress_raises_error(
        self, sample_game: Game
    ) -> None:
        """Test that making a move when not in progress raises ValueError."""
        with pytest.raises(ValueError, match="not in progress"):
            sample_game.make_move(Position(0, 0), 5)

    def test_make_move_when_paused_raises_error(self, sample_game: Game) -> None:
        """Test that making a move when paused raises ValueError."""
        sample_game.start()
        sample_game.pause()

        with pytest.raises(ValueError, match="not in progress"):
            sample_game.make_move(Position(0, 0), 5)

    def test_make_move_on_fixed_cell_raises_error(self, sample_game: Game) -> None:
        """Test that making a move on a fixed cell raises ValueError."""
        position = Position(0, 0)
        sample_game.board.set_cell_value(position, 5, is_fixed=True)
        sample_game.start()

        with pytest.raises(ValueError, match="Cannot modify a fixed cell"):
            sample_game.make_move(position, 8)


class TestGameCompletion:
    """Test game completion states."""

    def test_mark_as_won(self, sample_game: Game) -> None:
        """Test marking a game as won."""
        sample_game.start()

        sample_game.mark_as_won()

        assert sample_game.state == GameState.WON
        assert sample_game.is_finished
        assert not sample_game.is_active

    def test_mark_as_lost(self, sample_game: Game) -> None:
        """Test marking a game as lost."""
        sample_game.start()

        sample_game.mark_as_lost()

        assert sample_game.state == GameState.LOST
        assert sample_game.is_finished

    def test_cannot_win_not_started_game(self, sample_game: Game) -> None:
        """Test that not-started game cannot be won."""
        with pytest.raises(ValueError, match="Can only win a game in progress"):
            sample_game.mark_as_won()

    def test_cannot_lose_not_started_game(self, sample_game: Game) -> None:
        """Test that not-started game cannot be lost."""
        with pytest.raises(ValueError, match="Can only lose a game in progress"):
            sample_game.mark_as_lost()

    def test_won_game_records_end_time(self, sample_game: Game) -> None:
        """Test that winning a game records the end time."""
        sample_game.start()
        sleep(0.1)

        sample_game.mark_as_won()

        assert sample_game.elapsed_time > timedelta()


class TestGameElapsedTime:
    """Test game timer functionality."""

    def test_elapsed_time_before_start(self, sample_game: Game) -> None:
        """Test that elapsed time is zero before game starts."""
        assert sample_game.elapsed_time == timedelta()

    def test_elapsed_time_increases_during_game(self, sample_game: Game) -> None:
        """Test that elapsed time increases during gameplay."""
        sample_game.start()
        sleep(0.1)

        elapsed1 = sample_game.elapsed_time
        sleep(0.1)
        elapsed2 = sample_game.elapsed_time

        assert elapsed2 > elapsed1

    def test_elapsed_time_stops_when_won(self, sample_game: Game) -> None:
        """Test that elapsed time stops when game is won."""
        sample_game.start()
        sleep(0.1)
        sample_game.mark_as_won()

        elapsed1 = sample_game.elapsed_time
        sleep(0.1)
        elapsed2 = sample_game.elapsed_time

        # Elapsed time should be frozen
        difference = abs(elapsed2.total_seconds() - elapsed1.total_seconds())
        assert difference < 0.01  # Allow small margin for test execution


class TestGameProperties:
    """Test game property accessors."""

    def test_is_active_in_progress(self, sample_game: Game) -> None:
        """Test is_active returns True when game is in progress."""
        sample_game.start()

        assert sample_game.is_active

    def test_is_active_paused(self, sample_game: Game) -> None:
        """Test is_active returns True when game is paused."""
        sample_game.start()
        sample_game.pause()

        assert sample_game.is_active

    def test_is_active_not_started(self, sample_game: Game) -> None:
        """Test is_active returns False when game not started."""
        assert not sample_game.is_active

    def test_is_active_finished(self, sample_game: Game) -> None:
        """Test is_active returns False when game is finished."""
        sample_game.start()
        sample_game.mark_as_won()

        assert not sample_game.is_active

    def test_is_finished_won(self, sample_game: Game) -> None:
        """Test is_finished returns True when game is won."""
        sample_game.start()
        sample_game.mark_as_won()

        assert sample_game.is_finished

    def test_is_finished_lost(self, sample_game: Game) -> None:
        """Test is_finished returns True when game is lost."""
        sample_game.start()
        sample_game.mark_as_lost()

        assert sample_game.is_finished

    def test_is_finished_in_progress(self, sample_game: Game) -> None:
        """Test is_finished returns False when game is in progress."""
        sample_game.start()

        assert not sample_game.is_finished


class TestGameStringRepresentation:
    """Test game string representation."""

    def test_str_representation(self, sample_game: Game) -> None:
        """Test string representation includes key information."""
        sample_game.start()

        game_str = str(sample_game)

        assert "TestPlayer" in game_str
        assert "MEDIUM" in game_str or "Medium" in game_str
        assert "IN_PROGRESS" in game_str


class TestGameStateTransitions:
    """Test valid and invalid state transitions."""

    def test_state_transition_sequence(self, sample_game: Game) -> None:
        """Test a typical state transition sequence."""
        # NOT_STARTED -> IN_PROGRESS
        assert sample_game.state == GameState.NOT_STARTED
        sample_game.start()
        assert sample_game.state == GameState.IN_PROGRESS

        # IN_PROGRESS -> PAUSED
        sample_game.pause()
        assert sample_game.state == GameState.PAUSED

        # PAUSED -> IN_PROGRESS
        sample_game.resume()
        assert sample_game.state == GameState.IN_PROGRESS

        # IN_PROGRESS -> WON
        sample_game.mark_as_won()
        assert sample_game.state == GameState.WON

    @pytest.mark.parametrize(
        "final_state",
        [GameState.WON, GameState.LOST],
    )
    def test_finished_state_is_terminal(
        self, sample_game: Game, final_state: GameState
    ) -> None:
        """Test that finished states (WON/LOST) are terminal."""
        sample_game.start()

        if final_state == GameState.WON:
            sample_game.mark_as_won()
        else:
            sample_game.mark_as_lost()

        # Cannot pause a finished game
        with pytest.raises(ValueError):
            sample_game.pause()

        # Cannot make moves in a finished game
        with pytest.raises(ValueError):
            sample_game.make_move(Position(0, 0), 5)
