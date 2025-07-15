# noqa: D100
from datetime import datetime
from os import environ
from typing import List, Self

from dotenv import load_dotenv
from google.cloud.storage import Blob
from minio.datatypes import Bucket

from api.addons.storage.client.minio_client import MinioClient

load_dotenv()


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
