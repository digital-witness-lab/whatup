import json

from pulumi_gcp import projects, bigquery
from pulumi import Output, ResourceOptions, get_stack
from pulumi_google_native import bigquerydatatransfer as dts

from config import (
    bq_dataset_region,
    project,
    is_prod_stack,
    translation_enabled,
)
from bigquery import (
    bq_dataset_id,
    data_transfers_service_account,
)


if translation_enabled:
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

    if is_prod_stack():
        query_suffix = """
        AND m.chat_jid IN (
            SELECT
                JID
            FROM `labels.group_labels`
            WHERE label = "dwl-rule:translate"
        )
        """
    else:
        query_suffix = "LIMIT 20"

    query = Output.all(
        dataset_id=bq_dataset_id,
        results_table=results_table.table_id,
        conn_name=translate_connection.name,
        query_suffix=query_suffix,
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
              SELECT
                DISTINCT m.text AS text_content
              FROM
                `{args['dataset_id']}.messages` AS m
              LEFT JOIN `{args['dataset_id']}.{args['results_table']}` AS me
                ON FARM_FINGERPRINT(m.text) = me.text_hash
              WHERE
                m.text IS NOT NULL
                AND (
                    -- we haven't translated this text before
                    (me.text_hash IS NULL AND FARM_FINGERPRINT(m.text) IS NOT NULL)
                    OR
                    -- the last translation didn't succeed
                    (me.status != '')
                )
                AND length(m.text) < 30720 -- api limitation
              {args['query_suffix']}
            ),
            STRUCT('translate_text' AS translate_mode, 'en' AS target_language_code))
        ) as trans
        ON trans.text_hash = me.text_hash
        WHEN NOT MATCHED BY TARGET
        THEN
            INSERT ROW
        WHEN MATCHED AND trans.status = ''
        THEN
            UPDATE SET
                me.lang_orig = trans.lang_orig,
                me.text_translate = trans.text_translate,
                me.status = trans.status,
                me.timestamp = trans.timestamp
        ;
    """.strip()
    )

    translate_bigquery_task = dts.v1.TransferConfig(
        f"msg-translate-{get_stack()}-trans",
        dts.v1.TransferConfigArgs(
            # destination_dataset_id=bq_dataset_id,
            disabled=False,
            location=bq_dataset_region,
            display_name="Translate messages from messages table",
            data_source_id="scheduled_query",
            params={
                "query": query,
            },
            # Run every 3 hours, starting at 00h30... essentially waiting for the
            # postgres transfers to finish
            schedule=(
                "every 3 hours from 00:30 to 00:29"
                if is_prod_stack()
                else None
            ),
            service_account_name=data_transfers_service_account.email,
        ),
        opts=ResourceOptions(
            depends_on=[
                translate_connection,
                results_table,
                translate_dts_role,
            ]
        ),
    )
