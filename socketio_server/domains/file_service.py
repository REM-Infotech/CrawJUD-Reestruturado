"""Serviço de domínio para manipulação de arquivos e sessões."""

from typing import Any, AnyStr

from anyio import Path

from socketio_server.constructor.file import UploadableFile


class FileService:
    """Serviço de domínio para manipulação de arquivos e sessões de usuário."""

    async def save_file(self, file: UploadableFile, path_temp: Path) -> None:
        """Salva um arquivo enviado para o diretório temporário especificado."""
        await path_temp.mkdir(exist_ok=True, parents=True)
        async with await path_temp.joinpath(file.name).open("wb") as f:
            await f.write(file.file)

    async def save_session(
        self, server: Any, sid: str, session: dict[str, AnyStr], namespace: str | None = None
    ) -> None:
        """Armazena a sessão do usuário para um cliente na sessão do engineio."""
        namespace = namespace or "/"
        eio_sid = server.manager.eio_sid_from_sid(sid, namespace)
        eio_session = await server.eio.get_session(eio_sid)
        eio_session[namespace] = session
