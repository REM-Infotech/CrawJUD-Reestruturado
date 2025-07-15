# noqa: D104
from addons.storage.buckets.google_bucket import GoogleBucket
from addons.storage.buckets.minio_bucket import MinioBucket


class StorageBuckets(GoogleBucket, MinioBucket):  # noqa: D101
    abstract = True
