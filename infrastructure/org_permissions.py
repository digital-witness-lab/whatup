from pulumi import get_stack, Output
import pulumi_gcp as gcp

from storage import media_bucket
from config import project, customer_id


def create_group(name, roles):
    # Create a Cloud Identity Group.
    group = gcp.cloudidentity.Group(
        f"{name}-{get_stack()}",
        gcp.cloudidentity.GroupArgs(
            display_name=name,
            parent=f"customers/{customer_id}",
            group_key=gcp.cloudidentity.GroupGroupKeyArgs(
                id=f"{name}-{get_stack()}@digitalwitnesslab.org",  # Replace with the desired group email
            ),
            labels={
                "cloudidentity.googleapis.com/groups.discussion_forum": ""
            },
            initial_group_config="WITH_INITIAL_OWNER",
        ),
    )

    # List of roles to be assigned to the group.

    # Create IAM policies for each role and attach them to the group.
    for role in roles:
        gcp.projects.IAMMember(
            f"{name}-{role.replace('/', '-')}",
            project=project,
            role=role,
            member=Output.concat(
                "group:", group.group_key.apply(lambda key: key.id)
            ),
        )

    return group


data_viewers = create_group(
    "data-viewers",
    roles=[
        "roles/bigquery.dataViewer",
        "roles/bigquery.jobUser",
        "roles/bigquery.user",
        "roles/looker.viewer",
    ],
)

condition = gcp.storage.BucketIAMMemberConditionArgs(
    title="LimitToSpecificBucket",
    expression=f"resource.name == 'projects/_/buckets/{media_bucket.name}'",
)
data_viewers_media_role = "roles/storage.objectViewer"
gcp.storage.BucketIAMMember(
    "data-viewers-media-ro",
    role=data_viewers_media_role,
    bucket=media_bucket.name,
    member=Output.concat(
        "group:", data_viewers.group_key.apply(lambda key: key.id)
    ),
    condition=condition,
)

data_editors = create_group(
    "data-editor",
    roles=[
        "roles/bigquery.dataEditor",
        "roles/bigquery.jobUser",
        "roles/looker.instanceUser",
        "roles/looker.viewer",
        "roles/storage.objectViewer",
    ],
)
