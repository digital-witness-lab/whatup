from pulumi import ResourceOptions, get_stack

from pulumi_gcp import storage, artifactregistry

from config import location, is_prod_stack

# Cloud Storage buckets will be used as network filesystem using gcsfuse
# in Cloud Run services.
# https://cloud.google.com/run/docs/tutorials/network-filesystems-fuse

# Create an Artifact Registry repository
repository = artifactregistry.Repository(
    "whatup-repo",
    repository_id=f"whatup-{get_stack()}-repo",
    description="Repository for whatup container image",
    format="DOCKER",
    location=location,
)

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
