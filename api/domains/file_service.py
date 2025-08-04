"""Serviço de domínio para manipulação de arquivos e sessões."""

import io
import shutil
import traceback
from os import path
from pathlib import Path
from typing import Any, AnyStr

import aiofiles
from clear import clear
from quart import request
from tqdm import tqdm
from werkzeug.datastructures import FileStorage

from addons.storage import Storage

workdir_path = Path(__file__).cwd()


class FileService:
    """Serviço de domínio para manipulação de arquivos e sessões de usuário."""

    async def save_file(self) -> None:
        """Salva um arquivo enviado para o diretório temporário especificado."""
        # file_data: MultiDict[
        #     str, FileStorage | WerkZeugFileStorage
        # ] = await request.files

        storage = Storage("minio")
        # sid = getattr(session, "sid", None)
        # _sid = str(sid) if sid else uuid4().hex
        # path_temp = workdir_path.joinpath("temp", _sid.upper())

        # path_temp.mkdir(exist_ok=True, parents=True)
        # for _, v in list(file_data.items()):
        #     file_name = secure_filename(v.filename)
        #     is_coroutine = iscoroutinefunction(v.save)
        #     file_path = path_temp.joinpath(file_name)

        #     self.stream = v.stream
        #     v.save = self.save.__get__(v, WerkZeugFileStorage)

        #     if is_coroutine:
        #         await v.save(path_temp.joinpath(file_name))
        #     elif not is_coroutine:
        #         v.save(path_temp.joinpath(file_name))

        #     path_minio = os.path.join(_sid.upper(), file_name)
        #     storage.upload_file(path_minio, file_path)

        try:
            data = await request.form
            _file = await request.files
            sid = str(request.sid)

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
            _index_size = index * chunksize

            # tqdm.write(f"index: {index}")
            # tqdm.write(f"end: {_end}")
            # tqdm.write(f"file size: {file_size}")

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
                    dest_path = path.join(sid.upper(), file_name)
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
