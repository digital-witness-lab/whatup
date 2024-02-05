from PIL import Image
import imagehash
import json
from cloudpathlib import CloudPath, AnyPath
from google.cloud import storage
import click
#import dataset
#from sqlalchemy import types
from google.cloud import bigquery


cloud_object = AnyPath('gs://whatup-message-archive') # Can use this as argument for hash_images. 

# Process local or cloud image files or directories
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

    # table = bigquery.Table(table_id, schema=schema)
    # table = client.create_table(table) 

    file_or_dir = AnyPath(file_or_dir)
    files = {}

    if file_or_dir.is_dir():
        print("start")
        media_dirs = list(file_or_dir.rglob("*/media")) # takes ~ 30 secs - 1 min locally given 36 media dirs as of 2.5.24
        #media_dirs = list(file_or_dir.rglob("media")) # use this if directly pointing to one media directory
        for obj in media_dirs:
            files[obj] = list(AnyPath(obj).rglob("*"))
    else:
        files[file_or_dir] = [file_or_dir]
    i = 0
    # run through every key and its list of files. This took ~45 mins.
    for media_dir in files:
        new_entries = []
        for file in files[media_dir]:
            if not file.is_file() or file.name.startswith('.'): continue
            file = AnyPath(file)

            try:
                QUERY = ('SELECT filename FROM `{}` WHERE filename = "{}"').format(table_id, file.name)
                query_job = client.query(QUERY) 
                rows = query_job.result()  
                if rows.total_rows > 0: break # hash already exists

                hash = str(imagehash.phash(Image.open(file.open("rb"))))
                byte_hash = bytes.fromhex(hash)

                new_entries.append({"filename": file.name, "phash": byte_hash})
            except:
                print("Skipping a non-image file.")
        if len(new_entries) > 0:
            errors = client.insert_rows(table_id, new_entries, schema)
            if errors == []: 
                i += len(new_entries)
                print("Added {} new rows".format(len(new_entries)))
            else: print("Encountered errors while inserting rows: {}".format(errors))
        
    print(i)

if __name__ == '__main__':
    hash_images()