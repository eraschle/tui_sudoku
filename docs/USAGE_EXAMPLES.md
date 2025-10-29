# Infrastructure Layer Usage Examples

## Quick Start

### Import the Components

```python
from sudoku.infrastructure import (
    create_backtracking_generator,
    create_backtracking_solver,
    create_sudoku_validator,
)
```

## Complete Workflow Example

```python
# Initialize components
generator = create_backtracking_generator()
solver = create_backtracking_solver()
validator = create_sudoku_validator()

# Generate a 9x9 puzzle
puzzle = generator.generate(
    box_width=3,
    box_height=3,
    difficulty="MEDIUM"
)

# Validate the generated puzzle
is_valid = validator.is_board_valid(puzzle, box_width=3, box_height=3)
print(f"Generated puzzle is valid: {is_valid}")

# Try to make a move
if validator.is_valid_move(puzzle, row=0, col=0, num=5, box_width=3, box_height=3):
    puzzle[0][0] = 5
    print("Move accepted!")
else:
    print("Invalid move!")

# Solve the puzzle
solution = solver.solve(puzzle, box_width=3, box_height=3)
if solution:
    print("Puzzle solved!")
    
    # Check if solution is complete
    is_complete = validator.is_board_complete(
        solution, box_width=3, box_height=3
    )
    print(f"Solution is complete: {is_complete}")
```

## Board Generation Examples

### Generate 9x9 Boards (Standard Sudoku)

```python
generator = create_backtracking_generator()

# Easy puzzle
easy_puzzle = generator.generate(
    box_width=3,
    box_height=3,
    difficulty="EASY"
)

# Medium puzzle
medium_puzzle = generator.generate(
    box_width=3,
    box_height=3,
    difficulty="MEDIUM"
)

# Hard puzzle
hard_puzzle = generator.generate(
    box_width=3,
    box_height=3,
    difficulty="HARD"
)
```

### Generate 6x6 Boards (Mini Sudoku)

```python
generator = create_backtracking_generator()

# 6x6 puzzle (3x2 boxes)
mini_puzzle = generator.generate(
    box_width=3,
    box_height=2,
    difficulty="EASY"
)
```

## Solver Examples

### Solve a Puzzle

```python
solver = create_backtracking_solver()

# Solve and get the solution
solution = solver.solve(puzzle, box_width=3, box_height=3)

if solution is None:
    print("No solution exists!")
else:
    print("Solution found!")
    # solution is a 2D list with the completed board
```

### Check Solution Uniqueness

```python
solver = create_backtracking_solver()

# Check if puzzle has exactly one solution
has_unique = solver.has_unique_solution(
    puzzle, box_width=3, box_height=3
)

if has_unique:
    print("Puzzle has a unique solution")
else:
    print("Puzzle has multiple solutions or no solution")
```

## Validator Examples

### Validate a Move Before Making It

```python
validator = create_sudoku_validator()

row, col, num = 0, 0, 5

if validator.is_valid_move(puzzle, row, col, num, box_width=3, box_height=3):
    puzzle[row][col] = num
    print(f"Placed {num} at ({row}, {col})")
else:
    print(f"Cannot place {num} at ({row}, {col})")
```

### Check Board Validity

```python
validator = create_sudoku_validator()

# Check if current board state is valid
# (allows empty cells, just checks no conflicts)
is_valid = validator.is_board_valid(board, box_width=3, box_height=3)

if is_valid:
    print("Board state is valid")
else:
    print("Board has conflicts!")
```

### Check Board Completeness

```python
validator = create_sudoku_validator()

# Check if board is completely filled and valid
is_complete = validator.is_board_complete(board, box_width=3, box_height=3)

if is_complete:
    print("Puzzle is solved!")
else:
    print("Puzzle is not complete yet")
```

## Advanced Usage

### Custom Game Loop

```python
def play_sudoku():
    # Setup
    generator = create_backtracking_generator()
    validator = create_sudoku_validator()
    
    # Generate puzzle
    board = generator.generate(
        box_width=3, box_height=3, difficulty="MEDIUM"
    )
    
    # Game loop
    while not validator.is_board_complete(board, 3, 3):
        # Display board
        display_board(board)
        
        # Get user input
        row, col, num = get_user_input()
        
        # Validate and make move
        if validator.is_valid_move(board, row, col, num, 3, 3):
            board[row][col] = num
            print("Good move!")
        else:
            print("Invalid move! Try again.")
    
    print("Congratulations! Puzzle solved!")

def display_board(board):
    for row in board:
        print(" ".join(str(cell) if cell != 0 else "." for cell in row))

def get_user_input():
    # Implement user input logic
    pass
```

### Hint System

```python
def get_hint(puzzle):
    """Get a hint by solving one cell."""
    solver = create_backtracking_solver()
    
    # Solve the puzzle
    solution = solver.solve(puzzle, box_width=3, box_height=3)
    
    if not solution:
        return None
    
    # Find first empty cell and return its solution
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] == 0:
                return (row, col, solution[row][col])
    
    return None

# Usage
hint = get_hint(puzzle)
if hint:
    row, col, num = hint
    print(f"Hint: Try placing {num} at ({row}, {col})")
```

### Puzzle Generator with Guarantee

```python
def generate_valid_puzzle(difficulty="MEDIUM", max_attempts=10):
    """Generate a puzzle and ensure it has a unique solution."""
    generator = create_backtracking_generator()
    solver = create_backtracking_solver()
    
    for attempt in range(max_attempts):
        puzzle = generator.generate(
            box_width=3, box_height=3, difficulty=difficulty
        )
        
        if solver.has_unique_solution(puzzle, 3, 3):
            return puzzle
    
    raise ValueError("Could not generate valid puzzle")

# Usage
puzzle = generate_valid_puzzle(difficulty="HARD")
```

## Error Handling

```python
from sudoku.infrastructure import create_backtracking_generator

generator = create_backtracking_generator()

try:
    # Invalid difficulty
    puzzle = generator.generate(
        box_width=3, box_height=3, difficulty="IMPOSSIBLE"
    )
except ValueError as e:
    print(f"Error: {e}")
    # Error: Invalid difficulty: IMPOSSIBLE. Must be one of ['EASY', 'MEDIUM', 'HARD']
```

## Board Format

All components work with 2D lists where:
- Empty cells are represented by `0`
- Filled cells contain integers from `1` to `board_size`
- Board size = `box_width × box_height`

Example 4x4 board:
```python
board = [
    [1, 0, 0, 4],
    [0, 4, 1, 0],
    [0, 1, 4, 0],
    [4, 0, 0, 1],
]
```

Example 9x9 board:
```python
board = [
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
```
