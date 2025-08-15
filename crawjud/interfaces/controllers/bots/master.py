"""Modulo de controle da classe Base para todos os bots."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from threading import Semaphore
from typing import TYPE_CHECKING, ClassVar
from zoneinfo import ZoneInfo

import base91
from pandas import Timestamp, read_excel
from tqdm import tqdm

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.custom.canvas import subtask
from crawjud.custom.task import ContextTask
from crawjud.interfaces.dict.bot import BotData
from crawjud.utils.models.logs import MessageLogDict
from crawjud.utils.storage import Storage

if TYPE_CHECKING:
    from typing import ClassVar

    from socketio import SimpleClient

    from crawjud.interfaces.dict.bot import DictFiles

func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}


class AbstractCrawJUD:
    """Classe base para todos os bots."""

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """Verifica se a subclasse implementa todos os métodos obrigatórios."""
        tqdm.write("ok")

    def __init_subclass__(cls) -> None:
        """Empty."""
        cls.tasks_cls[cls.__name__] = cls


class CrawJUD[T](AbstractCrawJUD, ContextTask):
    """Classe CrawJUD."""

    current_task: ContextTask
    sio: SimpleClient
    _stop_bot: bool = False
    _folder_storage: ClassVar[str] = ""
    _xlsx_data: ClassVar[DictFiles] = {}
    _downloaded_files: ClassVar[list[DictFiles]] = []
    _bot_data: ClassVar[list[BotData]] = {}
    posicoes_processos: ClassVar[dict[str, int]] = {}

    tasks_cls: ClassVar[dict] = {}
    # Atributos Globais
    _pid: str | None = None
    _total_rows: int = 0
    _start_time: str | None = None
    _regiao: str | None = None
    _data_regiao: list[BotData] | None = None
    _cookies: dict[str, str] | None = None
    _headers: dict[str, str] | None = None
    _base_url: str | None = None

    semaforo_save = Semaphore(1)
    _storage = Storage("minio")

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

    @property
    def pid(self) -> str:
        return self._pid

    @pid.setter
    def pid(self, new_pid: str) -> None:
        self._pid = new_pid

    @property
    def start_time(self) -> str:
        return self._start_time

    @start_time.setter
    def start_time(self, _start_time: str) -> None:
        self._start_time = _start_time

    @property
    def total_rows(self) -> int:
        return self._total_rows

    @total_rows.setter
    def total_rows(self, _total_rows: int) -> None:
        self._total_rows = _total_rows

    @property
    def downloaded_files(self) -> list[DictFiles]:
        return self._downloaded_files

    @property
    def xlsx_data(self) -> DictFiles:
        return self._xlsx_data

    @property
    def folder_storage(self) -> str:
        return self._folder_storage

    @folder_storage.setter
    def folder_storage(self, _folder_storage: str) -> None:
        self._folder_storage = _folder_storage

    def load_data(
        self,
        base91_planilha: str,
    ) -> list[BotData]:
        """Convert an Excel file to a list of dictionaries with formatted data.

        Reads an Excel file, processes the data by formatting dates and floats,
        and returns the data as a list of dictionaries.

        Arguments:
            base91_planilha (str):
                base91 da planilha

        Returns:
            list[BotData]: A record list from the processed Excel file.

        """
        buffer_planilha = BytesIO(base91.decode(base91_planilha))
        df = read_excel(buffer_planilha)
        df.columns = df.columns.str.upper()

        def format_data(x: T) -> str:
            if str(x) == "NaT" or str(x) == "nan":
                return ""

            if isinstance(x, (datetime, Timestamp)):
                return x.strftime("%d/%m/%Y")

            return x

        def format_float(x: T) -> str:
            return f"{x:.2f}".replace(".", ",")

        for col in df.columns:
            df[col] = df[col].apply(format_data)

        for col in df.select_dtypes(include=["float"]).columns:
            df[col] = df[col].apply(format_float)

        return [BotData(list(item.items())) for item in df.to_dict(orient="records")]

    @property
    def bot_data(self) -> list[BotData]:
        return self._bot_data

    @property
    def storage(self) -> Storage:
        """Storage do CrawJUD."""
        return self._storage

    def download_files(
        self,
    ) -> None:
        # TODO(Nicholas Silva): Criar Exception para erros de download de arquivos
        # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
        """Baixa os arquivos necessários para a execução do robô.

        Raises:
            ExecutionError:
                Exception genérico de execução

        """
        files_b64: list[DictFiles] = (
            subtask("crawjud.download_files")
            .apply_async(kwargs={"storage_folder_name": self.folder_storage})
            .wait_ready()
        )
        xlsx_key = list(filter(lambda x: x["file_suffix"] == ".xlsx", files_b64))
        if not xlsx_key:
            raise ExecutionError(message="Nenhum arquivo Excel encontrado.")

        self._xlsx_data = xlsx_key[-1]
        self._downloaded_files = files_b64

    def data_frame(self) -> None:
        bot_data: list[BotData] = self.load_data(
            base91_planilha=self.xlsx_data["file_base91str"],
        )

        self._bot_data = bot_data

    def carregar_arquivos(self) -> None:
        self.download_files()
        self.data_frame()

        self.print_msg(
            message="Planilha carregada!",
            type_log="info",
        )
