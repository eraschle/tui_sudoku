"""Board renderers for Sudoku TUI."""

from sudoku.infrastructure.tui.renderers.board_renderer import BoardRenderer
from sudoku.infrastructure.tui.renderers.board_renderers import (
    CompactBoardRenderer,
    StandardBoardRenderer,
)


def create_board_renderer(style: str = "standard", **kwargs) -> BoardRenderer:
    """Factory function to create board renderers.

    Args:
        style: Rendering style ('standard', 'compact').
        **kwargs: Additional arguments passed to the renderer constructor.

    Returns:
        Appropriate renderer for the style.

    Raises:
        ValueError: If style is unknown.
    """
    if style == "standard":
        return StandardBoardRenderer(**kwargs)
    elif style == "compact":
        return CompactBoardRenderer()
    else:
        raise ValueError(f"Unknown renderer style: {style}")


__all__ = [
    "BoardRenderer",
    "StandardBoardRenderer",
    "CompactBoardRenderer",
    "create_board_renderer",
]
