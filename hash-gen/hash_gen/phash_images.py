from PIL import Image
from pathlib import Path
from itertools import islice
from dataclasses import dataclass
import typing as T

import imagehash
import click
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from cloudpathlib import AnyPath, CloudPath


BIGQUERY_SCHEMA = [
    bigquery.SchemaField("filename", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("phash", "BYTES", mode="REQUIRED"),
]


@dataclass
class ImageTask:
    filename: str
    path: CloudPath | Path

    def __str__(self):
        return f"<ImageTask {self.filename}@{self.path}>"


def batched(iterable, n):
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def process_images(tasks: T.Sequence[ImageTask]):
    for task in tasks:
        try:
            with task.path.open("rb") as fd:
                with Image.open(fd) as image:
                    hash = str(imagehash.phash(image))
            byte_hash = bytes.fromhex(hash)
            yield {"filename": task.filename, "phash": byte_hash}
        except Exception as e:
            print(f"Skipping a non-image file: {task}: {e}")


def filter_task_path(path: CloudPath | Path, job_idx: int, job_count: int) -> bool:
    return job_count <= 1 or hash(path.name) % job_count == job_idx


def process_tasks(tasks, client, hash_table_id):
    i = 0
    entries = process_images(tasks)
    for entries_batch in batched(entries, 1_000):
        errors = client.insert_rows(hash_table_id, entries_batch, BIGQUERY_SCHEMA)
        if not errors:
            i += len(entries_batch)
            print(f"Added {len(entries_batch)} new rows")
        else:
            print(f"Encountered errors while inserting rows: {errors}")


# Process local or cloud image files or directories
@click.command()
@click.option("--dataset-id", type=str)
@click.option(
    "--hash-table",
    type=str,
    default="phash_images",
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
@click.option("--job-idx", type=int, help="If running in parallel, which job is this")
@click.option(
    "--job-count",
    type=int,
    default=0,
    help="If running in parallel, how many jobs are being run",
)
def hash_images(
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


if __name__ == "__main__":
    hash_images()
