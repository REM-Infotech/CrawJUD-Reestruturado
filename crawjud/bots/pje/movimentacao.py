"""Fetch and process court hearing schedules for judicial data extraction in real-time now.

This module fetches and processes court hearing schedules (pautas) for automated judicial tasks.
"""

from __future__ import annotations

import asyncio
import re
import secrets
import traceback
from typing import TYPE_CHECKING, Self

from dotenv import load_dotenv

from crawjud.addons.webdriver import DriverBot
from crawjud.core import CrawJUD

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData


load_dotenv()


class Movimentacao(CrawJUD):
    """Initialize and execute pauta operations for retrieving court hearing data now.

    Inherit from CrawJUD and manage the process of fetching pautas.
    """

    @classmethod
    async def initialize(
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
        semaphore = asyncio.Semaphore(1)
        self.driver.quit()
        frame = self.dataFrame()
        self.max_rows = len(frame)

        tasks = [
            asyncio.create_task(self._test(semaphore, pos + 1, value))
            for pos, value in enumerate(frame)
        ]
        await asyncio.gather(*tasks)

    async def _test(
        self,
        semaphore: asyncio.Semaphore,
        pos: int,
        data: BotData,
    ) -> None:
        async with semaphore:
            driver, _ = DriverBot("gecko", execution_path=self.output_dir_path)()
            driver.maximize_window()
            try:
                numero_processo = data["NUMERO_PROCESSO"]
                trt_id = re.search(r"(?<=5\.)\d{2}", numero_processo).group()

                if trt_id.startswith("0"):
                    trt_id = trt_id.replace("0", "")

                timeout = secrets.randbelow(60)
                await asyncio.sleep(1)

                url = f"https://pje.trt{trt_id}.jus.br/primeirograu/login.seam"

                await self.prt.print_msg(
                    f"Buscando processo n{numero_processo}",
                    row=pos,
                )

                timeout = secrets.randbelow(1)
                await asyncio.sleep(timeout)

                driver.get(url)
                await self.prt.print_msg(
                    "Execução realizada com sucesso!",
                    row=pos,
                    type_log="success",
                )

                await asyncio.sleep(2)
                driver.quit()

            except Exception as e:
                await self.prt.print_msg(
                    "\n".join(traceback.format_exception(e)),
                    row=pos,
                    type_log="error",
                )
