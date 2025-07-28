# noqa: D100

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from dotenv import load_dotenv

from crawjud.addons.search import SearchController  # noqa: F401
from crawjud.core._dictionary import BotData

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData  # noqa: F401

load_dotenv(Path(__file__).parent.resolve().joinpath("../.env"))

TReturn = TypeVar("TReturn")


class ClassBot(ABC):  # noqa:  D101
    async def print_msg(  # noqa: B027, D102
        self,
        message: str = "Carregando",
        pid: str = None,
        row: int = 0,
        type_log: str = "log",
        status: str = "Inicializando",
        *args: Any,
        **kwargs: Any,
    ) -> None: ...  # noqa: D102, E303, N802, B027

    @abstractmethod
    async def execution(self) -> None: ...  # noqa: D102

    @abstractmethod
    async def queue(self) -> None: ...  # noqa: D102

    # @property  # noqa: B027
    # def max_rows(self) -> int: ...  # noqa: D102

    # @max_rows.setter  # noqa: B027
    # def max_rows(self, new_value: int) -> None: ...

    # @property  # noqa: B027
    # def total_rows(self) -> int: ...  # noqa: D102

    # @total_rows.setter  # noqa: B027
    # def total_rows(self, new_value: int) -> None: ...

    # @property  # noqa: B027
    # def is_stoped(self) -> bool: ...  # noqa: D102

    # @is_stoped.setter  # noqa: B027
    # def is_stoped(self, new_value: bool) -> None: ...

    # @property  # noqa: B027
    # def bot_data(self) -> BotData:
    #     """Property bot data."""

    # @bot_data.setter  # noqa: N802, B027
    # def bot_data(self, new_data: BotData) -> None:
    #     """Property bot data."""

    # @property  # noqa: N802, B027
    # def search_bot(self) -> SearchController:
    #     """Property para o searchbot."""

    # @search_bot.setter  # noqa: B027
    # def search_bot(self, instancia: SearchController) -> None:
    #     """Define a instância do searchbot."""

    # @property  # noqa: B027
    # def row(self) -> int: ...  # noqa: D102

    # @row.setter  # noqa: B027
    # def row(self, new_value: int) -> None:
    #     """Define o valor da variável row."""

    # @property  # noqa: B027
    # def cities_amazonas(self) -> dict[str, str]:  # noqa: N802
    #     """Return a dictionary categorizing Amazonas cities as 'Capital' or 'Interior'.

    #     Returns:
    #         dict[str, str]: City names with associated regional classification.

    #     """

    # def open_cfg(self) -> None:  # noqa: B027
    #     """Abre as configurações de execução."""

    # def dataFrame(self) -> list[BotData]:  # noqa: N802, B027
    #     """Convert an Excel file to a list of dictionaries with formatted data.

    #     Reads an Excel file, processes the data by formatting dates and floats,
    #     and returns the data as a list of dictionaries.

    #     Returns:
    #         List(list[dict[str, str]]): A record list from the processed Excel file.

    #     Raises:
    #         FileNotFoundError: If the target file does not exist.
    #         ValueError: For problems reading the file.

    #     """

    # def elawFormats(self, data: dict[str, str]) -> dict[str, str]:  # noqa: N802, B027
    #     """Format a legal case dictionary according to pre-defined rules.

    #     Args:
    #         data (dict[str, str]): The raw data dictionary.

    #     Returns:
    #         dict[str, str]: The data formatted with proper types and values.

    #     Rules:
    #         - If the key is "TIPO_EMPRESA" and its value is "RÉU", update "TIPO_PARTE_CONTRARIA" to "Autor".
    #         - If the key is "COMARCA", update "CAPITAL_INTERIOR" based on the value using the cities_Amazonas method.
    #         - If the key is "DATA_LIMITE" and "DATA_INICIO" is not present, set "DATA_INICIO" to the value of "DATA_LIMITE".
    #         - If the value is an integer or float, format it to two decimal places and replace the decimal point with a clcomma.
    #         - If the key is "CNPJ_FAVORECIDO" and its value is empty, set it to "04.812.509/0001-90".

    #     """

    # def format_string(self, string: str) -> str:  # noqa: N802, B027
    #     """Return a secure, normalized filename based on the input string.

    #     Args:
    #         string (str): The original filename.

    #     Returns:
    #         str: A secure version of the filename.

    #     """

    # def calc_time(self) -> list[int]:  # noqa: N802, B027
    #     """Calculate and return elapsed time as minutes and seconds.

    #     Returns:
    #         list[int]: A two-item list: [minutes, seconds] elapsed.

    #     """

    # def count_doc(self, doc: str) -> str | None:  # noqa: N802, B027
    #     """Determine whether a document number is CPF or CNPJ based on character length.

    #     Args:
    #         doc (str): The document number as string.

    #     Returns:
    #         str | None: 'cpf', 'cnpj', or None if invalid.

    #     """

    # def get_recent(self, folder: str) -> str | None:  # noqa: N802, B027
    #     """Return the most recent PDF file path from a folder.

    #     Args:
    #         folder (str): The directory to search.

    #     Returns:
    #         str | None: Full path to the most recent PDF file, or None.

    #     """

    # def normalizar_nome(self, word: str) -> str:  # noqa: N802, B027
    #     """Normalize a word by removing spaces and special separators.

    #     Args:
    #         word (str): The input word.

    #     Returns:
    #         str: The normalized, lowercase word.

    #     """

    # def similaridade(  # noqa: N802, B027
    #     self,
    #     word1: str,
    #     word2: str,
    # ) -> float:
    #     """Compare two words and return their similarity ratio.

    #     Args:
    #         word1 (str): The first word.
    #         word2 (str): The second word.

    #     Returns:
    #         float: A ratio where 1.0 denotes an identical match.

    #     """

    # def group_date_all(  # noqa: N802, B027
    #     self,
    #     data: dict[str, dict[str, str]],
    # ) -> list[dict[str, str]]:
    #     """Group legal case records by date and vara and return a list of records.

    #     Args:
    #         data (dict[str, dict[str, str]]): Data grouped by vara and date.

    #     Returns:
    #         list[dict[str, str]]: Flattened record list including dates and vara.

    #     """

    # def group_keys(  # noqa: N802, B027
    #     self,
    #     data: list[dict[str, str]],
    # ) -> dict[str, dict[str, str]]:
    #     """Group keys from a list of dictionaries into a consolidated mapping.

    #     Args:
    #         data (list[dict[str, str]]): List of dictionaries with process data.

    #     Returns:
    #         dict[str, dict[str, str]]: A dictionary mapping keys to value dictionaries.

    #     """

    # def gpt_chat(self, text_mov: str) -> str:  # noqa: N802, B027
    #     """Obtain an adjusted description via GPT chat based on the legal document text.

    #     Args:
    #         text_mov (str): The legal document text for analysis.

    #     Returns:
    #         str: An adjusted response derived from GPT chat.

    #     """

    # def text_is_a_date(self, text: str) -> bool:  # noqa: N802, B027
    #     """Determine if the provided text matches a date-like pattern.

    #     Args:
    #         text (str): The text to evaluate.

    #     Returns:
    #         bool: True if the text resembles a date; False otherwise.

    #     """
