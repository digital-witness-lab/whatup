from PIL import Image
import imagehash
import json
from cloudpathlib import CloudPath, AnyPath
from google.cloud import storage
import click
#import dataset
#from sqlalchemy import types
from google.cloud import bigquery

bucket_dir = "whatup-deploy.messages_test" # can use this in run command 

# Process local or cloud image files or directories
@click.command()
@click.option("--bucket-dir", type=str) # use this to process all unprocessed images in a particular bucket
@click.option(
    "--file-or-dir", type=click.Path(path_type=AnyPath)) # use this argument to process a specific local or cloud directory or image.
def hash_images(bucket_dir, file_or_dir):
    client = bigquery.Client()
    table_id = "{}.phash_images".format(bucket_dir)

    schema = [
        bigquery.SchemaField("filename", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("phash", "BYTES", mode="REQUIRED"),
    ]

    existing_hashes = {}

    if file_or_dir: 
        file_or_dir = AnyPath(file_or_dir)
        images_to_process = []
        if file_or_dir.is_dir():
            media_dirs = list(file_or_dir.rglob("*/media")) 
            #media_dirs = list(file_or_dir.rglob("media/*")) # use this if directly pointing to one media directory
            for obj in media_dirs:
                images_to_process.append(list(AnyPath(obj).rglob("*")))
        else:
            images_to_process.append(file_or_dir)

        QUERY = ('SELECT filename FROM `{}`').format(table_id)
        query_job = client.query(QUERY) 
        rows = query_job.result()  
        existing_hashes = {row[0] for row in list(rows)}

    else:
        QUERY = ('SELECT content_url FROM (SELECT * FROM `{}.media` WHERE REGEXP_CONTAINS(mimetype, \'image/*\')) as a LEFT JOIN `{}.phash_images` as b ON a.filename = b.filename WHERE b.filename IS NULL and content_url IS NOT NULL').format(bucket_dir,bucket_dir)
        query_job = client.query(QUERY) 
        rows = query_job.result()  
        images_to_process = [AnyPath(row[0]) for row in list(rows)]

    i = 0
    new_entries = []
    for file in images_to_process:
        if not file.is_file() or file.name.startswith('.') or file.name in existing_hashes: continue
        try:
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