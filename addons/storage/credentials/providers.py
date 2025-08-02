# noqa: D100
import json
from os import environ

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials as GoogleCredentials
from minio.credentials.credentials import Credentials
from minio.credentials.providers import Provider

load_dotenv()


class GoogleStorageCredentialsProvider(Provider):  # noqa: D101
    def retrieve(self) -> Credentials:  # noqa: D102
        json_credentials = json.loads(environ["GCS_CREDENTIALS"])
        credentials = GoogleCredentials.from_service_account_info(json_credentials)
        credentials = GoogleCredentials.with_scopes(
            ["https://www.googleapis.com/auth/cloud-platform"],
        )

        return Credentials(
            access_key=credentials.token, expiration=credentials.expiry
        )
