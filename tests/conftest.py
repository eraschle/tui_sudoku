"""Shared pytest fixtures for the Sudoku test suite.

This module provides common fixtures used across multiple test modules,
promoting code reuse and consistency in testing.
"""

import pytest

from sudoku.domain.entities.board import Board
from sudoku.domain.entities.game import Game
from sudoku.domain.entities.player import Player
from sudoku.domain.value_objects.board_size import BoardSize
from sudoku.domain.value_objects.difficulty import Difficulty
from sudoku.domain.value_objects.position import Position


@pytest.fixture
def board_size_9x9() -> BoardSize:
    """Create a standard 9x9 board size.

    Returns:
        BoardSize instance for 9x9 board with 3x3 boxes.
    """
    return BoardSize.standard_9x9()


@pytest.fixture
def board_size_6x6() -> BoardSize:
    """Create a mini 6x6 board size.

    Returns:
        BoardSize instance for 6x6 board with 2x3 boxes.
    """
    return BoardSize.mini_6x6()


@pytest.fixture
def empty_board_9x9(board_size_9x9: BoardSize) -> Board:
    """Create an empty 9x9 board.

    Args:
        board_size_9x9: The 9x9 board size fixture.

    Returns:
        Empty Board instance.
    """
    return Board(board_size_9x9)


@pytest.fixture
def empty_board_6x6(board_size_6x6: BoardSize) -> Board:
    """Create an empty 6x6 board.

    Args:
        board_size_6x6: The 6x6 board size fixture.

    Returns:
        Empty Board instance.
    """
    return Board(board_size_6x6)


@pytest.fixture
def simple_player() -> Player:
    """Create a simple test player.

    Returns:
        Player instance with name 'TestPlayer'.
    """
    return Player("TestPlayer")


@pytest.fixture
def sample_game(empty_board_9x9: Board, simple_player: Player) -> Game:
    """Create a sample game instance.

    Args:
        empty_board_9x9: Empty 9x9 board fixture.
        simple_player: Simple player fixture.

    Returns:
        Game instance in NOT_STARTED state.
    """
    return Game(
        board=empty_board_9x9,
        player=simple_player,
        difficulty=Difficulty.MEDIUM,
    )


@pytest.fixture
def partially_filled_board_9x9(board_size_9x9: BoardSize) -> Board:
    """Create a 9x9 board with some cells filled.

    Creates a board with a few values filled in to test validation logic.

    Args:
        board_size_9x9: The 9x9 board size fixture.

    Returns:
        Partially filled Board instance.
    """
    board = Board(board_size_9x9)
    # Fill some cells
    board.set_cell_value(Position(0, 0), 5, is_fixed=True)
    board.set_cell_value(Position(0, 1), 3, is_fixed=True)
    board.set_cell_value(Position(0, 2), 4, is_fixed=True)
    board.set_cell_value(Position(1, 0), 6, is_fixed=True)
    board.set_cell_value(Position(1, 1), 7, is_fixed=True)
    return board


@pytest.fixture
def valid_9x9_puzzle() -> list[list[int]]:
    """Create a valid 9x9 Sudoku puzzle (partially filled).

    Returns:
        2D list representing a valid puzzle with 0 for empty cells.
    """
    return [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]


@pytest.fixture
def solved_9x9_puzzle() -> list[list[int]]:
    """Create a complete and valid solution for the 9x9 puzzle.

    Returns:
        2D list representing a solved 9x9 Sudoku board.
    """
    return [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]


@pytest.fixture
def invalid_9x9_board() -> list[list[int]]:
    """Create an invalid 9x9 board (duplicate in row).

    Returns:
        2D list representing an invalid board with duplicate values.
    """
    return [
        [5, 5, 0, 0, 0, 0, 0, 0, 0],  # Duplicate 5 in first row
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]


@pytest.fixture
def valid_6x6_puzzle() -> list[list[int]]:
    """Create a valid 6x6 Sudoku puzzle (partially filled).

    Returns:
        2D list representing a valid 6x6 puzzle with 0 for empty cells.
    """
    return [
        [5, 6, 0, 3, 4, 0],
        [1, 4, 0, 6, 0, 2],
        [2, 0, 1, 0, 0, 5],
        [0, 0, 0, 1, 2, 3],
        [0, 2, 6, 5, 1, 4],
        [4, 0, 5, 2, 3, 6],
    ]
