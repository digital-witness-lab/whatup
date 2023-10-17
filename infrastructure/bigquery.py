from pulumi import Output

from pulumi_gcp import projects

from pulumi_google_native import bigquery, bigqueryconnection
from pulumi_google_native.bigqueryconnection.v1beta1 import (
    ConnectionArgs,
    CloudSqlPropertiesArgs,
    CloudSqlPropertiesType,
)

from config import location, project
from database import primary_cloud_sql_instance

messages_dataset = bigquery.v2.Dataset(
    "messages",
    bigquery.v2.DatasetArgs(
        description="BigQuery dataset for the messages DB.",
        location=location,
    ),
)

connection_args = ConnectionArgs(
    location=location,
    friendly_name="messages",
    description="Connection resource for running federated queries in BigQuery.",  # noqa: E501
    cloud_sql=CloudSqlPropertiesArgs(
        instance_id=primary_cloud_sql_instance.id,
        database="messages",
        type=CloudSqlPropertiesType.POSTGRES,
    ),
)

bigquery_sql_connection = bigqueryconnection.v1beta1.Connection(
    "bg-to-sql", args=connection_args
)

# Grant access to the service account automatically created
# by GCP when the above connection resource is created in
# the project.
#
# https://cloud.google.com/bigquery/docs/connect-to-sql#access-sql
projects.IAMMember(
    "bq-cloudsql-perm",
    member=Output.concat(
        "serviceAccount:service-",
        projects.get_project_output(filter=f"id:{project}").apply(
            lambda p: p.projects[0].number
        ),
        "@gcp-sa-bigqueryconnection.iam.gserviceaccount.com",
    ),
    role="roles/cloudsql.client",
)
