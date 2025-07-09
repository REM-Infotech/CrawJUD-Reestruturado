"""Module to manage Google Cloud Storage (GCS) operations."""

from __future__ import annotations

import json
from os import environ
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from google.cloud.storage import Client
from google.oauth2.service_account import Credentials
from trio import Path

if TYPE_CHECKING:
    from typing import Any, Self

    from google.cloud.storage import Bucket


class GoogleClient:
    """Class for Google Storage Client."""

    PROJECT_ID: str
    CREDENDIALS: dict[str, Any]

    client_google: Client
    credentials_gcs: Credentials

    def __init__(self, **kwrgs: str) -> None:
        """Initialize class with args."""
        if len(kwrgs) == 0:
            load_dotenv(str(Path(__file__).cwd().joinpath("celery_app", ".env")))
            kwrgs = environ

        self.CREDENDIALS = json.loads(kwrgs["CREDENDIALS_GCS"])
        self.PROJECT_ID = kwrgs["GCS_PROJECT_ID"]
        self.BUCKET_STORAGE = kwrgs["GCS_BUCKET_STORAGE"]
        self.credentials_gcs = self.scope_credentials()
        self.client_google = self.storage_client()

    @classmethod
    def constructor(cls, **kwrgs: str) -> Self:
        """Client Google constructor."""
        return cls(**kwrgs)

    def scope_credentials(self) -> Credentials:
        """Create Google Cloud Storage credentials from environment variables.

        Returns:
            Credentials: GCS service account credentials.

        """
        return Credentials.from_service_account_info(
            json.loads(self.CREDENDIALS)
        ).with_scopes(
            ["https://www.googleapis.com/auth/cloud-platform"],
        )

    def storage_client(self) -> Client:
        """Create a Google Cloud Storage client.

        Returns:
            Client: Configured GCS client.

        """
        return Client(credentials=self.credentials_gcs, project=self.PROJECT_ID)

    def bucket_gcs(self) -> Bucket:
        """Retrieve the GCS bucket object.

        Args:
            storage_client (Client): The GCS client.

        Returns:
            Bucket: The GCS bucket.

        """
        return self.storage_client.bucket(self.BUCKET_STORAGE)
