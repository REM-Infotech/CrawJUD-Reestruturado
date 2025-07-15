# noqa: D100
from __future__ import annotations

from datetime import datetime
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, List, Self

from dotenv import load_dotenv
from google.cloud.storage import Blob

if TYPE_CHECKING:
    from celery_app.addons.storage.client.minio_client import MinioClient

load_dotenv()


class MinioBucket:  # noqa: D101
    _name: str = None

    def __init__(  # noqa: D107
        self,
        client: MinioClient,
        name: str = None,
        user_project: str = None,
        creation_date: datetime = None,
    ) -> None:
        self._client = client
        self._user_project = user_project
        self._name = name
        self._creation_date = creation_date

    @property
    def name(self) -> str:  # noqa: D102
        return self._name

    @classmethod
    def create_instance(cls, storage_client: MinioClient) -> Self:
        """Retrieve the GCS bucket object.

        Args:
            storage_client (Client): The GCS client.

        Returns:
            Bucket: The GCS bucket.

        """
        bucket_name = environ["MINIO_BUCKET_NAME"]

        return cls(client=storage_client, name=bucket_name, user_project="local")

    def list_blobs(self) -> List[Blob]:  # noqa: D102
        return self._client.list_objects(self._name)

    def blob(self, name: str):  # noqa: ANN201, D102
        blob = None
        try:
            blob = BlobMinIO(
                self, name=name, data=self._client.get_object(self._name, name)
            )

        except Exception:
            blob = BlobMinIO(self, name)

        return blob


class BlobMinIO:  # noqa: D101
    def __init__(  # noqa: D107
        self, bucket: MinioBucket = None, name: str = None, data: dict = None
    ) -> None:
        self.name = name
        self._data = data
        self._bucket = bucket

    def upload_from_filename(self, file_path: Path) -> None:  # noqa: D102
        self._bucket._client.fput_object(  # noqa: SLF001
            self._bucket.name,
            self.name,
            file_path=file_path,  # noqa: SLF001
        )
