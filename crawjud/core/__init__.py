"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Any, AnyStr

import pandas as pd
from pandas import Timestamp
from pytz import timezone

from crawjud.addons.auth import authenticator
from crawjud.addons.elements import ElementsBot
from crawjud.addons.make_templates import MakeTemplates
from crawjud.addons.webdriver import DriverBot
from crawjud.exceptions.bot import StartError
from crawjud.types import StrPath

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
    search: Any

    elements: type_elements
    pid: str
    pos: int
    is_stoped: bool
    output_dir_path: StrPath
    config_bot: dict[str, AnyStr]
    system: str
    state_or_client: str

    # Variáveis de autenticação/protocolo
    username: str
    password: str
    senhatoken: str

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Inicializador do núcleo.

        Raises:
            StartError: Exception de erro de inicialização.

        """
        try:
            self.start_time = perf_counter()
            self.output_dir_path = kwargs.get("path_config")
            for k, v in list(kwargs.items()):
                if "bot" in k:
                    setattr(self, k.split("_")[1], v)
                    continue

                setattr(self, k, v)

            self.open_cfg()

            # Instancia o WebDriver
            driverbot = DriverBot(kwargs.get("preferred_browser", "chrome"), execution_path=self.output_dir_path)()
            self.driver = driverbot[0]
            self.wait = driverbot[1]

            self.elements = ElementsBot.config(
                system=self.system,
                state_or_client=self.state_or_client,
                **self.config_bot,
            ).bot_elements

            # Autenticação com os sistemas
            auth = authenticator(self.system)(
                username=self.username,
                password=self.password,
                driver=self.driver,
                wait=self.wait,
                system=self.system,
                elements=self.elements,
            )
            auth.auth()

            # Criação de planilhas template
            self.make_templates()

        except Exception as e:
            raise StartError(exception=e) from e

    def make_templates(self) -> None:
        """Criação de planilhas de output do robô."""
        time_xlsx = datetime.now(timezone("America/Manaus")).strftime("%d-%m-%y")
        planilha_args = [
            {
                "PATH_OUTPUT": self.output_dir_path,
                "TEMPLATE_NAME": f"Sucessos - PID {self.pid} {time_xlsx}.xlsx",
                "TEMPLATE_TYPE": "sucesso",
                "BOT_NAME": self.bot_name,
            },
            {
                "PATH_OUTPUT": self.output_dir_path,
                "TEMPLATE_NAME": f"Erros - PID {self.pid} {time_xlsx}.xlsx",
                "TEMPLATE_TYPE": "erro",
                "BOT_NAME": self.bot_name,
            },
        ]

        for item in planilha_args:
            attribute_name, attribute_val = MakeTemplates.constructor(**item).make()
            setattr(self, attribute_name, attribute_val)

    def open_cfg(self) -> None:
        """Abre as configurações de execução."""
        with Path(self.path_config).resolve().open("r") as f:
            data: dict[str, AnyStr] = json.loads(f.read())
            self.config_bot = data
            for k, v in list(data.items()):
                if k == "state" or k == "client":
                    self.state_or_client = v

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
