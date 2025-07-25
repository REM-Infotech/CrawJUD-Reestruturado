# noqa: D100

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from dotenv import load_dotenv

from crawjud.addons.search import SearchController
from crawjud.core._dictionary import BotData
from crawjud.core.master import Controller as Controller
from crawjud.types import TypeData

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData

load_dotenv(Path(__file__).parent.resolve().joinpath("../.env"))


class ClassBot(ABC):  # noqa: D101
    @classmethod
    @abstractmethod
    async def initialize(cls, *args: Any, **kwargs: Any) -> Self: ...  # noqa: D102

    @abstractmethod
    async def execution(self) -> None: ...  # noqa: D102

    @property
    @abstractmethod
    def max_rows(self) -> int: ...  # noqa: D102

    @max_rows.setter
    @abstractmethod
    def max_rows(self, new_value: int) -> None: ...

    @property
    @abstractmethod
    def total_rows(self) -> int: ...  # noqa: D102

    @total_rows.setter
    @abstractmethod
    def total_rows(self, new_value: int) -> None: ...

    @property
    @abstractmethod
    def is_stoped(self) -> bool: ...  # noqa: D102

    @is_stoped.setter
    @abstractmethod
    def is_stoped(self, new_value: bool) -> None: ...

    @property
    @abstractmethod
    def bot_data(self) -> BotData:
        """Property bot data."""

    @bot_data.setter
    @abstractmethod
    def bot_data(self, new_data: BotData) -> None:
        """Property bot data."""

    @property
    @abstractmethod
    def search_bot(self) -> SearchController:
        """Property para o searchbot."""

    @search_bot.setter
    @abstractmethod
    def search_bot(self, instancia: SearchController) -> None:
        """Define a instância do searchbot."""

    @property
    @abstractmethod
    def row(self) -> int: ...  # noqa: D102

    @row.setter
    @abstractmethod
    def row(self, new_value: int) -> None:
        """Define o valor da variável row."""

    @property
    @abstractmethod
    def cities_amazonas(self) -> dict[str, str]:  # noqa: N802
        """Return a dictionary categorizing Amazonas cities as 'Capital' or 'Interior'.

        Returns:
            dict[str, str]: City names with associated regional classification.

        """

    @abstractmethod
    def configure_searchengine(self) -> None:
        """Configura a instância do search engine."""

    @abstractmethod
    def portal_authentication(self) -> None:
        """Autenticação com os sistemas."""

    @abstractmethod
    def configure_webdriver(self) -> None:
        """Instancia o WebDriver."""

    @abstractmethod
    def configure_logger(self) -> None:
        """Configura o logger."""

    @abstractmethod
    def make_templates(self) -> None:
        """Criação de planilhas de output do robô."""

    @abstractmethod
    def open_cfg(self) -> None:
        """Abre as configurações de execução."""

    @abstractmethod
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

    @abstractmethod
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

        """

    @abstractmethod
    def tratamento_erros(self, exc: Exception, last_message: str = None) -> None:
        """Tratamento de erros dos robôs."""

    @abstractmethod
    def format_string(self, string: str) -> str:
        """Return a secure, normalized filename based on the input string.

        Args:
            string (str): The original filename.

        Returns:
            str: A secure version of the filename.

        """

    @abstractmethod
    def finalize_execution(self) -> None:
        """Finalize bot execution by closing browsers and logging total time.

        Performs cookie cleanup, quits the driver, and prints summary logs.
        """

    @abstractmethod
    def calc_time(self) -> list[int]:
        """Calculate and return elapsed time as minutes and seconds.

        Returns:
            list[int]: A two-item list: [minutes, seconds] elapsed.

        """

    @abstractmethod
    def append_moves(self) -> None:
        """Append legal movement records to the spreadsheet if any exist.

        Raises:
            ExecutionError: If no movements are available to append.

        """

    @abstractmethod
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

    @abstractmethod
    def append_error(self, data: dict[str, str] = None) -> None:
        """Append error information to the error spreadsheet file.

        Args:
            data (dict[str, str], optional): The error record to log.

        """

    @abstractmethod
    def append_validarcampos(self, data: list[dict[str, str]]) -> None:
        """Append validated field records to the validation spreadsheet.

        Args:
            data (list[dict[str, str]]): The list of validated data dictionaries.

        """

    @abstractmethod
    def count_doc(self, doc: str) -> str | None:
        """Determine whether a document number is CPF or CNPJ based on character length.

        Args:
            doc (str): The document number as string.

        Returns:
            str | None: 'cpf', 'cnpj', or None if invalid.

        """

    @abstractmethod
    def get_recent(self, folder: str) -> str | None:
        """Return the most recent PDF file path from a folder.

        Args:
            folder (str): The directory to search.

        Returns:
            str | None: Full path to the most recent PDF file, or None.

        """

    @abstractmethod
    def normalizar_nome(self, word: str) -> str:
        """Normalize a word by removing spaces and special separators.

        Args:
            word (str): The input word.

        Returns:
            str: The normalized, lowercase word.

        """

    @abstractmethod
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

    @abstractmethod
    def install_cert(self) -> None:
        """Install a certificate if it is not already installed.

        Uses certutil to import the certificate and logs the operation.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def gpt_chat(self, text_mov: str) -> str:
        """Obtain an adjusted description via GPT chat based on the legal document text.

        Args:
            text_mov (str): The legal document text for analysis.

        Returns:
            str: An adjusted response derived from GPT chat.

        """

    @abstractmethod
    def text_is_a_date(self, text: str) -> bool:
        """Determine if the provided text matches a date-like pattern.

        Args:
            text (str): The text to evaluate.

        Returns:
            bool: True if the text resembles a date; False otherwise.

        """
