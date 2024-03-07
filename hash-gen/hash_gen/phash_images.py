from PIL import Image
import imagehash
import json
from cloudpathlib import CloudPath, AnyPath
from google.cloud import storage
from cloudpathlib import GSClient
import click
import os
#import dataset
#from sqlalchemy import types
from google.cloud import bigquery
import google.auth

database_url = "whatup-deploy.messages_test" # can use this in run command 

# Process local or cloud image files or directories
@click.command()
@click.option("--database-url", type=str) # use this to process all unprocessed images in a particular bucket
@click.option(
    "--file-or-dir", type=click.Path(path_type=AnyPath)) # use this argument to process an unprocessed specific local or cloud directory or image.
def hash_images(database_url, file_or_dir):
    client = bigquery.Client()
    table_id = f"{database_url}.phash_images"
    creds = google.auth.default()[0] # I have to manually access creds just for CloudPathLib's GSClient instantiation (https://cloudpathlib.drivendata.org/v0.6/authentication/)
    
    gs_client = GSClient(credentials=creds)
    gs_client.set_as_default_client()
    schema = [
        bigquery.SchemaField("filename", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("phash", "BYTES", mode="REQUIRED"),
    ]

    existing_hashes = {}

    if file_or_dir: 
        file_or_dir = AnyPath(file_or_dir)
        images_to_process = []
        if file_or_dir.is_dir():
            images_to_process = list(AnyPath(file_or_dir.rglob("*/media/*"))) 
            #images_to_process = list(AnyPath(file_or_dir.rglob("media/*")))  # use this if directly pointing to one media directory
        else:
            images_to_process.append(file_or_dir)

        QUERY = (f'SELECT filename FROM `{table_id}`')
        query_job = client.query(QUERY) 
        rows = query_job.result()  
        existing_hashes = {row[0] for row in list(rows)}

    else: # the preferable method
        QUERY = (f'SELECT content_url FROM (SELECT * FROM `{database_url}.media` WHERE REGEXP_CONTAINS(mimetype, \'image/*\')) as a LEFT JOIN `{table_id}` as b ON a.filename = b.filename WHERE b.filename IS NULL and content_url IS NOT NULL')
        query_job = client.query(QUERY) 
        rows = query_job.result()  
        images_to_process = [AnyPath(row[0]) for row in list(rows)]

    i = 0
    new_entries = []

    with file.open('rb') as fd:
        with Image.open(fd) as image:
            hash = str(imagehash.phash(image))
    for file in images_to_process:
        if not file.is_file() or file.name.startswith('.') or file.name in existing_hashes: continue
        try:
            with file.open('rb') as fd:
                with Image.open(fd) as image:
                    hash = str(imagehash.phash(image))
            byte_hash = bytes.fromhex(hash)
             
            new_entries.append({"filename": file.name, "phash": byte_hash})
        except:
            print("Skipping a non-image file.")
        
    # if len(new_entries) > 0:
    #     errors = client.insert_rows(table_id, new_entries, schema)
    #     if errors == []: 
    #         i += len(new_entries)
    #         print(f"Added {len(new_entries)} new rows")
    #     else: print(f"Encountered errors while inserting rows: {errors}")

    print(i)

if __name__ == '__main__':
    hash_images()