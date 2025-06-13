"""Serviço de domínio para manipulação de arquivos e sessões."""

from typing import Any, AnyStr

from anyio import Path
from quart import request
from quart.datastructures import FileStorage


class FileService:
    """Serviço de domínio para manipulação de arquivos e sessões de usuário."""

    async def save_file(self) -> None:
        """Salva um arquivo enviado para o diretório temporário especificado."""
        file_data = await request.files
        path_temp = (await Path(__file__).cwd()).joinpath("temp", file_data.get("id_temp"))
        for _, v in list(file_data.items()):
            value: FileStorage = v
            await value.save(path_temp)

    async def save_session(
        self, server: Any, sid: str, session: dict[str, AnyStr], namespace: str | None = None
    ) -> None:
        """Armazena a sessão do usuário para um cliente na sessão do engineio."""
        namespace = namespace or "/"
        eio_sid = server.manager.eio_sid_from_sid(sid, namespace)
        eio_session = await server.eio.get_session(eio_sid)
        eio_session[namespace] = session
