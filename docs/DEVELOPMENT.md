# Development Guide

## Quick Start

### Installation

```bash
# Install in development mode with all dev dependencies
pip install -e ".[dev]"

# Or using uv (faster)
uv pip install -e ".[dev]"
```

### Running the Application

```bash
# Using the installed command
sudoku

# Or run directly from source
python -m sudoku.main
```

## Development Workflow

### Code Quality Checks

```bash
# Format code (auto-fix)
ruff format .

# Lint code (check only)
ruff check .

# Lint with auto-fix
ruff check --fix .

# Type checking
mypy src/sudoku

# Run all checks together
ruff check . && ruff format . && mypy src/sudoku && echo "All checks passed!"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sudoku --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Run specific test file
pytest tests/test_specific.py

# Run with verbose output
pytest -v

# Run fast tests only (skip slow tests)
pytest -m "not slow"
```

### Project Structure

```
src/sudoku/
├── __init__.py          # Package initialization
├── main.py              # Application entry point
├── sudoku.css           # Textual CSS stylesheet
├── domain/              # Core business logic
│   ├── entities/       # Game, Board, Cell, Player
│   ├── value_objects/  # Difficulty, Position, CellValue
│   ├── protocols/      # Interfaces
│   └── services/       # Domain services
├── application/         # Use cases and DTOs
│   ├── use_cases/      # Business operations
│   └── dto/            # Data transfer objects
├── infrastructure/      # External implementations
│   ├── generators/     # Board generation
│   ├── validators/     # Board validation
│   ├── solvers/        # Solving algorithms
│   └── persistence/    # File-based storage
└── presentation/        # TUI interface (to be implemented)
    └── widgets/        # Textual widgets
```

## Configuration Files

### pyproject.toml

Central configuration for:
- Project metadata and dependencies
- Build system (hatchling)
- Tool configurations (pytest, mypy, ruff, coverage)

### Key Settings

**Python Version**: >= 3.11

**Dependencies**:
- textual >= 0.47.0 (TUI framework)

**Dev Dependencies**:
- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- mypy >= 1.7.0
- ruff >= 0.1.6

## Common Tasks

### Adding a New Dependency

```bash
# Edit pyproject.toml, add to dependencies list
# Then reinstall
pip install -e ".[dev]"
```

### Creating a New Module

1. Create the Python file in the appropriate layer
2. Add proper docstrings and type hints
3. Update `__init__.py` if needed
4. Add tests in `tests/` directory
5. Run quality checks

### Running Specific Checks

```bash
# Check specific file
ruff check src/sudoku/main.py
mypy src/sudoku/main.py

# Check specific directory
ruff check src/sudoku/domain/
mypy src/sudoku/domain/
```

## Troubleshooting

### Import Errors

If you get import errors:
```bash
# Reinstall in development mode
pip install -e .
```

### Type Checking Issues

```bash
# Clear mypy cache
rm -rf .mypy_cache
mypy src/sudoku
```

### Test Failures

```bash
# Run with verbose output and show print statements
pytest -vv -s

# Run specific test
pytest tests/test_file.py::test_function_name -v
```

## Git Workflow

```bash
# Before committing
ruff check . && ruff format . && mypy src/sudoku && pytest

# If all checks pass, commit
git add .
git commit -m "Your commit message"
```

## Release Process

1. Update version in `src/sudoku/__init__.py` and `pyproject.toml`
2. Run all tests and checks
3. Build the package: `python -m build`
4. Tag the release: `git tag v0.x.x`
5. Push changes and tags

## Performance Profiling

```bash
# Profile the application
python -m cProfile -o profile.stats -m sudoku.main

# Analyze profile
python -m pstats profile.stats
```

## Debugging

### Using pdb

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use Python 3.7+ breakpoint
breakpoint()
```

### Running with debugger

```bash
python -m pdb -m sudoku.main
```
