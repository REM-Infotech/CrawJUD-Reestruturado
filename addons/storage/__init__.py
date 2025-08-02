# noqa: D104

from __future__ import annotations

from contextlib import suppress
from typing import Iterator, Literal, cast

from dotenv import dotenv_values
from minio import Minio as Client
from minio.credentials import EnvMinioProvider
from minio.datatypes import (
    check_bucket_name,
    parse_list_objects,
)
from minio.helpers import DictType
from minio.xml import unmarshal

from addons.storage._bucket import Blob, Bucket, ListBuckets
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

    def _list_objects(
        self,
        bucket_name: str,
        continuation_token: str | None = None,  # listV2 only
        delimiter: str | None = None,  # all
        encoding_type: str | None = None,  # all
        fetch_owner: bool | None = None,  # listV2 only
        include_user_meta: bool = False,  # MinIO specific listV2.
        max_keys: int | None = None,  # all
        prefix: str | None = None,  # all
        start_after: str | None = None,
        # all: v1:marker, versioned:key_marker
        version_id_marker: str | None = None,  # versioned
        use_api_v1: bool = False,
        include_version: bool = False,
        extra_headers: DictType | None = None,
        extra_query_params: DictType | None = None,
    ) -> Iterator[Blob]:
        """
        List objects optionally including versions.

        :Note:
            Its required to send empty values to delimiter/prefix and 1000 to
            max-keys when not provided for server-side bucket policy evaluation to
            succeed; otherwise AccessDenied error will be returned for such
            policies.

        """
        with suppress(Exception):
            check_bucket_name(bucket_name, s3_check=self._base_url.is_aws_host)

            if version_id_marker:
                include_version = True

            is_truncated = True
            while is_truncated:
                query = extra_query_params or {}
                if include_version:
                    query["versions"] = ""
                elif not use_api_v1:
                    query["list-type"] = "2"

                if not include_version and not use_api_v1:
                    if continuation_token:
                        query["continuation-token"] = continuation_token
                    if fetch_owner:
                        query["fetch-owner"] = "true"
                    if include_user_meta:
                        query["metadata"] = "true"
                query["delimiter"] = delimiter or ""
                if encoding_type:
                    query["encoding-type"] = encoding_type
                query["max-keys"] = str(max_keys or 1000)
                query["prefix"] = prefix or ""
                if start_after:
                    if include_version:
                        query["key-marker"] = start_after
                    elif use_api_v1:
                        query["marker"] = start_after
                    else:
                        query["start-after"] = start_after
                if version_id_marker:
                    query["version-id-marker"] = version_id_marker

                response = self._execute(
                    "GET",
                    bucket_name,
                    query_params=cast(DictType, query),
                    headers=extra_headers,
                )

                objects, is_truncated, start_after, version_id_marker = (
                    parse_list_objects(response)
                )

                if not include_version:
                    version_id_marker = None
                    if not use_api_v1:
                        continuation_token = start_after

                yield from objects

    # @classmethod
    # def storage_client(cls) -> Self:
    #     """Create a Google Cloud Storage client.

    #     Returns:
    #         Client: Configured GCS client.

    #     """
    #     bucket_name = environ["GCS_BUCKET_NAME"]
    #     project_id = environ["GCS_PROJECT_ID"]

    #     return cls(
    #         credentials=cls.scope_credentials(credentials),
    #         project=project_id,
    #     )

    # def bucket(self) -> StorageBuckets:  # noqa: D102
    #     return MinioBucket.create_instance(self)

    # @classmethod
    # def scope_credentials(cls) -> Credentials:
    #     """Create MinIO credentials from environment variables.

    #     Returns:
    #         Credentials: MinIO service account credentials.

    #     """
    #     return EnvMinioProvider()

    # def storage_client(self) -> Self:  # noqa: D102
    #     server_url = environ["MINIO_URL_SERVER"]
    #     return cls(server_url, credentials=, secure=False)
