# noqa: D100
from __future__ import annotations

from datetime import datetime
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, AnyStr, List, Self

from dotenv import load_dotenv
from google.cloud.storage import Blob

if TYPE_CHECKING:
    from addons.storage.client.minio_client import MinioClient

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
    def client(self) -> MinioClient:  # noqa: D102
        return self._client

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

    def list_blobs(  # noqa: D102
        self,
        prefix: str | None = None,
        recursive: bool = True,
    ) -> List[Blob]:
        list_files = self._client.list_objects(
            self._name,
            prefix=prefix,
            recursive=recursive,
        )
        files = []
        for item in list_files:
            files.append(item)

        if len(files) > 0:
            return [BlobMinIO(self, item.object_name, item) for item in files]

        return []

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
    _name: str = None
    _bucket: MinioBucket

    def __init__(  # noqa: D107
        self, bucket: MinioBucket = None, name: str = None, data: dict = None
    ) -> None:
        self.name = name
        self._data = data
        self._bucket = bucket

    @property
    def bucket(self) -> MinioBucket:  # noqa: D102
        return self._bucket

    @property
    def name(self) -> str:  # noqa: D102
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    def upload_from_filename(self, file_path: Path) -> None:  # noqa: D102
        self._bucket._client.fput_object(  # noqa: SLF001
            self._bucket.name,
            self.name,
            file_path=file_path,  # noqa: SLF001
        )

    def download_to_filename(self, *args: AnyStr, **kwargs: AnyStr) -> None:  # noqa: D102
        filename: Path = kwargs.pop("filename")

        data = self.bucket.client.get_object(self.bucket.name, self.name)

        filename.parent.mkdir(exist_ok=True, parents=True)

        with open(filename, "wb") as f:
            f.write(data.data)
