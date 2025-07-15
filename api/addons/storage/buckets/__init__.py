# noqa: D104

from __future__ import annotations

from typing import Self, Union

from api.addons.storage.buckets.google import GoogleBucket
from api.addons.storage.types_storage import storages

class_buckets = Union[GoogleBucket]
classes: dict[str, class_buckets] = {"google": GoogleBucket, "minio": "MinioClient"}


class BucketStorage(GoogleBucket):  # noqa: D101
    @classmethod
    def constructor(cls, storage_name: storages) -> Self:  # noqa: D102
        return classes[storage_name].storage_client()
