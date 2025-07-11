"""Serviço de domínio para manipulação de arquivos e sessões."""

from asyncio import iscoroutinefunction
from pathlib import Path
from typing import Any, AnyStr

from quart import request, session
from quart.datastructures import FileStorage
from werkzeug.datastructures import MultiDict
from werkzeug.datastructures.file_storage import FileStorage as WerkZeugFileStorage


class FileService:
    """Serviço de domínio para manipulação de arquivos e sessões de usuário."""

    async def save_file(self) -> None:
        """Salva um arquivo enviado para o diretório temporário especificado."""
        file_data: MultiDict[
            str, FileStorage | WerkZeugFileStorage
        ] = await request.files

        sid = getattr(session, "sid", None)
        path_temp = Path(__file__).cwd().joinpath("temp", sid)

        path_temp.mkdir(exist_ok=True, parents=True)
        for _, v in list(file_data.items()):
            is_coroutine = iscoroutinefunction(v.save)
            if is_coroutine:
                await v.save(path_temp.joinpath(v.filename))
            elif not is_coroutine:
                v.save(path_temp.joinpath(v.filename))

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
