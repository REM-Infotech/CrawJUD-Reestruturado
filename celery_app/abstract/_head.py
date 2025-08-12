from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from celery_app.abstract._properties import PropertyBot
from celery_app.common.exceptions.bot import ExecutionError
from celery_app.custom._canvas import subtask
from celery_app.types.bot import BotData, DictFiles

if TYPE_CHECKING:
    from utils.storage import Storage


class HeadBot[T](PropertyBot):
    def download_files(self) -> None:
        files_b64: list[DictFiles] = (
            subtask("crawjud.download_files")
            .apply_async(kwargs={"storage_folder_name": self.folder_storage})
            .wait_ready()
        )
        xlsx_key = list(filter(lambda x: x["file_suffix"] == ".xlsx", files_b64))
        if not xlsx_key:
            raise ExecutionError("Nenhum arquivo Excel encontrado.")

        self._xlsx_data = xlsx_key[-1]
        self._downloaded_files = files_b64

    def data_frame(self) -> None:
        bot_data: list[BotData] = self.crawjud_dataframe.apply_async(
            kwargs={"base91_planilha": self.xlsx_data["file_base91str"]}
        ).wait_ready()

        self._bot_data = bot_data

    def carregar_arquivos(self) -> None:
        self.download_files()
        self.data_frame()

        self.print_msg(
            message="Planilha carregada!",
            type_log="info",
        )

    @abstractmethod
    def autenticar(self, *args: T, **kwargs: T) -> bool: ...

    @abstractmethod
    def buscar_processo(self, *args: T, **kwargs: T) -> bool: ...

    @property
    @abstractmethod
    def storage(self) -> Storage: ...
