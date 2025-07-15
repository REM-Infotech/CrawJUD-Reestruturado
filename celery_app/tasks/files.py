"""Modulo de gerenciamento de tarefas do Celery."""

# from __future__ import annotations

# import mimetypes
# from pathlib import Path
# from typing import TYPE_CHECKING

# from celery.app import shared_task

# from addons.storage import Storage

# if TYPE_CHECKING:
#     from celery_app.types import StrPath, TReturnMessageUploadFile


# @shared_task
# def upload_file(file_path: StrPath) -> TReturnMessageUploadFile:
#     """Upload a file to Google Cloud Storage.

#     Args:
#         file_path (Path): The path file to upload.

#     Returns:
#         str: The basename of the uploaded file if successful, else None.

#     Raises:
#         Exception: If an error occurs during the upload process.

#     """
#     file = Path(file_path).resolve()
#     file_name = file.name

#     storage = Storage()
#     bucket = storage.bucket_gcs()

#     # Create a Blob object in the bucket
#     blob = bucket.blob(file_name)

#     # Upload the local file to the Blob object

#     content_type, _ = mimetypes.guess_type(file)

#     blob.upload_from_filename(file, content_type=content_type)

#     return "Arquivo enviado com sucesso!"
