"""Unit tests for the BacktrackingSolver.

This module tests the board solving logic including puzzle solving
and solution uniqueness checking.
"""


from sudoku.infrastructure.solvers.backtracking_solver import (
    BacktrackingSolver,
    create_backtracking_solver,
)


class TestBacktrackingSolverCreation:
    """Test solver instantiation."""

    def test_create_solver(self) -> None:
        """Test creating a backtracking solver instance."""
        solver = BacktrackingSolver()

        assert solver is not None

    def test_create_solver_via_factory(self) -> None:
        """Test creating solver using factory function."""
        solver = create_backtracking_solver()

        assert isinstance(solver, BacktrackingSolver)


class TestBacktrackingSolverSolve9x9:
    """Test solving 9x9 puzzles."""

    def test_solve_valid_puzzle(self, valid_9x9_puzzle: list[list[int]]) -> None:
        """Test solving a valid 9x9 puzzle."""
        solver = BacktrackingSolver()

        solution = solver.solve(valid_9x9_puzzle, box_width=3, box_height=3)

        assert solution is not None
        assert len(solution) == 9
        assert all(len(row) == 9 for row in solution)

    def test_solved_puzzle_has_no_zeros(
        self, valid_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that solved puzzle has no empty cells."""
        solver = BacktrackingSolver()

        solution = solver.solve(valid_9x9_puzzle, box_width=3, box_height=3)

        assert solution is not None
        for row in solution:
            assert 0 not in row

    def test_solved_puzzle_is_valid(
        self, valid_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that solution is valid (no duplicates)."""
        solver = BacktrackingSolver()

        solution = solver.solve(valid_9x9_puzzle, box_width=3, box_height=3)

        assert solution is not None

        # Check rows
        for row in solution:
            assert len(set(row)) == 9

        # Check columns
        for col_idx in range(9):
            column = [solution[row][col_idx] for row in range(9)]
            assert len(set(column)) == 9

    def test_solve_already_solved_puzzle(
        self, solved_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test solving an already solved puzzle returns the same board."""
        solver = BacktrackingSolver()

        solution = solver.solve(solved_9x9_puzzle, box_width=3, box_height=3)

        assert solution == solved_9x9_puzzle

    def test_solve_empty_board(self) -> None:
        """Test solving an empty board finds a solution."""
        solver = BacktrackingSolver()
        empty_board = [[0] * 9 for _ in range(9)]

        solution = solver.solve(empty_board, box_width=3, box_height=3)

        assert solution is not None
        assert all(0 not in row for row in solution)


class TestBacktrackingSolverSolve6x6:
    """Test solving 6x6 puzzles."""

    def test_solve_6x6_puzzle(self, valid_6x6_puzzle: list[list[int]]) -> None:
        """Test solving a valid 6x6 puzzle."""
        solver = BacktrackingSolver()

        solution = solver.solve(valid_6x6_puzzle, box_width=3, box_height=2)

        assert solution is not None
        assert len(solution) == 6
        assert all(len(row) == 6 for row in solution)

    def test_solved_6x6_has_no_zeros(
        self, valid_6x6_puzzle: list[list[int]]
    ) -> None:
        """Test that solved 6x6 puzzle has no empty cells."""
        solver = BacktrackingSolver()

        solution = solver.solve(valid_6x6_puzzle, box_width=3, box_height=2)

        assert solution is not None
        for row in solution:
            assert 0 not in row

    def test_solved_6x6_values_in_range(
        self, valid_6x6_puzzle: list[list[int]]
    ) -> None:
        """Test that solved 6x6 has values 1-6."""
        solver = BacktrackingSolver()

        solution = solver.solve(valid_6x6_puzzle, box_width=3, box_height=2)

        assert solution is not None
        for row in solution:
            for cell in row:
                assert 1 <= cell <= 6


class TestBacktrackingSolverUnsolvable:
    """Test behavior with unsolvable puzzles."""

    def test_solve_invalid_initial_board_returns_none(self) -> None:
        """Test that board with duplicate values in initial state returns None."""
        solver = BacktrackingSolver()

        # Create invalid puzzle with duplicates in first row
        invalid_board = [[1, 1, 0, 0, 0, 0, 0, 0, 0]] + [[0] * 9 for _ in range(8)]

        solution = solver.solve(invalid_board, box_width=3, box_height=3)

        # Should return None because initial board has duplicates
        assert solution is None

    def test_solve_board_with_column_duplicate_returns_none(self) -> None:
        """Test that board with duplicate in column returns None."""
        solver = BacktrackingSolver()

        # Create a board with duplicate in first column
        invalid_board = [
            [1, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0],  # Another 1 in column 0
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        solution = solver.solve(invalid_board, box_width=3, box_height=3)

        # Should return None because board has duplicate in column
        assert solution is None

    def test_solve_board_with_box_duplicate_returns_none(self) -> None:
        """Test that board with duplicate in box returns None."""
        solver = BacktrackingSolver()

        # Create a board with duplicate in first box (top-left 3x3)
        invalid_board = [
            [1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0],  # Another 1 in top-left box
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        solution = solver.solve(invalid_board, box_width=3, box_height=3)

        # Should return None because board has duplicate in box
        assert solution is None


class TestBacktrackingSolverUniqueSolution:
    """Test solution uniqueness checking."""

    def test_valid_puzzle_has_unique_solution(
        self, valid_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that valid puzzle has unique solution."""
        solver = BacktrackingSolver()

        has_unique = solver.has_unique_solution(
            valid_9x9_puzzle, box_width=3, box_height=3
        )

        assert has_unique

    def test_empty_board_has_multiple_solutions(self) -> None:
        """Test that empty board has multiple solutions."""
        solver = BacktrackingSolver()
        empty_board = [[0] * 9 for _ in range(9)]

        has_unique = solver.has_unique_solution(
            empty_board, box_width=3, box_height=3
        )

        assert not has_unique

    def test_solved_puzzle_has_unique_solution(
        self, solved_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that fully solved puzzle has unique solution."""
        solver = BacktrackingSolver()

        has_unique = solver.has_unique_solution(
            solved_9x9_puzzle, box_width=3, box_height=3
        )

        assert has_unique


class TestBacktrackingSolverOriginalNotModified:
    """Test that solving doesn't modify the original board."""

    def test_solve_does_not_modify_original(
        self, valid_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that solving creates a copy and doesn't modify original."""
        solver = BacktrackingSolver()
        original = [row[:] for row in valid_9x9_puzzle]

        solver.solve(valid_9x9_puzzle, box_width=3, box_height=3)

        assert valid_9x9_puzzle == original

    def test_uniqueness_check_does_not_modify_original(
        self, valid_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that uniqueness check doesn't modify original."""
        solver = BacktrackingSolver()
        original = [row[:] for row in valid_9x9_puzzle]

        solver.has_unique_solution(valid_9x9_puzzle, box_width=3, box_height=3)

        assert valid_9x9_puzzle == original


class TestBacktrackingSolverConsistency:
    """Test solver consistency."""

    def test_multiple_solves_give_same_result(
        self, valid_9x9_puzzle: list[list[int]]
    ) -> None:
        """Test that solving same puzzle multiple times gives same result."""
        solver = BacktrackingSolver()

        solution1 = solver.solve(valid_9x9_puzzle, box_width=3, box_height=3)
        solution2 = solver.solve(valid_9x9_puzzle, box_width=3, box_height=3)

        assert solution1 == solution2
