from pulumi import ResourceOptions
from pulumi_gcp import storage

from config import (
    is_prod_stack,
    location,
    temp_bucket_ttl_days,
    root_domain,
    dashboard_configs,
)

cors_origins = [
    f"{scheme}://{dashboard.domain}.{root_domain}"
    for dashboard in dashboard_configs.values()
    for scheme in ("http", "https")
]

print(cors_origins)

sessions_bucket = storage.Bucket(
    "dwl-sess",
    storage.BucketArgs(
        location=location,
        versioning=storage.BucketVersioningArgs(enabled=False),
        public_access_prevention="enforced",
        force_destroy=False if is_prod_stack() else True,
        uniform_bucket_level_access=True,
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
        uniform_bucket_level_access=True,
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
        uniform_bucket_level_access=True,
        cors=[
            storage.BucketCorArgs(
                methods=["GET", "HEAD"],
                origins=cors_origins,
                response_headers=["Content-Type", "ETag"],
                max_age_seconds=60 * 60 * 24,
            )
        ],
    ),
    opts=ResourceOptions(protect=is_prod_stack()),
)


temp_bucket = storage.Bucket(
    "dwl-temp",
    storage.BucketArgs(
        location=location,
        versioning=storage.BucketVersioningArgs(enabled=False),
        public_access_prevention="enforced",
        force_destroy=False if is_prod_stack() else True,
        uniform_bucket_level_access=True,
        lifecycle_rules=[
            storage.BucketLifecycleRuleArgs(
                action=storage.BucketLifecycleRuleActionArgs(type="Delete"),
                condition=storage.BucketLifecycleRuleConditionArgs(
                    age=temp_bucket_ttl_days
                ),
            )
        ],
    ),
    opts=ResourceOptions(protect=is_prod_stack()),
)
