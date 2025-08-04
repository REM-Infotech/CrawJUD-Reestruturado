"""Serviço de domínio para manipulação de arquivos e sessões."""

import os
from asyncio import iscoroutinefunction
from pathlib import Path
from typing import Any, AnyStr
from uuid import uuid4

from quart import request, session
from quart.datastructures import FileStorage
from werkzeug.datastructures import MultiDict
from werkzeug.datastructures.file_storage import FileStorage as WerkZeugFileStorage
from werkzeug.utils import secure_filename

from addons.storage import Storage

workdir_path = Path(__file__).cwd()


class FileService:
    """Serviço de domínio para manipulação de arquivos e sessões de usuário."""

    async def save_file(self) -> None:
        """Salva um arquivo enviado para o diretório temporário especificado."""
        file_data: MultiDict[
            str, FileStorage | WerkZeugFileStorage
        ] = await request.files

        storage = Storage("minio")
        sid = getattr(session, "sid", None)
        _sid = str(sid) if sid else uuid4().hex
        path_temp = workdir_path.joinpath("temp", _sid.upper())

        path_temp.mkdir(exist_ok=True, parents=True)
        for _, v in list(file_data.items()):
            file_name = secure_filename(v.filename)
            is_coroutine = iscoroutinefunction(v.save)
            file_path = path_temp.joinpath(file_name)

            self.stream = v.stream
            v.save = self.save.__get__(v, WerkZeugFileStorage)

            if is_coroutine:
                await v.save(path_temp.joinpath(file_name))
            elif not is_coroutine:
                v.save(path_temp.joinpath(file_name))

            path_minio = os.path.join(_sid.upper(), file_name)
            storage.upload_file(path_minio, file_path)

    def save(self, path: Path) -> None:  # noqa: D102
        chunk_size = 16384
        mode = "wb" if not Path(path).exists() else "ab"
        with Path(path).open(mode) as file_:
            data = self.stream.read(chunk_size)
            while data != b"":
                file_.write(data)
                data = self.stream.read(chunk_size)

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
