"""Serviço de domínio para manipulação de arquivos e sessões."""

import io
import shutil
import traceback
from os import path
from pathlib import Path
from typing import Any, AnyStr

import aiofiles
from clear import clear
from quart import request, session
from tqdm import tqdm
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from utils.storage import Storage

workdir_path = Path(__file__).cwd()


class FileService:
    """Serviço de domínio para manipulação de arquivos e sessões de usuário."""

    async def save_file(self) -> None:
        """Salva um arquivo enviado para o diretório temporário especificado."""
        storage = Storage("minio")

        try:
            data = await request.form
            _file = await request.files
            sid = str(session.sid)

            file_name = str(data.get("name"))
            index = int(data.get("index", 0))

            _total = int(data.get("total", 1)) * 1024
            chunk = data.get("chunk", _file.get("chunk", b""))
            chunksize = int(data.get("chunksize", 1024))
            file_size = int(data.get("file_size"))
            if isinstance(chunk, FileStorage):
                chunk = chunk.stream.read()

            _start = index * chunksize
            _end = min(file_size, _start + chunksize)

            content_type = str(data.get("content_type"))

            if not all([file_name, chunk, content_type]):
                tqdm.write(f"chunk: {chunk}")
                if chunk == b"":
                    return

                raise ValueError("Dados do chunk incompletos.")

            # Define diretório temporário para armazenar os chunks
            path_temp = Path(__file__).cwd().joinpath("temp", sid.upper())
            path_temp.mkdir(parents=True, exist_ok=True)
            file_path = path_temp.joinpath(file_name)

            # Salva o chunk no arquivo temporário
            mode = "ab" if index > 0 else "wb"

            async with aiofiles.open(file_path, mode) as f:
                await f.write(chunk)

            if _end >= file_size:
                async with aiofiles.open(file_path, "rb") as f:
                    _data = io.BytesIO(await f.read())
                    dest_path = path.join(sid.upper(), secure_filename(file_name))
                    storage.put_object(
                        object_name=dest_path,
                        data=_data,
                        length=_end,
                        content_type=content_type,
                    )

                shutil.rmtree(file_path.parent)

        except Exception as e:
            clear()
            tqdm.write("\n".join(traceback.format_exception(e)))

    async def save_session(
        self,
        server: Any,
        sid: str,
        session: dict[str, AnyStr],
        namespace: str | None = None,
    ) -> None:
        """Armazena a sessão do usuário para um cliente na sessão do engineio."""
        namespace = namespace or "/"
        eio_sid = server.manager.eio_sid_from_sid(sid, namespace)
        eio_session = await server.eio.get_session(eio_sid)
        eio_session[namespace] = session
