from PIL import Image
import imagehash
import json
from cloudpathlib import CloudPath, AnyPath
from google.cloud import storage
import click
import dataset
from sqlalchemy import types

def db_setup(database_url):
    print(database_url)
    db: dataset.Database = dataset.connect(database_url)
    phash_table = db.create_table(
        "phash_images",
        primary_id="filename",
        primary_type=db.types.text,
        primary_increment=False
    )
    phash_table.create_column('phash', types.ARRAY(db.types.integer))
    return db

# Process image files or directories
@click.command()
@click.option("--database-url", type=str)
@click.argument(
    "file-or-dir", type=click.Path(path_type=AnyPath)
)
def hash_images(file_or_dir, database_url):
    db = db_setup(database_url)

    file_or_dir = AnyPath(file_or_dir)
    files = []
    hashes = [] 

    # below block could maybe be more efficient? i think this is the block that takes a while. 
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
            #blob = bucket.blob(f"{file.stem}.json")
            #if blob.exists(): continue
            
            hash = 1 * imagehash.phash(Image.open(file.open("rb"))).hash.flatten()
            hashes.append(hash)
            entry = {"filename": file.name, "phash": hash.tolist()}
            
            db["phash_images"].insert(entry)
            i+= 1
            if i == 5: return
        except:
            print("Skipping a non-image file.")

    print(len(hashes))
    print(i)