# noqa: D104

from __future__ import annotations

from typing import Any, Generator, Literal

from dotenv import dotenv_values
from minio import Minio as Client
from minio.credentials import EnvMinioProvider
from minio.xml import unmarshal

from addons.storage._bucket import Blob as Blob
from addons.storage._bucket import Bucket, ListBuckets
from addons.storage.credentials.providers import GoogleStorageCredentialsProvider

environ = dotenv_values()
storages = Literal["google", "minio"]


class Storage(Client):  # noqa: B903, D101
    def __init__(self, storage: storages) -> None:  # noqa: D107
        server_url = environ["MINIO_URL_SERVER"]
        if storage == "google":
            credentials = GoogleStorageCredentialsProvider()

        elif storage == "minio":
            credentials = EnvMinioProvider()

        super().__init__(endpoint=server_url, credentials=credentials, secure=False)

    @property
    def bucket(self) -> Bucket:  # noqa: D102
        """Get the default bucket."""
        bucket_name = environ["MINIO_BUCKET_NAME"]
        return Bucket(name=bucket_name, creation_date=None, client=self)

    def list_objects(  # noqa: D102
        self,
        prefix: str = None,
        recursive: str = False,
        start_after: str = None,
        include_user_meta: str = False,
        include_version: str = False,
        use_api_v1: str = False,
        use_url_encoding_type: str = True,
        fetch_owner: str = False,
        extra_headers: str = None,
        extra_query_params: str = None,
    ) -> Generator[Blob, Any, None]:
        return self.bucket.list_objects(
            prefix=prefix,
            recursive=recursive,
            start_after=start_after,
            include_user_meta=include_user_meta,
            include_version=include_version,
            use_api_v1=use_api_v1,
            use_url_encoding_type=use_url_encoding_type,
            fetch_owner=fetch_owner,
            extra_headers=extra_headers,
            extra_query_params=extra_query_params,
        )

    def list_buckets(self) -> list[Bucket]:
        """
        List information of all accessible buckets.

        :return: List of :class:`Bucket <Bucket>` object.

        Example::
            buckets = client.list_buckets()
            for bucket in buckets:
                print(bucket.name, bucket.creation_date)

        """
        response = self._execute("GET")
        result = unmarshal(ListBuckets, response.data.decode())
        return result.buckets
