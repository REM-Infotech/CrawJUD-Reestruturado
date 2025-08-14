from __future__ import annotations

import io
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from minio.datatypes import Bucket as __Bucket
from minio.datatypes import ListAllMyBucketsResult
from minio.datatypes import Object as __Object
from minio.time import from_iso8601utc
from minio.xml import find, findall, findtext

if TYPE_CHECKING:
    from collections.abc import Generator
    from datetime import datetime

    from minio.helpers import ObjectWriteResult
    from minio.xml import Element
    from urllib3 import BaseHTTPResponse

    from crawjud.utils.storage import Storage
A = TypeVar("A", bound="ListBuckets")


class ListBuckets(ListAllMyBucketsResult):
    def __init__(self, buckets: list[__Bucket]) -> None:
        super().__init__(buckets=buckets)

    @classmethod
    def fromxml(cls, element: Element) -> Self:
        element = cast("Element", find(element, "Buckets", True))
        buckets = []
        elements = findall(element, "Bucket")
        for bucket in elements:
            name = cast("str", findtext(bucket, "Name", True))
            creation_date = findtext(bucket, "CreationDate")
            buckets.append(
                Bucket(
                    name,
                    from_iso8601utc(creation_date) if creation_date else None,
                ),
            )

        return cls(buckets=buckets)


class Bucket[T](__Bucket):
    client: Storage

    def __init__(self, name: str, creation_date: datetime, client: Storage) -> None:
        self.client = client
        super().__init__(name, creation_date)

    def list_objects(
        self,
        prefix: str | None = None,
        *,
        recursive: bool = True,
        start_after: str | None = None,
        include_user_meta: bool = False,
        include_version: bool = False,
        use_api_v1: bool = False,
        use_url_encoding_type: bool = True,
        fetch_owner: bool = False,
        extra_headers: str | None = None,
        extra_query_params: str | None = None,
    ) -> Generator[Blob, Any, None]:
        # Lista objetos do bucket conforme os parâmetros fornecidos.
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

    def get_object(
        self,
        object_name: str,
        offset: int = 0,
        length: int = 0,
        request_headers: T | None = None,
        ssec: T | None = None,
        version_id: str | None = None,
        extra_query_params: T | None = None,
    ) -> BaseHTTPResponse | None:
        with suppress(Exception):
            return self.client.get_object(
                bucket_name=self.name,
                object_name=object_name,
                offset=offset,
                length=length,
                request_headers=request_headers,
                ssec=ssec,
                version_id=version_id,
                extra_query_params=extra_query_params,
            )

        return None

    def append_object(
        self,
        object_name: str,
        data: bytes,
        length: int,
        chunk_size: int | None = None,
        content_type: str = "application/octet-stream",
        progress: T | None = None,
        extra_headers: T | None = None,
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
    _object_name: str | None = None
    client: Storage
    bucket: Bucket

    @classmethod
    def from_object(cls, _object: __Object, client: Storage, bucket: Bucket) -> Blob:
        """Crie uma instância de Blob a partir de um Object existente.

        Args:
            _object (__Object): Objeto de origem.
            client (Storage): Cliente de armazenamento.
            bucket (Bucket): Bucket associado.

        Returns:
            Blob: Instância de Blob criada a partir do Object.

        """
        return cls(ob=_object, client=client, bucket=bucket)

    @property
    def name(self) -> str:
        """Get the name of the blob."""
        if not self._object_name:
            self._object_name = self.object_name

        return self._object_name

    @name.setter
    def name(self, new_name: str) -> None:
        self._object_name = new_name

    def __init__(self, ob: __Object, client: Storage, bucket: Bucket) -> None:
        self.__dict__ = ob.__dict__
        self.client = client
        self.bucket = bucket

    def list_objects(
        self,
        *,
        recursive: bool = True,
        start_after: str | None = None,
        include_user_meta: bool = False,
        include_version: bool = False,
        use_api_v1: bool = False,
        use_url_encoding_type: bool = True,
        fetch_owner: bool = False,
        extra_headers: str | None = None,
        extra_query_params: str | None = None,
    ) -> Generator[Blob, Any, None]:
        # Lista objetos do bucket conforme os parâmetros fornecidos.
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
        if not self.is_dir:
            if isinstance(dest, str):
                dest = Path(dest)

            if "/" in self.name:
                split_bar = self.name.split("/")
                for _path in split_bar:
                    dest = dest.joinpath(_path)

                self.name = dest.name
                dest = dest.parent.resolve()
                dest.mkdir(exist_ok=True, parents=True)

            file_dest = str(dest.joinpath(self.name))

            self.client.fget_object(
                bucket_name=self.bucket_name,
                object_name=str(Path(dest.name).joinpath(self.name)),
                file_path=file_dest,
            )
