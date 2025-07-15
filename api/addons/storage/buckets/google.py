"""Module to manage Google Cloud Storage (GCS) operations."""

from __future__ import annotations

from os import environ
from typing import Self

from dotenv import load_dotenv
from google.cloud.storage import Bucket

from api.addons.storage.client.google import GoogleClient

load_dotenv()


class GoogleBucket(Bucket):
    """Class for Google Storage Client."""

    @classmethod
    def bucket(cls, storage_client: GoogleClient) -> Self:
        """Retrieve the GCS bucket object.

        Args:
            storage_client (Client): The GCS client.

        Returns:
            Bucket: The GCS bucket.

        """
        bucket_name = environ["GCS_BUCKET_NAME"]
        project_id = environ["GCS_PROJECT_ID"]

        return cls(client=storage_client, name=bucket_name, user_project=project_id)
