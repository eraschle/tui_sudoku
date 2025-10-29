"""Integration tests for complete game flow.

This module tests the full game flow from creation to completion,
integrating domain entities, services, and infrastructure components.
"""

import pytest

from sudoku.domain.entities.board import Board
from sudoku.domain.entities.game import Game, GameState
from sudoku.domain.entities.player import Player
from sudoku.domain.services.game_rules import GameRules
from sudoku.domain.value_objects.board_size import BoardSize
from sudoku.domain.value_objects.difficulty import Difficulty
from sudoku.domain.value_objects.position import Position
from sudoku.infrastructure.generators.backtracking_generator import (
    BacktrackingGenerator,
)
from sudoku.infrastructure.solvers.backtracking_solver import BacktrackingSolver


class TestCompleteGameFlow:
    """Test complete game flow from start to finish."""

    def test_full_game_lifecycle(self) -> None:
        """Test a complete game lifecycle: create, play, complete."""
        # 1. Create game components
        board_size = BoardSize.standard_9x9()
        player = Player("IntegrationTestPlayer")
        board = Board(board_size)

        # 2. Generate a puzzle
        generator = BacktrackingGenerator()
        puzzle = generator.generate(box_width=3, box_height=3, difficulty="EASY")

        # 3. Load puzzle into board
        for row in range(9):
            for col in range(9):
                if puzzle[row][col] != 0:
                    board.set_cell_value(
                        Position(row, col), puzzle[row][col], is_fixed=True
                    )

        # 4. Create game
        game = Game(board=board, player=player, difficulty=Difficulty.EASY)

        # 5. Start game
        game.start()
        assert game.state == GameState.IN_PROGRESS

        # 6. Solve the puzzle
        solver = BacktrackingSolver()
        solution = solver.solve(puzzle, box_width=3, box_height=3)
        assert solution is not None

        # 7. Fill in the solution
        for row in range(9):
            for col in range(9):
                if puzzle[row][col] == 0:  # Only fill empty cells
                    game.make_move(Position(row, col), solution[row][col])

        # 8. Verify board is complete and valid
        assert game.board.is_complete()
        assert GameRules.is_solved(game.board)

        # 9. Mark game as won
        game.mark_as_won()
        assert game.state == GameState.WON
        assert game.is_finished

    def test_game_flow_with_pause_resume(self) -> None:
        """Test game flow with pause and resume."""
        # Create simple game
        board = Board(BoardSize.standard_9x9())
        player = Player("TestPlayer")
        game = Game(board=board, player=player, difficulty=Difficulty.MEDIUM)

        # Start game
        game.start()
        assert game.state == GameState.IN_PROGRESS

        # Make some moves
        game.make_move(Position(0, 0), 5)
        game.make_move(Position(0, 1), 3)

        # Pause game
        game.pause()
        assert game.state == GameState.PAUSED

        # Cannot make moves while paused
        with pytest.raises(ValueError):
            game.make_move(Position(0, 2), 7)

        # Resume game
        game.resume()
        assert game.state == GameState.IN_PROGRESS

        # Can make moves again
        game.make_move(Position(0, 2), 7)
        assert game.board.get_cell(Position(0, 2)).get_numeric_value() == 7

    def test_game_flow_with_invalid_moves(self) -> None:
        """Test game flow handling invalid moves."""
        board = Board(BoardSize.standard_9x9())
        player = Player("TestPlayer")
        game = Game(board=board, player=player, difficulty=Difficulty.EASY)

        # Set up some fixed cells
        board.set_cell_value(Position(0, 0), 5, is_fixed=True)

        game.start()

        # Try to modify a fixed cell (should fail)
        with pytest.raises(ValueError, match="fixed cell"):
            game.make_move(Position(0, 0), 3)

        # Make a valid move
        game.make_move(Position(1, 1), 7)
        assert game.board.get_cell(Position(1, 1)).get_numeric_value() == 7

        # Clear the cell
        game.make_move(Position(1, 1), None)
        assert game.board.get_cell(Position(1, 1)).is_empty()


class TestGameWithValidator:
    """Test game flow with validation."""

    def test_valid_moves_only(self) -> None:
        """Test that only valid moves are accepted using GameRules."""
        board = Board(BoardSize.standard_9x9())
        player = Player("TestPlayer")
        game = Game(board=board, player=player, difficulty=Difficulty.EASY)

        game.start()

        # Place a value
        game.make_move(Position(0, 0), 5)

        # Check that placing same value in same row is invalid
        is_valid = GameRules.is_valid_placement(game.board, Position(0, 5), 5)
        assert not is_valid

        # Check that placing same value in same column is invalid
        is_valid = GameRules.is_valid_placement(game.board, Position(5, 0), 5)
        assert not is_valid

        # Check that placing same value in same box is invalid
        is_valid = GameRules.is_valid_placement(game.board, Position(2, 2), 5)
        assert not is_valid

        # Check that placing value in different region is valid
        is_valid = GameRules.is_valid_placement(game.board, Position(5, 5), 5)
        assert is_valid


