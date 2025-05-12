"""Core module for the CrawJUD bot.

This module provides the main functionalities and configurations
for the CrawJUD bot, including setup and authentication processes.
"""

from __future__ import annotations

import json
import logging
import platform
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd
from openai import OpenAI
from pytz import timezone

from crawjud.bot.common.exceptions import StartError

if platform.system() == "Windows":
    from pywinauto import Application

from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.bot.common import ExecutionError
from crawjud.bot.shared import PropertiesCrawJUD
from crawjud.types import TypeHint

__all__ = [
    pd,
    OpenAI,
    "Application",
    Group,
    Live,
    Panel,
    Progress,
    TaskID,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    WebDriver,
    WebDriverWait,
    Chrome,
    Options,
    Service,
]
logger = logging.getLogger(__name__)


class CrawJUD(PropertiesCrawJUD):
    """CrawJUD bot core class.

    Manages the initialization, setup, and authentication processes
    of the CrawJUD bot.
    """

    settings = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    def __init__(self) -> None:
        """Initialize the CrawJUD instance with provided arguments.

        Raises:
            StartError: If an error occurs during the setup process.

        """
        super().__init__()

    def __getattr__(self, nome: str) -> TypeHint:
        """Retrieve an attribute dynamically.

        Attempts to get the attribute 'nome' from the keyword arguments.
        If not found, it searches in the CrawJUD class dictionary and
        then in the PropertiesCrawJUD class dictionaries.

        Args:
            nome (str): The name of the attribute to retrieve.

        Returns:
            TypeHint: The value of the requested attribute.

        """
        item = self.kwargs.get(nome, None)

        if not item:
            item = CrawJUD.__dict__.get(nome, None)

            if not item:
                item = PropertiesCrawJUD.kwargs_.get(nome, None)

        return item

    def setup(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Set up the bot by loading configuration and preparing the environment.

        Performs the following steps:
        1. Loads configuration from a JSON file specified by `self.path_args`.
        2. Sets attributes based on the loaded configuration.
        3. Initializes logging and output directory paths.
        4. Prepares a list of arguments for the system.
        5. Installs certificates if `self.name_cert` is specified.
        6. Creates Excel files for logging successes and errors.
        7. Parses date strings into datetime objects if `self.xlsx` is not specified.
        8. Sets the state or client attribute.
        9. Launches the driver.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        self.row = 0

        try:
            self.kwargs = kwargs
            list_kwargs = list(kwargs.items())
            for key, value in list_kwargs:
                if key == "path_args":
                    value = Path(value).resolve()

                setattr(self, key, value)

            with open(self.path_args) as f:
                json_f: dict[str, str | int] = json.load(f)

                self.kwargs = json_f

                for key, value in json_f.items():
                    setattr(self, key, value)

            self.state_or_client = self.state if self.state is not None else self.client
            if " - " in self.state_or_client:
                self.state_or_client = self.state_or_client.split(" - ")[0]

        except Exception as e:
            raise StartError(e) from e

        try:
            self.init_log_bot()
            self.message = "Inicializando robô"
            self.type_log = "log"
            self.prt()

            self.output_dir_path = Path(self.path_args).parent.resolve()
            # time.sleep(10)
            self.list_args = [
                "--ignore-ssl-errors=yes",
                "--ignore-certificate-errors",
                "--display=:99",
                "--window-size=1600,900",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--kiosk-printing",
            ]
            if self.name_cert:
                self.install_cert()

            time_xlsx = datetime.now(timezone("America/Manaus")).strftime("%d-%m-%y")

            self.path = Path(self.output_dir_path).joinpath(f"Sucessos - PID {self.pid} {time_xlsx}.xlsx").resolve()

            self.path_erro = Path(self.output_dir_path).joinpath(f"Erros - PID {self.pid} {time_xlsx}.xlsx").resolve()

            self.name_colunas = self.MakeXlsx.make_output("sucesso", self.path)
            self.MakeXlsx.make_output("erro", self.path_erro)

            if not self.xlsx and self.data_inicio is not None:
                self.data_inicio = datetime.strptime(self.data_inicio, "%Y-%m-%d")
                self.data_fim = datetime.strptime(self.data_fim, "%Y-%m-%d")

            driver, wait = self.driver_launch()

            self.driver = driver
            self.wait = wait

            self.elements = self.ElementsBot.config().bot_elements

        except Exception as e:
            self.row = 0
            self.message = "Falha ao iniciar"
            self.type_log = "error"
            self.prt(status="Falha ao iniciar")

            if self.driver:
                self.driver.quit()

            raise e

    def auth_bot(self) -> None:
        """Authenticate the bot using the specified login method.

        Checks if the bot is logged in using the provided authentication method.
        Logs a success message if login is successful.
        Quits the driver, logs an error message, and raises an exception if login fails.

        Raises:
            ExecutionError: If the login fails.

        """
        try:
            if self.login_method:
                chk_logged = self.AuthBot()
                if chk_logged is True:
                    self.message = "Login efetuado com sucesso!"
                    self.type_log = "log"
                    self.prt()

                elif chk_logged is False:
                    self.driver.quit()
                    self.message = "Erro ao realizar login"
                    self.type_log = "error"
                    self.prt()
                    raise ExecutionError(message=self.message)

        except Exception as e:
            err = traceback.format_exc()
            logger.exception(err)
            self.row = 0
            self.message = "Erro ao realizar login"
            self.type_log = "error"

            self.prt()
            self.prt(status="Falha ao iniciar")
            if self.driver:
                self.driver.quit()

            raise e
