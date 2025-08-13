from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from tqdm import tqdm

from utils.models.logs import MessageLogDict
from utils.webdriver import DriverBot

func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}

if TYPE_CHECKING:
    from typing import ClassVar

    from crawjud_app.addons.auth.controller import AuthController
    from crawjud_app.addons.search.controller import SearchController
    from interface.dict.bot import BotData


class AbstractClassBot[T](ABC):
    # Adiciona importação para ClassVar

    tasks_cls: ClassVar[dict] = {}
    subclasses_auth: ClassVar[dict[str, type[AuthController]]] = {}
    subclasses_search: ClassVar[dict[str, type[SearchController]]] = {}
    # Atributos Globais
    _pid: str | None = None
    _total_rows: int = 0
    _start_time: str | None = None
    _regiao: str | None = None
    _data_regiao: list[BotData] | None = None
    _cookies: dict[str, str] | None = None
    _headers: dict[str, str] | None = None
    _base_url: str | None = None

    _driver: ClassVar[DriverBot] = None

    @property
    def driver(self) -> DriverBot:
        if not self._driver:
            self._driver = DriverBot(
                selected_browser="chrome",
                with_proxy=True,
            )

        return self._driver

    @property
    def data_regiao(self) -> list[BotData]:
        return self._data_regiao

    @data_regiao.setter
    def data_regiao(self, _data_regiao: str) -> None:
        self._data_regiao = _data_regiao

    @property
    def regiao(self) -> str:
        return self._regiao

    @regiao.setter
    def regiao(self, _regiao: str) -> None:
        self._regiao = _regiao

    def print_msg(  # noqa: D417
        self,
        message: str,
        row: int = 0,
        errors: int = 0,
        type_log: str = "log",
    ) -> None:
        """Envia mensagem de log para o sistema de tarefas assíncronas.

        Args:
            pid (str): Identificador do processo.
            message (str): Mensagem a ser registrada.
            row (int): Linha atual do processamento.
            type_log (str): Tipo de log (info, error, etc).
            total_rows (int): Total de linhas a serem processadas.
            start_time (str): Horário de início do processamento.
            status (str): Status atual do processamento (default: "Em Execução").



        """
        # Obtém o horário atual formatado
        time_exec = datetime.now(tz=ZoneInfo("America/Manaus")).strftime("%H:%M:%S")
        # Monta o prompt da mensagem
        prompt = (
            f"[({self._pid[:6].upper()}, {type_log}, {row}, {time_exec})> {message}]"
        )

        # Cria objeto de log da mensagem
        data = {
            "data": MessageLogDict(
                message=str(prompt),
                pid=str(self._pid),
                row=int(row),
                type=type_log,
                status="Em Execução",
                total=int(self._total_rows),
                success=0,
                errors=errors,
                remaining=int(self._total_rows),
                start_time=self._start_time,
            ),
        }

        self.sio.emit(
            event="log_execution",
            data=data,
        )
        # Envia a mensagem formatada para o sistema de monitoramento

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """Verifica se a subclasse implementa todos os métodos obrigatórios."""
        tqdm.write("ok")

    def __init_subclass__(cls) -> None:
        cls.tasks_cls[cls.__name__] = cls

    @abstractmethod
    def save_success_cache(self, data: dict) -> None:
        """Save the successful cache data.

        Args:
            data (dict): The data to be saved in the cache.

        """
