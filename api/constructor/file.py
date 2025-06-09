"""Uploadable File."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class UploadableFile:
    """Uploadable File."""

    file: bytes  # Substitua por um tipo mais específico se souber (ex: io.BytesIO, etc)
    name: str
    id: Optional[Any] = None
    url: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
