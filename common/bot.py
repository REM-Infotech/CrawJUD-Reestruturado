# noqa: D100
from typing import Any, Self

from crawjud.core import CrawJUD


class ClassBot(CrawJUD):  # noqa: D101
    @classmethod
    def initialize(cls, *args: Any, **kwargs: Any) -> Self:  # noqa: D102
        raise NotImplementedError("Subclasses must implement this method")

    def execution(self) -> None:  # noqa: D102
        raise NotImplementedError("Subclasses must implement this method")
