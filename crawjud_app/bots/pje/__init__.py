# noqa: D104
from __future__ import annotations

import importlib

from . import resources

capa = importlib.import_module(".capa", __package__)

__all__ = ["capa", "resources"]
