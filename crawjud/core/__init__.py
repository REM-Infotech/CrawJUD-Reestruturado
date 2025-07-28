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
from datetime import datetime
from difflib import SequenceMatcher
from os import listdir, path
from pathlib import Path
from time import perf_counter, sleep
from typing import Any, AnyStr, Generic, Self, TypeVar

import pandas as pd
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from pandas import Timestamp
from pytz import timezone
from werkzeug.utils import secure_filename

from addons.logger import dict_config
from crawjud.addons.make_templates import MakeTemplates
from crawjud.core._dictionary import BotData
from crawjud.core._properties import PropertiesCrawJUD
from crawjud.exceptions.bot import ExecutionError, StartError
from crawjud.types import TypeData

T = TypeVar("AnyValue", bound=str)


class CrawJUD(PropertiesCrawJUD):
    """Classe de controle de variáveis CrawJUD."""

    def initialize(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Self:
        """Initialize a new Pauta instance with provided arguments now.

        Args:
            *args (str|int): Positional arguments.
            **kwargs (str|int): Keyword arguments.

        """
        try:
            self.print_msg = kwargs.get("task_bot").print_msg
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

            pid = kwargs.get("pid")
            self.print_msg("Configurando o núcleo...", pid, 0, "log", "Inicializando")

            self.open_cfg()

            # Configuração do logger
            self.configure_logger()

            # Define o InputFile
            self.input_file = Path(self.output_dir_path).resolve().joinpath(self.xlsx)

            # Criação de planilhas template
            self.make_templates()

            self.print_msg(
                "Núcleo configurado.", self.pid, 0, "success", "Inicializando"
            )

            return self

        except Exception as e:
            raise StartError(exception=e) from e

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
        self.print_msg(
            "Criando planilhas de output",
            row=0,
            type_log="log",
            status="Inicializando",
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
        self.print_msg(
            "Planilhas criadas.",
            row=0,
            type_log="success",
            status="Inicializando",
        )

        for item in planilha_args:
            attribute_name, attribute_val = MakeTemplates.constructor(**item).make()
            setattr(self, attribute_name, attribute_val)

    def open_cfg(self) -> None:
        """Abre as configurações de execução."""
        self.print_msg(
            "Carregando configurações",
            row=0,
            type_log="log",
            status="Inicializando",
        )

        with Path(self.path_config).resolve().open("r") as f:
            data: dict[str, AnyStr] = json.loads(f.read())
            self.config_bot = data
            for k, v in list(data.items()):
                if k == "state" or k == "client":
                    self.state_or_client = v

                setattr(self, k, v)

        self.print_msg(
            "Configurações carregadas",
            row=0,
            type_log="success",
            status="Inicializando",
        )

    def dataFrame(self) -> list[BotData]:  # noqa: N802
        """Convert an Excel file to a list of dictionaries with formatted data.

        Reads an Excel file, processes the data by formatting dates and floats,
        and returns the data as a list of dictionaries.

        Returns:
            list[BotData]: A record list from the processed Excel file.

        Raises:
            FileNotFoundError: If the target file does not exist.
            ValueError: For problems reading the file.

        """
        input_file = Path(self.output_dir_path).joinpath(self.xlsx).resolve()

        df = pd.read_excel(input_file)
        df.columns = df.columns.str.upper()

        def format_data(x: Generic[T]) -> str:
            if str(x) == "NaT" or str(x) == "nan":
                return ""

            if isinstance(x, (datetime, Timestamp)):
                return x.strftime("%d/%m/%Y")

            return x

        def format_float(x: Generic[T]) -> str:
            return f"{x:.2f}".replace(".", ",")

        for col in df.columns:
            df[col] = df[col].apply(format_data)

        for col in df.select_dtypes(include=["float"]).columns:
            df[col] = df[col].apply(format_float)

        to_list = [dict(list(item.items())) for item in df.to_dict(orient="records")]

        return to_list

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
        err_message = "\n".join(traceback.format_exception_only(exc))
        message = f"Erro de Operação: {err_message}"
        self.print_msg(message=message, type_log="error", pid=self.pid, row=self.row)

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
        self.print_msg(
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

        self.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

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
