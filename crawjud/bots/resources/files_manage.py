"""
Gerencia operações de download, movimentação e remoção de arquivos temporários.

Este módulo fornece funções para baixar arquivos de um storage, organizar e
remover diretórios temporários utilizados durante o processamento dos dados.
"""

import shutil
from pathlib import Path

from addons.storage import Storage
from crawjud import work_dir


async def download_files(pid: str, config_folder_name: str) -> Path:
    """
    Baixe arquivos de um storage, organize e remova diretórios temporários.

    Args:
        pid (str): Identificador do processo para o diretório temporário.
        config_folder_name (str): Nome da pasta de configuração para download.

    Returns:
        Path: Caminho para o arquivo JSON baixado e movido.

    Raises:
        FileNotFoundError: Caso o diretório de arquivos não seja encontrado.

    """
    storage = Storage("minio")
    path_files = work_dir.joinpath("temp", pid)

    await storage.download_files(
        dest=path_files,
        prefix=config_folder_name,
    )

    for root, _, files in path_files.joinpath(config_folder_name).walk():
        for file in files:
            shutil.move(root.joinpath(file), path_files.joinpath(file))

    shutil.rmtree(path_files.joinpath(config_folder_name))

    return path_files.joinpath(f"{config_folder_name}.json")


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
