from __future__ import annotations

import io
import xml.etree.ElementTree as ET  # noqa: S405
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator, Type, TypeVar, cast

from minio.datatypes import Bucket as __Bucket
from minio.datatypes import ListAllMyBucketsResult
from minio.datatypes import Object as __Object
from minio.helpers import ObjectWriteResult
from minio.time import from_iso8601utc
from minio.xml import find, findall, findtext
from urllib3 import BaseHTTPResponse

if TYPE_CHECKING:
    from addons.storage import Storage  # noqa: F401

A = TypeVar("A", bound="ListBuckets")


class ListBuckets(ListAllMyBucketsResult):
    def __init__(self, buckets: list[__Bucket]) -> None:
        super().__init__(buckets=buckets)

    @classmethod
    def fromxml(cls: Type[A], element: ET.Element) -> A:
        """Create new object with values from XML element."""
        element = cast(ET.Element, find(element, "Buckets", True))
        buckets = []
        elements = findall(element, "Bucket")
        for bucket in elements:
            name = cast(str, findtext(bucket, "Name", True))
            creation_date = findtext(bucket, "CreationDate")
            buckets.append(
                Bucket(
                    name,
                    from_iso8601utc(creation_date) if creation_date else None,
                )
            )

        return cls(buckets=buckets)


class Bucket(__Bucket):
    client: Storage

    def __init__(self, name: str, creation_date: datetime, client: Storage) -> None:
        self.client = client
        super().__init__(name, creation_date)

    def list_objects(
        self,
        prefix: str = None,
        recursive: bool = True,
        start_after: str = None,
        include_user_meta: str = False,
        include_version: str = False,
        use_api_v1: str = False,
        use_url_encoding_type: str = True,
        fetch_owner: str = False,
        extra_headers: str = None,
        extra_query_params: str = None,
    ) -> Generator[Blob, Any, None]:
        for ob in self.client._list_objects(  # noqa: SLF001
            bucket_name=self.name,
            delimiter=None if recursive else "/",
            include_user_meta=include_user_meta,
            prefix=prefix,
            start_after=start_after,
            use_api_v1=use_api_v1,
            include_version=include_version,
            encoding_type="url" if use_url_encoding_type else None,
            fetch_owner=fetch_owner,
            extra_headers=extra_headers,
            extra_query_params=extra_query_params,
        ):
            yield Blob.from_object(ob, self.client, self)

    def get_object(  # noqa: ANN202
        self,
        object_name: str,
        offset: int = 0,
        length: int = 0,
        request_headers: Any | None = None,
        ssec: Any | None = None,
        version_id: str | None = None,
        extra_query_params: Any | None = None,
    ) -> BaseHTTPResponse | None:
        with suppress(Exception):
            return self.client.get_object(
                self.name,
                object_name,
                offset,
                length,
                request_headers,
                ssec,
                version_id,
                extra_query_params,
            )

        return None

    def append_object(
        self,
        object_name: str,
        data: bytes,
        length: int,
        chunk_size: int = None,
        content_type: str = "application/octet-stream",
        progress: Any = None,
        extra_headers: Any = None,
    ) -> ObjectWriteResult:
        if not self.get_object(object_name):
            return self.client.put_object(
                object_name=object_name,
                data=io.BytesIO(data),
                length=length,
                content_type=content_type,
            )

        size = length * 1024
        _chunktotal = chunk_size * 1024
        return self.client.append_object(
            object_name=object_name,
            data=io.BytesIO(data),
            length=size,
            progress=progress,
            extra_headers=extra_headers,
        )


class Blob(__Object):
    @classmethod
    def from_object(cls, _object: __Object, client: Storage, bucket: Bucket) -> Blob:
        """Create a Blob instance from an existing Object."""
        return cls(ob=_object, client=client, bucket=bucket)

    @property
    def name(self) -> str:
        """Get the name of the blob."""
        return self.object_name

    def __init__(self, ob: __Object, client: Storage, bucket: Bucket) -> None:
        self.__dict__ = ob.__dict__
        self.client = client
        self.bucket = bucket
        if not self.is_dir:
            del self.list_objects

    def list_objects(
        self,
        prefix: str = None,
        recursive: bool = True,
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
            prefix=self.name,
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

    def save(self, dest: Path | str) -> None:
        if hasattr(self, "is_dir"):
            return
        if isinstance(dest, str):
            dest = Path(dest)

        file_dest = str(dest.joinpath(self.name))

        self.client.fget_object(self.bucket_name, self.name, file_dest)
