"""Serviço de domínio para manipulação de arquivos e sessões."""

from pathlib import Path
from typing import Any, AnyStr

import aiofiles
from quart import request

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

        data = await request.form
        sid = request.sid

        file_name = data.get("name")
        index = int(data.get("index", 0))
        total = int(data.get("total", 1))
        chunk_size = int(data.get("chunk_size"))
        chunk = data.get("chunk")
        content_type = data.get("content_type")

        if not all([file_name, chunk, content_type]):
            raise ValueError("Dados do chunk incompletos.")

        # Define diretório temporário para armazenar os chunks
        path_temp = Path(__file__).cwd().joinpath("temp", sid.upper())
        path_temp.mkdir(parents=True, exist_ok=True)
        file_path = path_temp.joinpath(file_name)

        # Salva o chunk no arquivo temporário
        mode = "ab" if index > 0 else "wb"

        storage.bucket.append_object(file_path.name, chunk, total, chunk_size)

        async with aiofiles.open(file_path, mode) as f:
            await f.write(chunk)

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
