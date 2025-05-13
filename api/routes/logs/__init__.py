"""Module for the logs routes."""

from importlib import import_module

from quart import Blueprint

logsbot = Blueprint("logsbot", __name__)


def imports() -> None:
    """Import the routes for the logs module."""
    import_module(".route", __package__)
    import_module(".logbot", __package__)


imports()