class TestPuzzleGenerationAndSolution:
    """Test puzzle generation and solution integration."""

    def test_generated_puzzle_is_solvable(self) -> None:
        """Test that generated puzzles can be solved."""
        generator = BacktrackingGenerator()
        solver = BacktrackingSolver()

        # Generate puzzle
        puzzle = generator.generate(box_width=3, box_height=3, difficulty="MEDIUM")

        # Verify it's solvable
        solution = solver.solve(puzzle, box_width=3, box_height=3)

        assert solution is not None
        assert all(0 not in row for row in solution)

    def test_generated_puzzle_has_unique_solution(self) -> None:
        """Test that generated puzzles have unique solutions."""
        generator = BacktrackingGenerator()
        solver = BacktrackingSolver()

        # Generate puzzle
        puzzle = generator.generate(box_width=3, box_height=3, difficulty="EASY")

        # Check uniqueness
        has_unique = solver.has_unique_solution(puzzle, box_width=3, box_height=3)

        assert has_unique

    def test_6x6_puzzle_generation_and_solution(self) -> None:
        """Test 6x6 puzzle generation and solution."""
        generator = BacktrackingGenerator()
        solver = BacktrackingSolver()

        # Generate 6x6 puzzle
        puzzle = generator.generate(box_width=3, box_height=2, difficulty="MEDIUM")

        assert len(puzzle) == 6
        assert all(len(row) == 6 for row in puzzle)

        # Solve it
        solution = solver.solve(puzzle, box_width=3, box_height=2)

        assert solution is not None
        assert len(solution) == 6
        assert all(len(row) == 6 for row in solution)


class TestBoardAndGameRulesIntegration:
    """Test integration between Board and GameRules."""

    def test_game_rules_with_real_board(self, partially_filled_board_9x9: Board) -> None:
        """Test GameRules with a real Board instance."""
        # Board has some values filled, all should be valid
        assert GameRules.is_valid_board(partially_filled_board_9x9)

        # Get candidates for an empty position
        empty_positions = partially_filled_board_9x9.get_empty_positions()
        if empty_positions:
            candidates = GameRules.get_candidates(
                partially_filled_board_9x9, empty_positions[0]
            )
            assert len(candidates) > 0
            assert all(1 <= c <= 9 for c in candidates)

    def test_filling_board_maintains_validity(self) -> None:
        """Test that filling board step by step maintains validity."""
        board = Board(BoardSize.standard_9x9())

        # Fill first row with valid values
        for col in range(9):
            board.set_cell_value(Position(0, col), col + 1)

        # Board should still be valid
        assert GameRules.is_valid_board(board)
        assert GameRules.is_valid_row(board, 0)

        # Try to place duplicate in first row (should be invalid according to rules)
        is_valid = GameRules.is_valid_placement(board, Position(0, 0), 1)
        # Position(0,0) is already filled, so we can't place there
        # Let's check a different position
        board.clear_cell(Position(0, 0))
        is_valid = GameRules.is_valid_placement(board, Position(0, 0), 2)
        assert not is_valid  # 2 already exists in the row


class TestCompleteGameWithStatistics:
    """Test complete game flow with statistics tracking."""

    def test_game_completion_tracks_time(self) -> None:
        """Test that game completion tracks elapsed time."""
        from time import sleep

        board = Board(BoardSize.standard_9x9())
        player = Player("TestPlayer")
        game = Game(board=board, player=player, difficulty=Difficulty.EASY)

        game.start()
        sleep(0.1)  # Wait a bit

        game.mark_as_won()

        # Time should be tracked
        assert game.elapsed_time.total_seconds() > 0
        assert game.is_finished


class TestEdgeCasesIntegration:
    """Test edge cases in integration scenarios."""

    def test_clone_board_independence(self) -> None:
        """Test that cloned boards are independent."""
        original = Board(BoardSize.standard_9x9())
        original.set_cell_value(Position(0, 0), 5)

        cloned = original.clone()
        cloned.set_cell_value(Position(1, 1), 7)

        # Original should not have the new value
        assert original.get_cell(Position(1, 1)).is_empty()
        # Clone should have both values
        assert cloned.get_cell(Position(0, 0)).get_numeric_value() == 5
        assert cloned.get_cell(Position(1, 1)).get_numeric_value() == 7

    def test_multiple_games_different_difficulties(self) -> None:
        """Test creating multiple games with different difficulties."""
        player = Player("TestPlayer")

        easy_board = Board(BoardSize.standard_9x9())
        medium_board = Board(BoardSize.standard_9x9())
        hard_board = Board(BoardSize.standard_9x9())

        easy_game = Game(board=easy_board, player=player, difficulty=Difficulty.EASY)
        medium_game = Game(
            board=medium_board, player=player, difficulty=Difficulty.MEDIUM
        )
        hard_game = Game(board=hard_board, player=player, difficulty=Difficulty.HARD)

        assert easy_game.difficulty == Difficulty.EASY
        assert medium_game.difficulty == Difficulty.MEDIUM
        assert hard_game.difficulty == Difficulty.HARD
