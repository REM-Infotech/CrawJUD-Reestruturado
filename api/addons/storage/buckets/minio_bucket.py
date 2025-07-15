# noqa: D100
from datetime import datetime
from os import environ
from typing import Self

from minio.datatypes import Bucket

from api.addons.storage.client.minio_client import MinioClient


class MinioBucket(Bucket):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        client: MinioClient,
        name: str,
        user_project: str,
        creation_date: datetime,
    ) -> None:
        self._client = client
        self._user_project = user_project
        self._name = name
        self._creation_date = creation_date

    @classmethod
    def bucket(cls, storage_client: MinioClient) -> Self:
        """Retrieve the GCS bucket object.

        Args:
            storage_client (Client): The GCS client.

        Returns:
            Bucket: The GCS bucket.

        """
        bucket_name = environ["MINIO_BUCKET_NAME"]

        return cls(client=storage_client, name=bucket_name, user_project="local")
