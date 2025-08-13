# noqa: D104
import importlib

from crawjud_app.bots import pje, resources

__all__ = ["pje", "resources"]


def _init_addons() -> None:
    importlib.import_module("crawjud_app.addons.auth", __package__)
    importlib.import_module("crawjud_app.addons.search", __package__)


_init_addons()
