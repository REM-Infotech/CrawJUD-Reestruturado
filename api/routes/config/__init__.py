"""Config blueprint for admin routes."""

from __future__ import annotations

from importlib import import_module

from quart import Blueprint

admin = Blueprint("admin", __name__)


def import_routes() -> None:
    """Import routes."""
    import_module(".users", __package__)


import_routes()
