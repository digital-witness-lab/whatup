import base64

import click
from cloudpathlib import AnyPath
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from .phash_images import (
    process_tasks,
    filter_task_path,
    BIGQUERY_SCHEMA,
    ImageTask,
    hash_image,
)

DEFAULT_HASH_TABLE = "phash_images"


@click.group()
def cli():
    pass


# Process local or cloud image files or directories
@cli.command("bulk-to-bigquery")
@click.option("--dataset-id", type=str)
@click.option(
    "--hash-table",
    type=str,
    default=DEFAULT_HASH_TABLE,
    help="Bigquery table name where to output image hashes",
)
@click.option(
    "--media-table",
    type=str,
    default="media",
    help="Table name of existing media data to read from",
)
@click.option("--image", "images", type=click.Path(path_type=AnyPath), multiple=True)
@click.option("--dir", "directories", type=click.Path(path_type=AnyPath), multiple=True)
@click.option(
    "--job-idx", default=0, type=int, help="If running in parallel, which job is this"
)
@click.option(
    "--job-count",
    type=int,
    default=0,
    help="If running in parallel, how many jobs are being run",
)
def bulk_to_bigquery(
    dataset_id, hash_table, media_table, images, directories, job_idx, job_count
):
    client = bigquery.Client()
    hash_table_id = f"{dataset_id}.{hash_table}"
    tasks = []

    if images:
        for image in images:
            if filter_task_path(image, job_idx, job_count):
                tasks.append(ImageTask(image.name, image))

    if directories:
        for directory in directories:
            tasks.extend(
                ImageTask(image.name, image)
                for image in directory.rglob("*/media/*")
                if image.is_file() and filter_task_path(image, job_idx, job_count)
            )

    if media_table:
        media_table_id = f"{dataset_id}.{media_table}"
        try:
            client.get_table(
                hash_table_id
            )  # will raise NotFound if hash table doesn't exist
            query = f"""
            SELECT
                media_table.filename, media_table.content_url
            FROM `{media_table_id}` as media_table
            LEFT JOIN `{hash_table_id}` as hash_table
                ON media_table.filename = hash_table.filename
            WHERE
                REGEXP_CONTAINS(media_table.mimetype, 'image/*') AND
                hash_table.filename IS NULL AND  -- this selects items not in the hash table
                content_url IS NOT NULL
            """
        except NotFound:
            client.create_table(bigquery.Table(hash_table_id, schema=BIGQUERY_SCHEMA))
            query = f"""
            SELECT
                media_table.filename, media_table.content_url
            FROM `{media_table_id}` as media_table
            WHERE
                REGEXP_CONTAINS(media_table.mimetype, 'image/*') AND
                content_url IS NOT NULL
            """
        if job_count:
            query = f"""
            {query} AND
            MOD(FARM_FINGERPRINT(media_table.filename), {job_count}) = {job_idx}
            """
        query_job = client.query(query)
        rows = query_job.result()
        tasks.extend(ImageTask(row[0], AnyPath(row[1])) for row in rows)

    print(f"Found {len(tasks)} tasks to work on")
    process_tasks(tasks, client, hash_table_id)


@cli.command("query-image")
@click.option("--dataset-id", type=str)
@click.option(
    "--hash-table",
    type=str,
    default=DEFAULT_HASH_TABLE,
    help="Bigquery table name where to output image hashes",
)
@click.option(
    "--media-table",
    type=str,
    default="media",
    help="Table name of existing media data to read from",
)
@click.option("--threshold", type=float, default=0.01)
@click.argument("image", type=click.Path(path_type=AnyPath))
def query_image(dataset_id, hash_table, media_table, image, threshold):
    client = bigquery.Client()

    image_hash = hash_image(image)
    image_hash_b64 = base64.standard_b64encode(image_hash).decode("utf8")

    hash_table_id = f"{dataset_id}.{hash_table}"
    media_table_id = f"{dataset_id}.{media_table}"
    query = f"""
    SELECT d.* FROM (
        SELECT 
            BIT_COUNT(hash_table.phash ^ FROM_BASE64(@image_hash_b64)) / (8 * BYTE_LENGTH(hash_table.phash)) AS distance,
            hash_table.filename AS filename,
            media_table.content_url AS content_url
        FROM `{hash_table_id}` AS hash_table
        JOIN `{media_table_id}` AS media_table
            ON hash_table.filename = media_table.filename
    ) AS d
    WHERE distance < @threshold
    ORDER BY d.distance
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("image_hash_b64", "STRING", image_hash_b64),
            bigquery.ScalarQueryParameter("threshold", "FLOAT64", threshold),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    for row in query_job.result():
        print(f"[{row.distance}] {row.content_url}")


if __name__ == "__main__":
    cli()
