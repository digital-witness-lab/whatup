from pulumi import ResourceOptions

from pulumi_gcp import storage

from config import location, is_prod_stack

# Cloud Storage buckets will be used as network filesystem using gcsfuse
# in Cloud Run services.
# https://cloud.google.com/run/docs/tutorials/network-filesystems-fuse

sessions_bucket = storage.Bucket(
    "dwl-sess",
    storage.BucketArgs(
        location=location,
        versioning=storage.BucketVersioningArgs(enabled=False),
        public_access_prevention="enforced",
        force_destroy=False if is_prod_stack() else True,
    ),
    opts=ResourceOptions(protect=is_prod_stack()),
)

message_archive_bucket = storage.Bucket(
    "dwl-msgarc",
    storage.BucketArgs(
        location=location,
        versioning=storage.BucketVersioningArgs(enabled=False),
        public_access_prevention="enforced",
        force_destroy=False if is_prod_stack() else True,
    ),
    opts=ResourceOptions(protect=is_prod_stack()),
)

media_bucket = storage.Bucket(
    "dwl-media",
    storage.BucketArgs(
        location=location,
        versioning=storage.BucketVersioningArgs(enabled=False),
        public_access_prevention="enforced",
        force_destroy=False if is_prod_stack() else True,
    ),
    opts=ResourceOptions(protect=is_prod_stack()),
)
