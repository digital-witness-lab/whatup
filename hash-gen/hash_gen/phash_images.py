from PIL import Image
from pathlib import Path
from itertools import islice
from dataclasses import dataclass
import typing as T

import imagehash
from cloudpathlib import CloudPath
from google.cloud import bigquery


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


def hash_image(image_path: CloudPath | Path) -> bytes:
    with image_path.open("rb") as fd:
        with Image.open(fd) as image:
            image_hash = str(imagehash.phash(image))
    return bytes.fromhex(image_hash)


def process_images(tasks: T.Sequence[ImageTask]):
    for task in tasks:
        try:
            byte_hash = hash_image(task.path)
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
