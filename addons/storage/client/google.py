# noqa: D100

from __future__ import annotations

import json
from os import environ
from typing import Self

from dotenv import load_dotenv
from google.cloud.storage import Client
from google.oauth2.service_account import Credentials

from addons.storage.buckets import StorageBuckets

load_dotenv()


class GoogleClient(Client):  # noqa: D101
    @classmethod
    def scope_credentials(cls, credentials: str) -> Credentials:
        """Create Google Cloud Storage credentials from environment variables.

        Returns:
            Credentials: GCS service account credentials.

        """
        return Credentials.from_service_account_info(
            json.loads(credentials)
        ).with_scopes(
            ["https://www.googleapis.com/auth/cloud-platform"],
        )

    @classmethod
    def storage_client(cls) -> Self:
        """Create a Google Cloud Storage client.

        Returns:
            Client: Configured GCS client.

        """
        project_id = environ["GCS_PROJECT_ID"]
        credentials = environ["GCS_CREDENTIALS"]

        return cls(
            credentials=cls.scope_credentials(credentials),
            project=project_id,
        )

    def bucket(self) -> StorageBuckets:  # noqa: D102
        bucket_name = environ["GCS_BUCKET_NAME"]
        return super().bucket(bucket_name)
