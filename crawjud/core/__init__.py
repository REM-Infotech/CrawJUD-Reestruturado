"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

import json
import logging
import logging.config
import re
import ssl
import subprocess
import traceback
import unicodedata
from contextlib import suppress
from datetime import datetime
from difflib import SequenceMatcher
from logging import Logger
from os import listdir, path
from pathlib import Path
from time import perf_counter, sleep
from typing import TYPE_CHECKING, AnyStr, Self

import pandas as pd
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
from pandas import Timestamp
from pytz import timezone
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from werkzeug.utils import secure_filename

from addons.logger import dict_config
from addons.printlogs import PrintMessage
from crawjud.addons.auth import AuthController
from crawjud.addons.elements import ElementsBot
from crawjud.addons.make_templates import MakeTemplates
from crawjud.addons.search import SearchController
from crawjud.core._dictionary import BotData
from crawjud.exceptions import AuthenticationError
from crawjud.exceptions.bot import ExecutionError, StartError
from crawjud.types import StrPath, TypeData
from crawjud.types.elements import type_elements
from models.logs import MessageLog
from webdriver import DriverBot

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData

load_dotenv(Path(__file__).parent.resolve().joinpath("../.env"))


class CrawJUD:
    """Classe de controle de variáveis CrawJUD."""

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

            self.prt.bot_instance = self
            self.status_log = "Inicializando"
            pid = kwargs.get("pid")
            self.prt.print_msg(
                "Configurando o núcleo...", pid, 0, "log", self.status_log
            )

            self.open_cfg()

            # Configuração do logger
            self.configure_logger()

            # Define o InputFile
            self.input_file = Path(self.output_dir_path).resolve().joinpath(self.xlsx)

            # Instancia o WebDriver
            self.configure_webdriver()

            if self.system.lower() != "pje":
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

            # Configura o search_bot
            if self.system.lower() != "pje":
                self.configure_searchengine()

            self.prt.print_msg(
                "Núcleo configurado.", self.pid, 0, "success", self.status_log
            )

        except Exception as e:
            raise StartError(exception=e) from e

    _row: int = 0
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
    state_or_client: str = None
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
    def bot_data(self) -> BotData:
        """Property bot data."""
        return self._data_bot

    @bot_data.setter
    def bot_data(self, new_data: BotData) -> None:
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
    def row(self) -> int:  # noqa: D102
        return self._row

    @row.setter
    def row(self, new_value: int) -> None:
        """Define o valor da variável row."""
        self._row = new_value

    @property
    def cities_amazonas(self) -> dict[str, str]:  # noqa: N802
        """Return a dictionary categorizing Amazonas cities as 'Capital' or 'Interior'.

        Returns:
            dict[str, str]: City names with associated regional classification.

        """
        return self._cities_am

    def configure_searchengine(self) -> None:
        """Configura a instância do search engine."""
        self.search_bot = SearchController.construct(
            system=self.system,
            typebot=self.name,
            driver=self.driver,
            wait=self.wait,
            elements=self.elements,
            bot_data=self.bot_data,
            prt=self.prt,
        )

    def portal_authentication(self) -> None:
        """Autenticação com os sistemas."""
        self.prt.print_msg(
            "Autenticando no sistema",
            row=0,
            type_log="log",
            status=self.status_log,
        )
        auth = AuthController.construct(
            system=self.system,
            username=self.username,
            password=self.password,
            driver=self.driver,
            wait=self.wait,
            elements=self.elements,
            prt=self.prt,
        )
        is_logged = auth.auth()

        if not is_logged:
            self.prt.print_msg(
                "Erro ao autenticar no sistema, verifique as credenciais.",
                row=0,
                type_log="error",
                status=self.status_log,
            )
            raise AuthenticationError(
                "Erro ao autenticar no sistema, verifique as credenciais."
            )

        self.prt.print_msg(
            "Autenticação realizada com sucesso",
            row=0,
            type_log="success",
            status=self.status_log,
        )

    def configure_webdriver(self) -> None:
        """Instancia o WebDriver."""
        self.prt.print_msg(
            "Inicializando webdriver",
            row=0,
            type_log="log",
            status=self.status_log,
        )
        self.driver = DriverBot(
            self.preferred_browser, execution_path=self.output_dir_path
        )
        self.wait = self.driver.wait
        self.prt.print_msg(
            "Webdriver inicializado",
            row=0,
            type_log="success",
            status=self.status_log,
        )

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
        self.prt.print_msg(
            "Criando planilhas de output",
            row=0,
            type_log="log",
            status=self.status_log,
        )
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
        self.prt.print_msg(
            "Planilhas criadas.",
            row=0,
            type_log="success",
            status=self.status_log,
        )

        for item in planilha_args:
            attribute_name, attribute_val = MakeTemplates.constructor(**item).make()
            setattr(self, attribute_name, attribute_val)

    def open_cfg(self) -> None:
        """Abre as configurações de execução."""
        self.prt.print_msg(
            "Carregando configurações",
            row=0,
            type_log="log",
            status=self.status_log,
        )

        with Path(self.path_config).resolve().open("r") as f:
            data: dict[str, AnyStr] = json.loads(f.read())
            self.config_bot = data
            for k, v in list(data.items()):
                if k == "state" or k == "client":
                    self.state_or_client = v

                setattr(self, k, v)

        self.prt.print_msg(
            "Configurações carregadas",
            row=0,
            type_log="success",
            status=self.status_log,
        )

    def dataFrame(self) -> list[BotData]:  # noqa: N802
        """Convert an Excel file to a list of dictionaries with formatted data.

        Reads an Excel file, processes the data by formatting dates and floats,
        and returns the data as a list of dictionaries.

        Returns:
            List(list[dict[str, str]]): A record list from the processed Excel file.

        Raises:
            FileNotFoundError: If the target file does not exist.
            ValueError: For problems reading the file.

        """
        df = pd.read_excel(self.input_file)
        df.columns = df.columns.str.upper()

        for col in df.columns:
            with suppress(Exception):
                df[col] = df[col].apply(
                    lambda x: (
                        x.strftime("%d/%m/%Y")
                        if isinstance(x, (datetime, Timestamp))
                        else x
                    )
                )

        for col in df.select_dtypes(include=["float"]).columns:
            with suppress(Exception):
                df[col] = df[col].apply(lambda x: f"{x:.2f}".replace(".", ","))

        data_planilha = []

        df_dicted = df.to_dict(orient="records")
        for item in df_dicted:
            for key, value in item.items():
                if str(value) == "nan":
                    item[key] = None

            data_planilha.append(item)

        logs = MessageLog.query_logs(self.pid)

        if logs and logs.row > 0:
            data_planilha = data_planilha[: logs.row + 1]

        return data_planilha

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
        windows = []
        with suppress(Exception):
            windows = self.driver.window_handles

        if len(windows) == 0:
            self.configure_webdriver()
            self.portal_authentication()

        err_message = "\n".join(traceback.format_exception_only(exc))
        message = f"Erro de Operação: {err_message}"
        self.prt.print_msg(
            message=message, type_log="error", pid=self.pid, row=self.row
        )

        self.bot_data.update({"MOTIVO_ERRO": err_message})
        self.append_error(self.bot_data)

    def format_string(self, string: str) -> str:
        """Return a secure, normalized filename based on the input string.

        Args:
            string (str): The original filename.

        Returns:
            str: A secure version of the filename.

        """
        return secure_filename(
            "".join([
                c
                for c in unicodedata.normalize("NFKD", string)
                if not unicodedata.combining(c)
            ]),
        )

    def finalize_execution(self) -> None:
        """Finalize bot execution by closing browsers and logging total time.

        Performs cookie cleanup, quits the driver, and prints summary logs.
        """
        window_handles = self.driver.window_handles
        if window_handles:
            self.driver.delete_all_cookies()
            self.driver.quit()

        end_time = perf_counter()
        execution_time = end_time - self.start_time
        minutes, seconds = divmod(int(execution_time), 60)

        flag_path = Path(self.output_dir_path).joinpath(f"{self.pid}.flag")
        with flag_path.open("w") as f:
            f.write(self.pid)
        self.row = self.total_rows
        type_log = "success"
        message = f"Fim da execução, tempo: {minutes} minutos e {seconds} segundos"
        self.prt.print_msg(
            message=message,
            pid=self.pid,
            row=self.row,
            type_log=type_log,
            status="Finalizado",
        )

    def calc_time(self) -> list[int]:
        """Calculate and return elapsed time as minutes and seconds.

        Returns:
            list[int]: A two-item list: [minutes, seconds] elapsed.

        """
        end_time = perf_counter()
        execution_time = end_time - self.start_time
        minutes = int(execution_time / 60)
        seconds = int(execution_time - minutes * 60)
        return [minutes, seconds]

    def append_moves(self) -> None:
        """Append legal movement records to the spreadsheet if any exist.

        Raises:
            ExecutionError: If no movements are available to append.

        """
        if self.appends:
            for append in self.appends:
                self.append_success(
                    append, "Movimentação salva na planilha com sucesso!!"
                )
        else:
            raise ExecutionError(message="Nenhuma Movimentação encontrada")

    def append_success(
        self,
        data: TypeData,
        message: str = None,
        fileN: str = None,  # noqa: N803
    ) -> None:
        """Append successful execution data to the success spreadsheet.

        Args:
            data (TypeData): The data to be appended.
            message (str, optional): A success message to log.
            fileN (str, optional): Filename override for saving data.

        """
        type_log = "info"
        if message:
            type_log = "success"

        if not message:
            message = "Execução do processo efetuada com sucesso!"

        def save_info(data: list[dict[str, str]]) -> None:
            output_success = self.planilha_sucesso

            if fileN or not output_success:
                output_success = (
                    Path(self.planilha_sucesso).parent.resolve().joinpath(fileN)
                )

            if not output_success.exists():
                df = pd.DataFrame(data)
            else:
                df_existing = pd.read_excel(output_success)
                df = df_existing.to_dict(orient="records")
                df.extend(data)

            new_data = pd.DataFrame(df)
            new_data.to_excel(output_success, index=False)

        typed = type(data) is list and all(isinstance(item, dict) for item in data)

        if not typed:
            data2 = dict.fromkeys(self.name_colunas, "")
            for item in data:
                data2_itens = list(
                    filter(
                        lambda x: x[1] is None or str(x[1]).strip() == "",
                        list(data2.items()),
                    )
                )
                for key, _ in data2_itens:
                    data2.update({key: item})
                    break

            data.clear()
            data.append(data2)

        save_info(data)

        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def append_error(self, data: dict[str, str] = None) -> None:
        """Append error information to the error spreadsheet file.

        Args:
            data (dict[str, str], optional): The error record to log.

        """
        if not path.exists(self.planilha_erro):
            df = pd.DataFrame([data])
        else:
            df_existing = pd.read_excel(self.planilha_erro)
            df = df_existing.to_dict(orient="records")
            df.extend([data])

        new_data = pd.DataFrame(df)
        new_data.to_excel(self.planilha_erro, index=False)

    def append_validarcampos(self, data: list[dict[str, str]]) -> None:
        """Append validated field records to the validation spreadsheet.

        Args:
            data (list[dict[str, str]]): The list of validated data dictionaries.

        """
        nomeplanilha = f"CAMPOS VALIDADOS PID {self.pid}.xlsx"
        planilha_validar = (
            Path(self.planilha_sucesso).parent.resolve().joinpath(nomeplanilha)
        )
        if not path.exists(planilha_validar):
            df = pd.DataFrame(data)
        else:
            df_existing = pd.read_excel(planilha_validar)
            df = df_existing.to_dict(orient="records")
            df.extend(data)

        new_data = pd.DataFrame(df)
        new_data.to_excel(planilha_validar, index=False)

    def count_doc(self, doc: str) -> str | None:
        """Determine whether a document number is CPF or CNPJ based on character length.

        Args:
            doc (str): The document number as string.

        Returns:
            str | None: 'cpf', 'cnpj', or None if invalid.

        """
        numero = "".join(filter(str.isdigit, doc))
        if len(numero) == 11:
            return "cpf"
        if len(numero) == 14:
            return "cnpj"
        return None

    def get_recent(self, folder: str) -> str | None:
        """Return the most recent PDF file path from a folder.

        Args:
            folder (str): The directory to search.

        Returns:
            str | None: Full path to the most recent PDF file, or None.

        """
        files = [
            path.join(folder, f)
            for f in listdir(folder)
            if (path.isfile(path.join(folder, f)) and f.lower().endswith(".pdf"))
            and not f.lower().endswith(".crdownload")  # W261, W503
        ]
        files.sort(key=lambda x: path.getctime(x), reverse=True)
        return files[0] if files else None

    def normalizar_nome(self, word: str) -> str:
        """Normalize a word by removing spaces and special separators.

        Args:
            word (str): The input word.

        Returns:
            str: The normalized, lowercase word.

        """
        return re.sub(r"[\s_\-]", "", word).lower()

    def similaridade(
        self,
        word1: str,
        word2: str,
    ) -> float:
        """Compare two words and return their similarity ratio.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.

        Returns:
            float: A ratio where 1.0 denotes an identical match.

        """
        return SequenceMatcher(None, word1, word2).ratio()

    def install_cert(self) -> None:
        """Install a certificate if it is not already installed.

        Uses certutil to import the certificate and logs the operation.
        """

        def CertIsInstall(crt_sbj_nm: str, store: str = "MY") -> bool:  # noqa: N802
            for cert, _, _ in ssl.enum_certificates(store):
                try:
                    x509_cert = x509.load_der_x509_certificate(
                        cert, default_backend()
                    )
                    subject_name = x509_cert.subject.rfc4514_string()
                    if crt_sbj_nm in subject_name:
                        return True
                except Exception as e:
                    exc = "\n".join(traceback.format_exception_only(e))
                    self.logger.error(exc)

            return False

        installed = CertIsInstall(self.name_cert.split(".pfx")[0])

        if not installed:
            path_cert = Path(self.output_dir_path).joinpath(self.name_cert)
            comando = [
                "certutil",
                "-importpfx",
                "-user",
                "-f",
                "-p",
                self.token,
                "-silent",
                str(path_cert),
            ]
            try:
                resultado = subprocess.run(  # nosec: B603
                    comando,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.message = resultado.stdout
                self.type_log = "log"
                self.prt()
            except subprocess.CalledProcessError as e:
                raise e

    def group_date_all(
        self,
        data: dict[str, dict[str, str]],
    ) -> list[dict[str, str]]:
        """Group legal case records by date and vara and return a list of records.

        Args:
            data (dict[str, dict[str, str]]): Data grouped by vara and date.

        Returns:
            list[dict[str, str]]: Flattened record list including dates and vara.

        """
        records = []
        for vara, dates in data.items():
            for date, entries in dates.items():
                for entry in entries:
                    record = {"Data": date, "Vara": vara}
                    record.update(entry)
                    records.append(record)
        return records

    def group_keys(
        self,
        data: list[dict[str, str]],
    ) -> dict[str, dict[str, str]]:
        """Group keys from a list of dictionaries into a consolidated mapping.

        Args:
            data (list[dict[str, str]]): List of dictionaries with process data.

        Returns:
            dict[str, dict[str, str]]: A dictionary mapping keys to value dictionaries.

        """
        record = {}
        for pos, entry in enumerate(data):
            for key, value in entry.items():
                if key not in record:
                    record[key] = {}
                record[key][str(pos)] = value
        return record

    def gpt_chat(self, text_mov: str) -> str:
        """Obtain an adjusted description via GPT chat based on the legal document text.

        Args:
            text_mov (str): The legal document text for analysis.

        Returns:
            str: An adjusted response derived from GPT chat.

        """
        try:
            sleep(5)
            client = self.OpenAI_client
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.headgpt},
                    {
                        "role": "user",
                        "content": (
                            f"Analise o seguinte texto e ajuste sua resposta de acordo com o tipo de documento: {text_mov}."  # noqa: E501
                        ),
                    },
                ],
                temperature=0.1,
                max_tokens=300,
            )

            choices = completion.choices
            choice = choices[0]
            choice_message = choice.message
            text = choice_message.content

            return text or text_mov

        except Exception as e:
            raise e

    def text_is_a_date(self, text: str) -> bool:
        """Determine if the provided text matches a date-like pattern.

        Args:
            text (str): The text to evaluate.

        Returns:
            bool: True if the text resembles a date; False otherwise.

        """
        date_like_pattern = r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}"
        return bool(re.search(date_like_pattern, text))
