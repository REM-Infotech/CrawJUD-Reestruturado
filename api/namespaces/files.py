"""Socket.IO namespace for bot file operations and session management."""

import asyncio
from typing import AnyStr

from anyio import Path
from quart_socketio import Namespace, SocketIO
from tqdm import tqdm

from api.constructor.file import UploadableFile
from api.domains.file_service import FileService
from api.types import ASyncServerType


class FileNamespaces(Namespace):
    """Socket.IO namespace for handling file uploads, session management, and selector data for bots."""

    namespace: str
    server: ASyncServerType

    def __init__(self, namespace: str, io: SocketIO) -> None:
        """Initialize FileNamespaces with namespace and server, and inject FileService."""
        super().__init__(namespace, io)
        self.namespace = namespace
        self.file_service = FileService()

    async def on_add_file(self) -> None:
        """Handle file upload event from a client (e.g., FormBot).

        Receives file data, constructs an UploadableFile, and saves it asynchronously to a temporary directory.

        Args:
            sid: The session ID of the client.
            data: Dictionary containing file data and a temporary ID ('id_temp').

        """
        asyncio.create_task(self.file_service.save_file())

    async def on_connect(self) -> None:
        """Handle client connection event.

        Creates and saves a session for the connected client.

        Args:
            sid: The session ID of the client.
            environ: The WSGI environment dictionary for the connection.

        """
        tqdm.write(f"Client connected to namespace {self.namespace}")

    async def on_disconnect(self) -> None:
        """Handle client disconnection event.

        Args:
            sid: The session ID of the client.
            reason: The reason for disconnection.

        """

    async def on_get_selectors_data(self) -> dict[str, list[dict[str, str]]]:
        """Provide selector data for the client (e.g., dropdown options).

        Args:
            sid: The session ID of the client.
            data: Additional data from the client (unused).

        Returns:
            A dictionary with selector options for credentials and other info.

        """
        return {
            "credentials": [{"value": None, "text": "Selecione o Estado", "disabled": True}],
            "other_info": [{"value": None, "text": "Selecione o Estado", "disabled": True}],
        }

    async def save_session(self, sid: str, session: dict[str, AnyStr], namespace: str | None = None) -> None:
        """Delegate to FileService.save_session (deprecated)."""
        await self.file_service.save_session(self.server, sid, session, namespace)

    async def save_file(self, file: UploadableFile, path_temp: Path) -> None:
        """Delegate to FileService.save_file (deprecated)."""
        await self.file_service.save_file(file, path_temp)
