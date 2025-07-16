"""Módulo de controle de variáveis CrawJUD."""

from __future__ import annotations

import json
import logging
import logging.config
from datetime import datetime
from logging import Logger
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, AnyStr

from pytz import timezone
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from addons.logger import dict_config
from addons.printlogs import PrintMessage
from crawjud.addons.auth import authenticator
from crawjud.addons.elements import ElementsBot
from crawjud.addons.interator import Interact
from crawjud.addons.make_templates import MakeTemplates
from crawjud.addons.search import search_engine
from crawjud.addons.webdriver import DriverBot
from crawjud.exceptions.bot import StartError
from crawjud.types import StrPath
from crawjud.types.elements import type_elements

if TYPE_CHECKING:
    from crawjud.addons.search.controller import SearchController


class Controller:
    """Classe de controle de variáveis CrawJUD."""

    row: int
    # Variáveis de dados/configuraçoes
    bot_data: dict[str, str]
    config_bot: dict[str, AnyStr]
    planilha_sucesso: StrPath
    # Variáveis de estado/posição/indice
    pid: str
    pos: int
    _is_stoped: bool
    start_time: float

    # Variáveis de verificações
    system: str
    typebot: str
    state_or_client: str
    preferred_browser: str = "chrome"
    total_rows: int

    # Variáveis de autenticação/protocolo
    username: str
    password: str
    senhatoken: str

    # Classes Globais
    elements: type_elements
    driver: WebDriver
    search: SearchController
    wait: WebDriverWait
    logger: Logger
    prt: PrintMessage

    # Variáveis de nome/caminho de arquivos/pastas
    xlsx: str
    input_file: StrPath
    output_dir_path: StrPath
    _cities_am: dict[str, str]
    _search: SearchController = None
    _data_bot: dict[str, str] = {}
    interact: Interact

    @property
    def max_rows(self) -> int:  # noqa: D102
        return self.prt.total_rows

    @max_rows.setter
    def max_rows(self, new_value: int) -> None:
        self.prt.total_rows = new_value

    @property
    def total_rows(self) -> int:  # noqa: D102
        return self.prt.total_rows

    @total_rows.setter
    def total_rows(self, new_value: int) -> None:
        self.prt.total_rows = new_value

    @property
    def is_stoped(self) -> bool:  # noqa: D102
        return self._is_stoped

    @is_stoped.setter
    def is_stoped(self, new_value: bool) -> None:
        self._is_stoped = new_value

    @property
    def bot_data(self) -> dict[str, str]:
        """Property bot data."""
        return self._data_bot

    @bot_data.setter
    def bot_data(self, new_data: dict[str, str]) -> None:
        """Property bot data."""
        self._data_bot = new_data

    @property
    def search_bot(self) -> SearchController:
        """Property para o searchbot."""
        return self._search

    @search_bot.setter
    def search_bot(self, instancia: SearchController) -> None:
        """Define a instância do searchbot."""
        self._search = instancia

    @property
    def cities_amazonas(self) -> dict[str, str]:  # noqa: N802
        """Return a dictionary categorizing Amazonas cities as 'Capital' or 'Interior'.

        Returns:
            dict[str, str]: City names with associated regional classification.

        """
        return self._cities_am

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Inicializador do núcleo.

        Raises:
            StartError: Exception de erro de inicialização.

        """
        try:
            with (
                Path(__file__)
                .parent.resolve()
                .joinpath("data_formatters", "cities_amazonas.json")
                .open("r") as f
            ):
                self._cities_am = json.loads(f.read())

            self.is_stoped = False
            self.start_time = perf_counter()
            self.output_dir_path = Path(kwargs.get("path_config")).parent.resolve()
            for k, v in list(kwargs.items()):
                if "bot" in k:
                    setattr(self, k.split("_")[1], v)
                    continue

                setattr(self, k, v)

            self.open_cfg()

            # Configuração do logger
            self.configure_logger()

            # Define o InputFile
            self.input_file = Path(self.output_dir_path).resolve().joinpath(self.xlsx)

            # Instancia o WebDriver
            self.configure_webdriver()

            # Instancia o elements
            self.elements = ElementsBot.config(
                system=self.system,
                state_or_client=self.state_or_client,
                **self.config_bot,
            ).bot_elements

            # Autenticação com os sistemas
            self.portal_authentication()

            # Criação de planilhas template
            self.make_templates()

            self.interact = Interact(driver=self.driver, wait=self.wait, pid=self.pid)

            # Configura o search_bot
            self.configure_searchengine()
        except Exception as e:
            raise StartError(exception=e) from e

    def configure_searchengine(self) -> None:
        """Configura a instância do search engine."""
        self.search_bot = search_engine(self.system)(
            typebot=self.name,
            driver=self.driver,
            wait=self.wait,
            elements=self.elements,
            bot_data=self.bot_data,
            interact=self.interact,
            prt=self.prt,
        )

    def portal_authentication(self) -> None:
        """Autenticação com os sistemas."""
        auth = authenticator(self.system)(
            username=self.username,
            password=self.password,
            driver=self.driver,
            wait=self.wait,
            system=self.system,
            elements=self.elements,
            prt=self.prt,
        )
        auth.auth()

    def configure_webdriver(self) -> None:
        """Instancia o WebDriver."""
        driverbot = DriverBot(
            self.preferred_browser, execution_path=self.output_dir_path
        )()
        self.driver = driverbot[0]
        self.wait = driverbot[1]

    def configure_logger(self) -> None:
        """Configura o logger."""
        log_path = str(self.output_dir_path.joinpath(f"{self.pid}.log"))

        config, logger_name = dict_config(
            LOG_LEVEL=logging.INFO, LOGGER_NAME=self.pid, FILELOG_PATH=log_path
        )
        logging.config.dictConfig(config)

        self.logger = logging.getLogger(logger_name)
        self.prt.logger = self.logger
        self.prt.total_rows = int(getattr(self, "total_rows", 0))

    def make_templates(self) -> None:
        """Criação de planilhas de output do robô."""
        time_xlsx = datetime.now(timezone("America/Manaus")).strftime("%d-%m-%y")
        planilha_args = [
            {
                "PATH_OUTPUT": self.output_dir_path,
                "TEMPLATE_NAME": f"Sucessos - PID {self.pid} {time_xlsx}.xlsx",
                "TEMPLATE_TYPE": "sucesso",
                "BOT_NAME": self.name,
            },
            {
                "PATH_OUTPUT": self.output_dir_path,
                "TEMPLATE_NAME": f"Erros - PID {self.pid} {time_xlsx}.xlsx",
                "TEMPLATE_TYPE": "erro",
                "BOT_NAME": self.name,
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
