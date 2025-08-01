"""
Gerencia operações de download, movimentação e remoção de arquivos temporários.

Este módulo fornece funções para baixar arquivos de um storage, organizar e
remover diretórios temporários utilizados durante o processamento dos dados.
"""

import asyncio
import base64
import shutil
from pathlib import Path
from typing import TypedDict

from addons.storage import Storage
from celery_app._wrapper import shared_task
from crawjud import work_dir


class DictFiles(TypedDict):
    """Dicionário para armazenar informações de arquivos baixados."""

    file_name: str
    file_base64str: str
    file_suffix: str = ".json"


@shared_task(name="crawjud.download_files")
def download_files(storage_folder_name: str) -> list[DictFiles]:
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

    asyncio.run(
        storage.download_files(
            dest=path_files,
            prefix=storage_folder_name,
        )
    )

    list_files: list[DictFiles] = []
    for root, _, files in path_files.joinpath(storage_folder_name).walk():
        for file in files:
            with root.joinpath(file).open("rb") as f:
                file_base64str = base64.b64encode(f.read()).decode()
            list_files.append(
                DictFiles(
                    file_name=file,
                    file_base64str=file_base64str,
                    file_suffix=Path(file).suffix,
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
