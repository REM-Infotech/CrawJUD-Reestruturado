# noqa: D100

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from dotenv import load_dotenv

from crawjud.addons.search import SearchController  # noqa: F401
from crawjud.core import CrawJUD
from crawjud.types import BotData

if TYPE_CHECKING:
    from crawjud.types import BotData  # noqa: F401

load_dotenv(Path(__file__).parent.resolve().joinpath("../.env"))

TReturn = TypeVar("TReturn")


class ClassBot(CrawJUD):  # noqa:  D101
    @abstractmethod
    def execution(self) -> None: ...  # noqa: D102

    @abstractmethod
    def queue(self) -> None: ...  # noqa: D102
