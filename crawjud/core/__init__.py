"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

import json
import logging
import logging.config
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Any, AnyStr

import pandas as pd
from pandas import Timestamp
from pytz import timezone

from crawjud.addons.auth import authenticator
from crawjud.addons.elements import ElementsBot
from crawjud.addons.logger import dict_config
from crawjud.addons.make_templates import MakeTemplates
from crawjud.addons.webdriver import DriverBot
from crawjud.exceptions.bot import StartError
from crawjud.types import StrPath

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait

    from crawjud.types.elements import type_elements


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
    state_or_client: str

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

    # Variáveis de nome/caminho de arquivos/pastas
    xlsx: str
    input_file: StrPath
    output_dir_path: StrPath

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Inicializador do núcleo.

        Raises:
            StartError: Exception de erro de inicialização.

        """
        try:
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
            driverbot = DriverBot(kwargs.get("preferred_browser", "chrome"), execution_path=self.output_dir_path)()
            self.driver = driverbot[0]
            self.wait = driverbot[1]

            # Instancia o elements
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

            log_path = str(self.output_dir_path.joinpath(f"{self.pid}.log"))
            logging.config.dictConfig(dict_config(LOG_LEVEL=logging.INFO, LOGGER_NAME=self.pid, FILELOG_PATH=log_path))
            self.logger = logging.getLogger(self.pid)

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

    @property
    def cities_amazonas(self) -> dict[str, str]:  # noqa: N802
        """Return a dictionary categorizing Amazonas cities as 'Capital' or 'Interior'.

        Returns:
            dict[str, str]: City names with associated regional classification.

        """
        with Path(__file__).parent.resolve().joinpath("data_formatters", " cities_amazonas.json").open("r") as f:
            return json.loads(f.read())
