# noqa: D104

from __future__ import annotations

from pathlib import Path

from api.addons.storage.client import StorageClient
from api.addons.storage.types_storage import storages


class Storage:  # noqa: B903, D101
    storage: str
    client: StorageClient

    def __init__(self, storage: storages) -> None:  # noqa: D107
        self.storage = storage
        self.client = StorageClient.constructor(storage)
        self.bucket = self.client.bucket()

    async def upload_file(self, file_name: str, file_path: Path) -> None:  # noqa: D102
        blob = self.bucket.blob(file_name)
        blob.upload_from_filename(file_path)
