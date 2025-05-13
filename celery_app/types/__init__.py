"""Módulo de tipos do celery app."""

from os import PathLike
from typing import Union

# Definição do tipo "StrPath"
StrPath = Union[str, PathLike]
