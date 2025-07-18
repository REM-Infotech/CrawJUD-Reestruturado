"""Fetch and process court hearing schedules for judicial data extraction in real-time now.

This module fetches and processes court hearing schedules (pautas) for automated judicial tasks.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Self

from crawjud.core import CrawJUD

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData


class Movimentacao(CrawJUD):
    """Initialize and execute pauta operations for retrieving court hearing data now.

    Inherit from CrawJUD and manage the process of fetching pautas.
    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize a new Pauta instance with provided arguments now.

        Args:
            *args (str|int): Positional arguments.
            **kwargs (str|int): Keyword arguments.

        Returns:
            Self: A new instance of Pauta.

        """
        return cls(*args, **kwargs)

    async def execution(self) -> None:
        """Execute the main process loop to retrieve pautas until data range is covered now.

        This method continuously processes each court hearing date and handles errors.
        """
        semaphore = asyncio.Semaphore(27)
        main_window = self.driver.current_window_handle  # noqa: F841

        frame = self.dataFrame()
        self.max_rows = len(frame)

        tasks = [
            asyncio.create_task(self._test(semaphore, pos, value))
            for pos, value in enumerate(frame)
        ]
        await asyncio.gather(*tasks)

    async def _test(
        self, semaphore: asyncio.Semaphore, pos: int, data: BotData
    ) -> None:
        async with semaphore:
            driver = self.driver
            driver.switch_to.new_window("window")
