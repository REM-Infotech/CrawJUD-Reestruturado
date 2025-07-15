# noqa: D104
from typing import Self, Union

from celery_app.addons.storage.client.google import GoogleClient
from celery_app.addons.storage.client.minio_client import MinioClient
from celery_app.addons.storage.types_storage import storages

class_clients = Union[GoogleClient, MinioClient]
classes: dict[str, class_clients] = {"google": GoogleClient, "minio": MinioClient}


class StorageClient(GoogleClient, MinioClient):  # noqa: D101
    @classmethod
    def constructor(cls, storage_name: storages) -> Self:  # noqa: D102
        return classes[storage_name].storage_client()
