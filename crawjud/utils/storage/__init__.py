# noqa: D104

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Literal

from dotenv import dotenv_values
from minio import Minio as Client
from minio.credentials import EnvMinioProvider
from minio.xml import unmarshal
from tqdm import tqdm

from crawjud.utils.storage._bucket import Blob as Blob
from crawjud.utils.storage._bucket import Bucket, ListBuckets
from crawjud.utils.storage.credentials.providers import (
    GoogleStorageCredentialsProvider,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from minio.datatypes import Object
    from minio.helpers import ObjectWriteResult
environ = dotenv_values()
storages = Literal["google", "minio"]


class ArquivoNaoEncontradoError(FileNotFoundError):
    """Empty."""

    message: str

    def __init__(self, message: str, *args) -> None:
        """Empty."""
        self.message = message
        super().__init__(*args)

    def __str__(self) -> str:
        """Empty.

        Returns:
            str: string

        """
        return self.message


class Storage[T](Client):  # noqa: D101
    def __init__(self, storage: storages) -> None:  # noqa: D107
        server_url = environ["MINIO_URL_SERVER"]
        if storage == "google":
            credentials = GoogleStorageCredentialsProvider()

        elif storage == "minio":
            credentials = EnvMinioProvider()

        super().__init__(endpoint=server_url, credentials=credentials, secure=False)

    @property
    def bucket(self) -> Bucket:
        """Get the default bucket."""
        bucket_name = environ["MINIO_BUCKET_NAME"]
        return Bucket(name=bucket_name, creation_date=None, client=self)

    def list_objects(
        self,
        prefix: str | None = None,
        start_after: str | None = None,
        extra_headers: str | None = None,
        extra_query_params: str | None = None,
        *,
        recursive: str | None = False,
        include_user_meta: str | None = False,
        include_version: str | None = False,
        use_api_v1: str | bool = False,
        use_url_encoding_type: str | None = True,
        fetch_owner: str | bool = False,
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
        """List information of all accessible buckets.

        Returns:
            list: List of :class:`Bucket <Bucket>` object.

        Example::
            buckets = client.list_buckets()
            for bucket in buckets:
                print(bucket.name, bucket.creation_date)

        """
        response = self._execute("GET")
        result = unmarshal(ListBuckets, response.data.decode())
        return result.buckets

    def upload_file(self, file_name: str, file_path: Path) -> None:
        """Upload a file to the bucket.

        Args:
            file_name (str): Nome do arquivo no bucket.
            file_path (Path): Caminho do arquivo local a ser enviado.



        Raises:
            ArquivoNaoEncontradoError: Caso o arquivo não seja encontrado.

        """
        # Verifica se o arquivo existe
        if not file_path.exists():
            raise ArquivoNaoEncontradoError(
                message=f"Arquivo não encontrado: {file_path}",
            )

        file_size = file_path.stat().st_size
        chunk_size = 1024  # Tamanho do chunk em bytes

        # Abre o arquivo em modo binário
        with (
            file_path.open("rb") as f,
            tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                desc=file_name,
            ) as pbar,
        ):
            # Inicializa barra de progresso
            while True:
                tqdm.write(str(f))
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                pbar.update(len(chunk))
                self.bucket.append_object(file_name, chunk, 0)

    def fget_object(
        self,
        object_name: str,
        file_path: str,
        request_headers: T | None = None,
        ssec: T | None = None,
        version_id: str | None = None,
        extra_query_params: T | None = None,
        tmp_file_path: str | None = None,
        progress: T | None = None,
    ) -> Object:
        bucket_name = self.bucket.name
        return super().fget_object(
            bucket_name,
            object_name,
            file_path,
            request_headers,
            ssec,
            version_id,
            extra_query_params,
            tmp_file_path,
            progress,
        )

    def fput_object(
        self,
        object_name: str,
        file_path: str,
        content_type: str = "application/octet-stream",
        metadata: T | None = None,
        sse: T | None = None,
        progress: T | None = None,
        part_size: int = 0,
        num_parallel_uploads: int = 3,
        tags: T | None = None,
        retention: T | None = None,
        *,
        legal_hold: bool = False,
    ) -> ObjectWriteResult:
        bucket_name = self.bucket.name
        return super().fput_object(
            bucket_name,
            object_name,
            file_path,
            content_type,
            metadata,
            sse,
            progress,
            part_size,
            num_parallel_uploads,
            tags,
            retention,
            legal_hold,
        )

    def put_object(
        self,
        object_name: str,
        data: BinaryIO,
        length: int,
        metadata: T | None = None,
        sse: T | None = None,
        progress: T | None = None,
        part_size: int = 0,
        num_parallel_uploads: int = 3,
        tags: T | None = None,
        retention: T | None = None,
        write_offset: int | None = None,
        *,
        legal_hold: bool = False,
    ) -> ObjectWriteResult:
        bucket_name = self.bucket.name

        return super().put_object(
            bucket_name,
            object_name,
            data,
            length,
            metadata,
            sse,
            progress,
            part_size,
            num_parallel_uploads,
            tags,
            retention,
            legal_hold,
            write_offset,
        )

    def append_object(
        self,
        object_name: str,
        data: bytes,
        length: int,
        chunk_size: int | None = None,
        progress: T = None,
        extra_headers: T = None,
    ) -> ObjectWriteResult:
        bucket_name = self.bucket.name
        return super().append_object(
            bucket_name,
            object_name,
            data,
            length,
            chunk_size,
            progress,
            extra_headers,
        )

    def download_files(self, dest: str | Path, prefix: str) -> None:
        files = self.bucket.list_objects(prefix=prefix, recursive=True)

        if isinstance(dest, str):
            dest = Path(dest)

        for file in files:
            self.fget_object(self.bucket.name, file.name, dest.joinpath(file.name))
