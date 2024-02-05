from PIL import Image
import imagehash
import json
from cloudpathlib import CloudPath, AnyPath
from google.cloud import storage
import click
#import dataset
#from sqlalchemy import types
from google.cloud import bigquery

# Process image files or directories
@click.command()
@click.argument(
    "file-or-dir", type=click.Path(path_type=AnyPath)
)
def hash_images(file_or_dir):
    client = bigquery.Client()
    table_id = "whatup-deploy.messages_test.phash_images"

    schema = [
        bigquery.SchemaField("filename", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("phash", "BYTES", mode="REQUIRED"),
    ]

    file_or_dir = AnyPath(file_or_dir)
    files = []
    hashes = [] 

    if file_or_dir.is_dir(): # are local directory structures going to mirror the bucket? 
        media_dirs = list(file_or_dir.rglob("*/media"))
        for obj in media_dirs:
            files.extend(AnyPath(obj).rglob("*"))
        files = [path for path in files if path.is_file() and not path.name.startswith('.')]
    else:
        files.append(file_or_dir)
    i = 0
    for file in files:
        file = AnyPath(file)

        try:
            QUERY = ('SELECT filename FROM `{}` WHERE filename = "{}" ').format(table_id, file.name)
            query_job = client.query(QUERY) 
            rows = query_job.result()  
            if rows.total_rows > 0: break # hash already exists

            hash = str(imagehash.phash(Image.open(file.open("rb"))))
            byte_hash = bytes.fromhex(hash)

            entry = [{"filename": file.name, "phash": byte_hash}]
            errors = client.insert_rows(table_id, entry, schema)
            if errors == []:
                i+= 1
            else:
                print("Encountered errors while inserting rows: {}".format(errors))
        except:
            print("Skipping a non-image file.")

    print(len(hashes))
    print(i)

if __name__ == '__main__':
    hash_images()