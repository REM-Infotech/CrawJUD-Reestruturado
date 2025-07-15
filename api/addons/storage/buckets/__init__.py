# noqa: D104

from __future__ import annotations

from typing import Union

from api.addons.storage.buckets.google import GoogleBucket
from api.addons.storage.buckets.minio_bucket import MinioBucket
from api.addons.storage.types_storage import storages as storages

class_buckets = Union[GoogleBucket, MinioBucket]
classes: dict[str, class_buckets] = {"google": GoogleBucket, "minio": MinioBucket}


class BucketStorage(GoogleBucket, MinioBucket):  # noqa: D101
    """Abstract Class."""
