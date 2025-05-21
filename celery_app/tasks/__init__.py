"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING

from celery.app import shared_task

from celery_app.addons.mail import Mail
from celery_app.addons.storage.google import GoogleClient

if TYPE_CHECKING:
    from celery_app.types import StrPath, TReturnMessageMail, TReturnMessageUploadFile


@shared_task
def send_email(subject: str, to: str, message: str, files_path: list[str] = None) -> TReturnMessageMail:
    """Send an email to the specified recipient."""
    mail = Mail.construct()
    mail.message["Subject"] = subject
    mail.message["To"] = to
    mail.message.attach(message)

    if len(files_path) > 0:
        for file in files_path:
            mail.attach_file(file)

    mail.send_message(to=to)

    return "E-mail enviado com sucesso!"


@shared_task
def upload_file(file_path: StrPath) -> TReturnMessageUploadFile:
    """Upload a file to Google Cloud Storage.

    Args:
        file_path (Path): The path file to upload.

    Returns:
        str: The basename of the uploaded file if successful, else None.

    Raises:
        Exception: If an error occurs during the upload process.

    """
    file = Path(file_path).resolve()
    file_name = file.name

    storage = GoogleClient.constructor()
    bucket = storage.bucket_gcs()

    # Create a Blob object in the bucket
    blob = bucket.blob(file_name)

    # Upload the local file to the Blob object

    content_type, _ = mimetypes.guess_type(file)

    blob.upload_from_filename(file, content_type=content_type)

    return "Arquivo enviado com sucesso!"
