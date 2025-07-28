from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING, Any, AnyStr, Callable, ParamSpec, TypeVar

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from addons.printlogs import PrintMessage
from crawjud.addons.search import SearchController
from crawjud.core._dictionary import BotData
from crawjud.types import StrPath
from crawjud.types.elements import type_elements

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData

PrintParamSpec = ParamSpec("PrintParamSpec", bound=str)
PrintTReturn = TypeVar("PrintTReturn", bound=Any)


class PropertiesCrawJUD:
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
    _print_msg: Callable[PrintParamSpec, PrintTReturn]

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

    @property
    def print_msg(self) -> Callable[PrintParamSpec, PrintTReturn]:
        return self._print_msg

    @print_msg.setter
    def print_msg(self, new_value: Callable[PrintParamSpec, PrintTReturn]) -> None:
        self._print_msg = new_value

    @property
    def prt(self) -> Callable[PrintParamSpec, PrintTReturn]:
        return self._print_msg
