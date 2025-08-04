# noqa: D104

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO, Generator, Literal

from dotenv import dotenv_values
from minio import Minio as Client
from minio.credentials import EnvMinioProvider
from minio.helpers import ObjectWriteResult
from minio.xml import unmarshal
from tqdm import tqdm

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

    def upload_file(self, file_name: str, file_path: Path) -> None:  # noqa: D102
        """Upload a file to the bucket.

        Args:
            file_name (str): Nome do arquivo no bucket.
            file_path (Path): Caminho do arquivo local a ser enviado.

        Returns:
            None: Não retorna valor.

        Raises:
            FileNotFoundError: Caso o arquivo não seja encontrado.

        """
        # Verifica se o arquivo existe
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        file_size = file_path.stat().st_size
        chunk_size = 1024  # Tamanho do chunk em bytes

        # Abre o arquivo em modo binário
        with file_path.open("rb") as f:
            # Inicializa barra de progresso
            with tqdm(
                total=file_size, unit="B", unit_scale=True, desc=file_name
            ) as pbar:
                while True:
                    print(f)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    pbar.update(len(chunk))
                    self.bucket.append_object(file_name, chunk, 0)

    def put_object(  # noqa: D102
        self,
        object_name: str,
        data: BinaryIO,
        length: int,
        content_type: str = "application/octet-stream",
        metadata: Any | None = None,
        sse: Any | None = None,
        progress: Any | None = None,
        part_size: int = 0,
        num_parallel_uploads: int = 3,
        tags: Any | None = None,
        retention: Any | None = None,
        legal_hold: bool = False,
        write_offset: int | None = None,
    ) -> ObjectWriteResult:
        bucket_name = self.bucket.name

        return super().put_object(
            bucket_name,
            object_name,
            data,
            length,
            content_type,
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

    def append_object(  # noqa: D102
        self,
        object_name: str,
        data: bytes,
        length: int,
        chunk_size: int = None,
        content_type: str = "application/octet-stream",
        progress: Any = None,
        extra_headers: Any = None,
    ) -> ObjectWriteResult:
        return self.bucket.append_object(
            object_name,
            data,
            length,
            chunk_size,
            content_type,
            progress,
            extra_headers,
        )

    def download_files(self, dest: str | Path, prefix: str) -> None:  # noqa: D102
        files = self.bucket.list_objects(prefix=prefix, recursive=True)

        if isinstance(dest, str):
            dest = Path(dest)

        for file in files:
            self.fget_object(self.bucket.name, file.name, dest.joinpath(file.name))
