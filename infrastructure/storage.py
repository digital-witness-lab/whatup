from pulumi_gcp import storage

from .config import location

# Cloud Storage buckets will be used as network filesystem using gcsfuse
# in Cloud Run services.
# https://cloud.google.com/run/docs/tutorials/network-filesystems-fuse

whatupcore2_bucket = storage.Bucket(
    "whatupcore2Bucket",
    storage.BucketArgs(
        name="dwl-whatupcore2",
        location=location,
        versioning=storage.BucketVersioningArgs(enabled=True),
        public_access_prevention="enforced",
    ),
)

sessions_bucket = storage.Bucket(
    "sessionsBucket",
    storage.BucketArgs(
        name="dwl-sessions",
        location=location,
        versioning=storage.BucketVersioningArgs(enabled=True),
        public_access_prevention="enforced",
    ),
)

message_archive_bucket = storage.Bucket(
    "messageArchiveBucket",
    storage.BucketArgs(
        name="dwl-message-archive",
        location=location,
        versioning=storage.BucketVersioningArgs(enabled=True),
        public_access_prevention="enforced",
    ),
)
