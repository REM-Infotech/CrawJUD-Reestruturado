"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

import json
from abc import ABC
from logging import Logger
from pathlib import Path
from time import perf_counter
from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
    Callable,
    ParamSpec,
    Self,
    TypeVar,
)

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from celery_app.custom._canvas import subtask as subtask
from crawjud.addons.make_templates import MakeTemplates as MakeTemplates
from crawjud.addons.search import SearchController
from crawjud.common.exceptions.bot import ExecutionError as ExecutionError
from crawjud.common.exceptions.bot import StartError
from crawjud.types import StrPath
from crawjud.types import TypeData as TypeData
from crawjud.types.elements import type_elements
from utils.logger import dict_config as dict_config
from utils.printlogs import PrintMessage

if TYPE_CHECKING:
    from crawjud.types import BotData
T = TypeVar("AnyValue", bound=str)
PrintParamSpec = ParamSpec("PrintParamSpec", bound=str)
PrintTReturn = TypeVar("PrintTReturn", bound=Any)


class CrawJUD(ABC):
    """Classe de controle de variáveis CrawJUD."""

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
    _total_rows: int = 0
    _print_msg: Callable[PrintParamSpec, PrintTReturn] = None

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
    def total_rows(self) -> int:  # noqa: D102
        return self._total_rows

    @total_rows.setter
    def total_rows(self, new_value: int) -> None:
        self._total_rows = new_value

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
    def prt(self) -> Callable[PrintParamSpec, PrintTReturn]:  # noqa: D102
        return self._print_msg

    async def initialize(
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

    def print_msg(
        self,
        pid: str,
        message: str,
        row: int,
        type_log: str,
        total_rows: int,
        start_time: str,
    ) -> None:
        """
        Envia mensagem de log para o sistema de tarefas assíncronas.

        Args:
            pid (str): Identificador do processo.
            message (str): Mensagem a ser registrada.
            row (int): Linha atual do processamento.
            type_log (str): Tipo de log (info, error, etc).
            total_rows (int): Total de linhas a serem processadas.
            start_time (str): Horário de início do processamento.

        Returns:
            None: Não retorna valor.

        """
        _task_message = subtask("log_message")
        _task_message.apply_async(
            kwargs={
                "pid": pid,
                "message": message,
                "row": row,
                "type_log": type_log,
                "total_rows": total_rows,
                "start_time": start_time,
            }
        )
