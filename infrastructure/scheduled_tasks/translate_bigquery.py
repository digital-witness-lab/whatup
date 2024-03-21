import json

from pulumi_gcp import projects, bigquery
from pulumi import Output, ResourceOptions, get_stack
from pulumi_google_native import bigquerydatatransfer as dts

from config import bq_dataset_region, project, is_prod_stack
from bigquery import bq_dataset_id, transfers_role


translate_connection = bigquery.Connection(
    f"con-trans-msg-en-{get_stack()}",
    location=bq_dataset_region,
    connection_id=f"con-trans-msg-en-{get_stack()}",
    cloud_resource=bigquery.ConnectionCloudResourceArgs(),
    description="Connection to vertex AI for translation of messages",  # noqa: E501
)

service_account_email = (
    translate_connection.cloud_resource.service_account_id.apply(
        lambda sid: sid.split("/")[-1]
    )
)

# Permissions from https://cloud.google.com/bigquery/docs/translate-text#required_permissions
translate_dts_role = projects.IAMCustomRole(
    "translate-dts-role",
    projects.IAMCustomRoleArgs(
        # GCP wants this to be a camel-cased role id.
        # The regex for this disallows the use of dashes(-).
        role_id=f"translateDTSRole{get_stack().casefold().replace('-', '_')}",
        permissions=[
            "bigquery.jobs.create",
            "bigquery.models.create",
            "bigquery.models.getData",
            "bigquery.models.updateData",
            "bigquery.models.updateMetadata",
            "bigquery.tables.getData",
            "bigquery.models.getData",
            "bigquery.jobs.create",
        ],
        title="BigQuery Translate DTS Role",
        stage="GA",
    ),
)

translate_dts_perm = projects.IAMMember(
    "con-trans-msg-en-dts",
    member=Output.concat("serviceAccount:", service_account_email),
    project=project,
    role=Output.concat("roles/").concat(translate_dts_role.name),
)

transfers_perm = projects.IAMMember(
    "con-trans-msg-en-tr",
    member=Output.concat("serviceAccount:", service_account_email),
    project=project,
    role=Output.concat("roles/").concat(transfers_role.name),
)


service_usage_consumer = projects.IAMMember(
    "con-trans-msg-en-suc",
    member=Output.concat("serviceAccount:", service_account_email),
    project=project,
    role="roles/serviceusage.serviceUsageConsumer",
)

connection_user = projects.IAMMember(
    "con-trans-msg-en-cu",
    member=Output.concat("serviceAccount:", service_account_email),
    project=project,
    role="roles/bigquery.connectionUser",
)

cloud_translate_user = projects.IAMMember(
    "con-trans-msg-en-ctu",
    member=Output.concat("serviceAccount:", service_account_email),
    project=project,
    role="roles/cloudtranslate.user",
)

results_table = bigquery.Table(
    "messages_english",
    dataset_id=bq_dataset_id,
    table_id="messages_english",
    schema=json.dumps(
        [
            {
                "name": "text_hash",
                "type": "INT64",
                "description": "FarmHash of original text",
            },
            {
                "name": "lang_orig",
                "type": "STRING",
                "description": "Original text ISO code",
            },
            {
                "name": "text_orig",
                "type": "STRING",
                "description": "Original text",
            },
            {
                "name": "text_translate",
                "type": "STRING",
                "description": "Translated text",
            },
            {
                "name": "status",
                "type": "STRING",
                "description": "Status of the translation",
            },
            {
                "name": "timestamp",
                "type": "DATETIME",
                "description": "When the translation happened",
            },
        ]
    ),
)

query = Output.all(
    dataset_id=bq_dataset_id,
    results_table=results_table.table_id,
    conn_name=translate_connection.name,
).apply(
    lambda args: f"""
    CREATE OR REPLACE MODEL
    `{args['dataset_id']}.translation_model`
    REMOTE WITH CONNECTION `{args['conn_name']}`
    OPTIONS (remote_service_type = 'cloud_ai_translate_v3');
    
    MERGE INTO `{args['dataset_id']}.{args['results_table']}` as me
    USING (
      SELECT
        FARM_FINGERPRINT(text_content) AS text_hash,
        STRING(ml_translate_result.translations[0].detected_language_code) AS lang_orig,
        text_content AS text_orig,
        STRING(ml_translate_result.translations[0].translated_text) AS text_translate,
        ml_translate_status as status,
        current_datetime() AS timestamp
      FROM ML.TRANSLATE(
        MODEL `{args['dataset_id']}.translation_model`,
        (
          SELECT DISTINCT
            text AS text_content
          FROM `{args['dataset_id']}.messages`
          WHERE FARM_FINGERPRINT(text) NOT IN (SELECT text_hash FROM `{args['dataset_id']}.{args['results_table']}`)
            LIMIT 20
        ),
        STRUCT('translate_text' AS translate_mode, 'en' AS target_language_code))
    ) as trans
    ON trans.text_hash = me.text_hash
    WHEN NOT MATCHED BY TARGET
    THEN
        INSERT ROW;
    WHEN MATCHED BY TARGET AND trans.status = ''
    THEN
        UPDATE SET
            me.lang_orig = trans.lang_orig,
            me.text_translate = trans.text_translate,
            me.status = trans.status,
            me.timestamp = trans.timestamp
""".strip()
)

translate_bigquery_task = dts.v1.TransferConfig(
    f"msg-translate-{get_stack()}-trans",
    dts.v1.TransferConfigArgs(
        destination_dataset_id=bq_dataset_id,
        location=bq_dataset_region,
        display_name="Translate messages from messages table",
        data_source_id="scheduled_query",
        params={
            "query": query,
        },
        schedule="every 6 hours" if is_prod_stack() else None,
        service_account_name=service_account_email,
    ),
    opts=ResourceOptions(
        depends_on=[
            translate_connection,
            results_table,
            translate_dts_role,
            transfers_perm,
        ]
    ),
)
