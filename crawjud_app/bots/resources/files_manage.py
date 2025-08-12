"""
Gerencia operações de download, movimentação e remoção de arquivos temporários.

Este módulo fornece funções para baixar arquivos de um storage, organizar e
remover diretórios temporários utilizados durante o processamento dos dados.
"""

import json
import shutil
from os import path
from pathlib import Path
from typing import Generic, TypeVar

import base91
from crawjud import work_dir
from werkzeug.utils import secure_filename

from crawjud_app.decorators import shared_task
from crawjud_app.types import ReturnFormataTempo
from crawjud_app.types.bot import DictFiles
from utils.storage import Storage

T = TypeVar("AnyValue", bound=ReturnFormataTempo)


@shared_task(name="crawjud.download_files")
def download_files(  # noqa: D417
    storage_folder_name: str, *args: Generic[T], **kwargs: Generic[T]
) -> list[DictFiles]:
    """
    Baixe arquivos de um storage, organize e remova diretórios temporários.

    Args:
        storage_folder_name (str): Nome da pasta de configuração para download.

    Returns:
        list[DictFiles]: Lista de dicionários contendo informações dos arquivos baixados.

    Raises:
        FileNotFoundError: Caso o diretório de arquivos não seja encontrado.

    """
    storage = Storage("minio")
    path_files = work_dir.joinpath("temp")
    list_files: list[DictFiles] = []

    _folder_temp = storage_folder_name.upper()
    _json_name = f"{storage_folder_name.upper()}.json"
    _object_name = path.join(_folder_temp, _json_name)
    config_file = storage.bucket.get_object(_object_name)

    path_files.joinpath(_object_name).parent.mkdir(exist_ok=True, parents=True)

    _data_json: dict[str, str] = json.loads(config_file.data)

    if _data_json.get("xlsx"):
        _xlsx_name = secure_filename(_data_json.get("xlsx"))
        _path_minio = path.join(_folder_temp, _xlsx_name)
        file_xlsx = storage.bucket.get_object(_path_minio)
        file_base91str = base91.encode(file_xlsx.data)

        _suffix = Path(_xlsx_name).suffix

        list_files.append(
            DictFiles(
                file_name=_xlsx_name,
                file_base91str=file_base91str,
                file_suffix=_suffix,
            )
        )

    if _data_json.get("otherfiles"):
        files_list: list[str] = _data_json.get("otherfiles")
        for file in files_list:
            file = secure_filename(file)
            _path_minio = path.join(_folder_temp, file)
            _file = storage.bucket.get_object(_path_minio)
            _suffix = Path(file).suffix

            file_base91str = base91.encode(_file.data)
            list_files.append(
                DictFiles(
                    file_name=file,
                    file_base91str=file_base91str,
                    file_suffix=_suffix,
                )
            )

    shutil.rmtree(path_files.joinpath(storage_folder_name))

    return list_files


async def remove_temp_files(pid: str) -> None:
    """
    Remove diretórios temporários utilizados durante o processamento dos dados.

    Args:
        pid (str): Identificador do processo cujos arquivos temporários serão removidos.

    Returns:
        None: Esta função não retorna valor.

    """
    path_files = work_dir.joinpath("temp", pid)
    if path_files.exists():
        shutil.rmtree(path_files)
