"""Sudoku TUI Application.

A terminal-based Sudoku game built following Clean Architecture principles,
SOLID design patterns, and Python best practices.

Architecture Layers:
- Domain: Core business logic and entities
- Application: Use cases and DTOs
- Infrastructure: External implementations (persistence, validation, generation)
- Presentation: TUI interface (to be implemented)

Example:
    >>> from sudoku.main import main
    >>> main()  # Start the application
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = [
    "__author__",
    "__license__",
    "__version__",
]
