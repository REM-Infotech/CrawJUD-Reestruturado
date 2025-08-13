"""Gerencia operações de download, movimentação e remoção de arquivos temporários.

Este módulo fornece funções para baixar arquivos de um storage, organizar e
remover diretórios temporários utilizados durante o processamento dos dados.
"""

import json
import shutil
from pathlib import Path

import base91
from werkzeug.utils import secure_filename

from crawjud_app.decorators import shared_task
from interface.dict.bot import DictFiles
from utils.storage import Storage

work_dir = Path(__file__).cwd()


@shared_task(name="crawjud.download_files")
def download_files(
    storage_folder_name: str,
) -> list[DictFiles]:
    """Baixe arquivos de um storage, organize e remova diretórios temporários.

    Args:
        storage_folder_name (str): Nome da pasta de configuração para download.

    Returns:
        list[DictFiles]:
            Lista de dicionários contendo informações dos arquivos baixados.


    """
    storage = Storage("minio")
    path_files = work_dir.joinpath("temp")
    list_files: list[DictFiles] = []

    folder_temp_ = storage_folder_name.upper()
    json_name_ = f"{storage_folder_name.upper()}.json"

    object_name_ = str(Path(folder_temp_).joinpath(json_name_))
    config_file = storage.bucket.get_object(object_name_)

    path_files.joinpath(object_name_).parent.mkdir(exist_ok=True, parents=True)

    data_json_: dict[str, str] = json.loads(config_file.data)

    if data_json_.get("xlsx"):
        xlsx_name_ = secure_filename(data_json_.get("xlsx"))

        path_minio_ = str(Path(folder_temp_).joinpath(xlsx_name_))
        file_xlsx = storage.bucket.get_object(path_minio_)
        file_base91str = base91.encode(file_xlsx.data)

        suffix_ = Path(xlsx_name_).suffix

        list_files.append(
            DictFiles(
                file_name=xlsx_name_,
                file_base91str=file_base91str,
                file_suffix=suffix_,
            ),
        )

    if data_json_.get("otherfiles"):
        files_list: list[str] = data_json_.get("otherfiles")
        for file in files_list:
            file = secure_filename(file)
            path_minio_ = str(Path(folder_temp_).joinpath(file))
            file_ = storage.bucket.get_object(path_minio_)
            suffix_ = Path(file).suffix

            file_base91str = base91.encode(file_.data)
            list_files.append(
                DictFiles(
                    file_name=file,
                    file_base91str=file_base91str,
                    file_suffix=suffix_,
                ),
            )

    shutil.rmtree(path_files.joinpath(storage_folder_name))

    return list_files
