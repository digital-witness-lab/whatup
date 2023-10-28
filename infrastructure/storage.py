from pulumi import ResourceOptions

from pulumi_gcp import storage

from config import location, is_prod_stack

# Cloud Storage buckets will be used as network filesystem using gcsfuse
# in Cloud Run services.
# https://cloud.google.com/run/docs/tutorials/network-filesystems-fuse

whatupcore2_bucket = storage.Bucket(
    "dwl-core2",
    storage.BucketArgs(
        location=location,
        # Enabling versioning will produce unpredictable behavior with
        # gcsfuse.
        versioning=storage.BucketVersioningArgs(enabled=False),
        public_access_prevention="enforced",
        force_destroy=False if is_prod_stack() else True,
    ),
    opts=ResourceOptions(protect=is_prod_stack()),
)

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
