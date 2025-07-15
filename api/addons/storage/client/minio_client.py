# noqa: D100
from __future__ import annotations

from os import environ
from typing import TYPE_CHECKING, Self

from dotenv import load_dotenv
from minio import Minio as Client
from minio.credentials import EnvMinioProvider

from api.addons.storage.buckets.minio_bucket import MinioBucket

load_dotenv()

if TYPE_CHECKING:
    from minio.credentials.credentials import Credentials


class MinioClient(Client):  # noqa: D101
    @classmethod
    def scope_credentials(cls) -> Credentials:
        """Create MinIO credentials from environment variables.

        Returns:
            Credentials: MinIO service account credentials.

        """
        return EnvMinioProvider()

    @classmethod
    def storage_client(cls) -> Self:  # noqa: D102
        server_url = environ["MINIO_URL_SERVER"]

        return cls(server_url, credentials=cls.scope_credentials(), secure=False)

    def bucket(self) -> MinioBucket:  # noqa: D102
        return MinioBucket.create_instance(self)


# def main():
#     # Create a client with the MinIO server playground, its access key
#     # and secret key.

#     # The file to upload, change this path if needed
#     source_file = "/tmp/test-file.txt"

#     client = MinioClient.storage_client()
#     # The destination bucket and filename on the MinIO server
#     bucket_name = "python-test-bucket"
#     destination_file = "my-test-file.txt"

#     # Make the bucket if it doesn't exist.
#     found = client.bucket_exists(bucket_name)
#     if not found:
#         client.make_bucket(bucket_name)
#         print("Created bucket", bucket_name)
#     else:
#         print("Bucket", bucket_name, "already exists")

#     # Upload the file, renaming it in the process
#     client.fput_object(
#         bucket_name,
#         destination_file,
#         source_file,
#     )
#     print(
#         source_file,
#         "successfully uploaded as object",
#         destination_file,
#         "to bucket",
#         bucket_name,
#     )


# if __name__ == "__main__":
#     try:
#         main()
#     except S3Error as exc:
#         print("error occurred.", exc)
