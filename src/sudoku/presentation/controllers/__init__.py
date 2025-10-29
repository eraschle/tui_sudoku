"""Controllers for coordinating application flow.

This module provides controllers that act as intermediaries between
the UI layer and the application use cases.
"""

from .app_controller import AppController


__all__ = [
    "AppController",
]
