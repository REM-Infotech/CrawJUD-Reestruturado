"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING

import pandas as pd
from pandas import Timestamp

from crawjud.addons.auth import authenticator
from crawjud.addons.elements import ElementsBot
from crawjud.addons.search import SearchBot
from crawjud.addons.webdriver import DriverBot

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

    from crawjud.types.elements import type_elements


class CrawJUD:
    """CrawJUD bot core class.

    Manages the initialization, setup, and authentication processes
    of the CrawJUD bot.
    """

    bot_data: dict[str, str]
    start_time: float
    driver: WebDriver
    search: SearchBot
    senhatoken: str
    elements: type_elements
    pid: str
    pos: int
    is_stoped: bool

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Inicializador do núcleo."""
        self.start_time = perf_counter()

        for k, v in list(kwargs.items()):
            setattr(self, k, v)

        # Instancia o WebDriver
        driverbot = DriverBot(kwargs.get("preferred_browser", "chrome"))()
        self.driver = driverbot[0]
        self.wait = driverbot[1]

        self.elements = ElementsBot().config().bot_elements

        # Autenticação com os sistemas
        auth = authenticator(kwargs.get("system"))(
            username=kwargs.get("username"),
            password=kwargs.get("password"),
            driver=self.driver,
            wait=self.wait,
        )
        auth.auth()

    def open_cfg(self) -> None:
        """Abre as configurações de execução."""
        with Path(self.path_config).resolve().open("r") as f:
            data = json.loads(f.read())
            for k, v in list(data.items()):
                setattr(self, k, v)

    def dataFrame(self) -> list[dict[str, str]]:  # noqa: N802
        """Convert an Excel file to a list of dictionaries with formatted data.

        Reads an Excel file, processes the data by formatting dates and floats,
        and returns the data as a list of dictionaries.

        Returns:
            list[dict[str, str]]: A record list from the processed Excel file.

        Raises:
            FileNotFoundError: If the target file does not exist.
            ValueError: For problems reading the file.

        """
        input_file = Path(self.output_dir_path).joinpath(self.xlsx).resolve()

        df = pd.read_excel(input_file)
        df.columns = df.columns.str.upper()

        for col in df.columns:
            df[col] = df[col].apply(lambda x: (x.strftime("%d/%m/%Y") if isinstance(x, (datetime, Timestamp)) else x))

        for col in df.select_dtypes(include=["float"]).columns:
            df[col] = df[col].apply(lambda x: f"{x:.2f}".replace(".", ","))

        vars_df = []

        df_dicted = df.to_dict(orient="records")
        for item in df_dicted:
            for key, value in item.items():
                if str(value) == "nan":
                    item[key] = None
            vars_df.append(item)

        return vars_df
        # self.search = SearchBot.setup()
