"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

import json
import logging
import logging.config
import traceback
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Any, AnyStr

import pandas as pd
from dotenv import load_dotenv
from pandas import Timestamp
from pytz import timezone

from crawjud.addons.auth import authenticator
from crawjud.addons.elements import ElementsBot
from crawjud.addons.interator import Interact
from crawjud.addons.logger import dict_config
from crawjud.addons.make_templates import MakeTemplates
from crawjud.addons.printlogs import PrintMessage
from crawjud.addons.search import search_engine
from crawjud.addons.webdriver import DriverBot
from crawjud.exceptions.bot import StartError
from crawjud.types import StrPath

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait

    from crawjud.addons.search import search_types
    from crawjud.types.elements import type_elements

load_dotenv(Path(__file__).parent.resolve().joinpath("../.env"))


class CrawJUD:
    """CrawJUD bot core class.

    Manages the initialization, setup, and authentication processes
    of the CrawJUD bot.
    """

    # Variáveis de dados/configuraçoes
    bot_data: dict[str, str]
    config_bot: dict[str, AnyStr]

    # Variáveis de estado/posição/indice
    pid: str
    pos: int
    is_stoped: bool
    start_time: float

    # Variáveis de verificações
    system: str
    typebot: str
    state_or_client: str
    preferred_browser: str = "gecko"
    total_rows: int

    # Variáveis de autenticação/protocolo
    username: str
    password: str
    senhatoken: str

    # Classes Globais
    elements: type_elements
    driver: WebDriver
    search: Any
    wait: WebDriverWait
    logger: logging.Logger
    prt: PrintMessage

    # Variáveis de nome/caminho de arquivos/pastas
    xlsx: str
    input_file: StrPath
    output_dir_path: StrPath
    _cities_am: dict[str, str]
    _search: search_types = None
    _data_bot: dict[str, str] = {}
    interact: Interact

    @property
    def bot_data(self) -> dict[str, str]:
        """Property bot data."""
        return self._data_bot

    @bot_data.setter
    def bot_data(self, new_data: dict[str, str]) -> None:
        """Property bot data."""
        self._data_bot = new_data

    @property
    def search_bot(self) -> search_types:
        """Property para o searchbot."""
        return self._search

    @search_bot.setter
    def search_bot(self, instancia: search_types) -> None:
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
            with Path(__file__).parent.resolve().joinpath("data_formatters", "cities_amazonas.json").open("r") as f:
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

            # Configuração do logger
            self.configure_logger()

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
        )
        auth.auth()

    def configure_webdriver(self) -> None:
        """Instancia o WebDriver."""
        driverbot = DriverBot(self.preferred_browser, execution_path=self.output_dir_path)()
        self.driver = driverbot[0]
        self.wait = driverbot[1]

    def configure_logger(self) -> None:
        """Configura o logger."""
        log_path = str(self.output_dir_path.joinpath(f"{self.pid}.log"))

        config, logger_name = dict_config(LOG_LEVEL=logging.INFO, LOGGER_NAME=self.pid, FILELOG_PATH=log_path)
        logging.config.dictConfig(config)

        self.logger = logging.getLogger(logger_name)
        self.prt = PrintMessage.constructor(logger=self.logger, total_rows=self.total_rows)

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
        df = pd.read_excel(self.input_file)
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

    def elawFormats(self, data: dict[str, str]) -> dict[str, str]:  # noqa: N802
        """Format a legal case dictionary according to pre-defined rules.

        Args:
            data (dict[str, str]): The raw data dictionary.

        Returns:
            dict[str, str]: The data formatted with proper types and values.

        Rules:
            - If the key is "TIPO_EMPRESA" and its value is "RÉU", update "TIPO_PARTE_CONTRARIA" to "Autor".
            - If the key is "COMARCA", update "CAPITAL_INTERIOR" based on the value using the cities_Amazonas method.
            - If the key is "DATA_LIMITE" and "DATA_INICIO" is not present, set "DATA_INICIO" to the value of "DATA_LIMITE".
            - If the value is an integer or float, format it to two decimal places and replace the decimal point with a clcomma.
            - If the key is "CNPJ_FAVORECIDO" and its value is empty, set it to "04.812.509/0001-90".

        """  # noqa: E501
        data_listed = list(data.items())
        for key, value in data_listed:
            if isinstance(value, str):
                if not value.strip():
                    data.pop(key)

            elif value is None:
                data.pop(key)

            if key.upper() == "TIPO_EMPRESA":
                data["TIPO_PARTE_CONTRARIA"] = "Autor"
                if value.upper() == "RÉU":
                    data["TIPO_PARTE_CONTRARIA"] = "Autor"

            elif key.upper() == "COMARCA":
                set_locale = self.cities_Amazonas.get(value, "Outro Estado")
                data["CAPITAL_INTERIOR"] = set_locale

            elif key == "DATA_LIMITE" and not data.get("DATA_INICIO"):
                data["DATA_INICIO"] = value

            elif isinstance(value, (int, float)):
                data[key] = f"{value:.2f}".replace(".", ",")

            elif key == "CNPJ_FAVORECIDO" and not value:
                data["CNPJ_FAVORECIDO"] = "04.812.509/0001-90"

        return data

    def tratamento_erros(self, exc: Exception, last_message: str = None) -> None:
        """Tratamento de erros dos robôs."""
        with suppress(Exception):
            windows = self.driver.window_handles
            if len(windows) == 0:
                self.configure_webdriver()
                self.portal_authentication()

        err_message = "\n".join(traceback.format_exception_only(exc))
        message = f"Erro de Operação: {err_message}"
        self.prt.print_msg(message=message, type_log="error")

        self.bot_data.update({"MOTIVO_ERRO": err_message})
        self.append_error(self.bot_data)
