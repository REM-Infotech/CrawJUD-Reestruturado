# noqa: D100
from __future__ import annotations

from os import environ
from typing import TYPE_CHECKING, List, Self

from dotenv import load_dotenv
from google.cloud.storage import Blob, Bucket

load_dotenv()

if TYPE_CHECKING:
    from addons.storage.client.google import GoogleClient


class GoogleBucket(Bucket):  # noqa: D101
    @property
    def name(self) -> str:  # noqa: D102
        return self._name

    @classmethod
    def create_instance(cls, storage_client: GoogleClient) -> Self:  # noqa: D102
        bucket_name = environ["GCS_BUCKET_NAME"]

        return cls(name=bucket_name, user_project=storage_client.project)

    def list_blobs(self, prefix: str | None = None) -> List[Blob]:  # noqa: D102
        return super().list_blobs(prefix=prefix)

    def blob(  # noqa: ANN201, D102
        self,
        name: str,
        chunk_size: int | None = None,
        encryption_key: str | None = None,
        kms_key_name: str | None = None,
        generation: str | None = None,
    ) -> Blob:
        _blob = Blob(
            name=name,
            bucket=self,
            chunk_size=chunk_size,
            encryption_key=encryption_key,
            kms_key_name=kms_key_name,
            generation=generation,
        )

        return _blob
