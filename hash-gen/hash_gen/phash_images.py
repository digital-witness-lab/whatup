from PIL import Image
import imagehash
import json
from cloudpathlib import CloudPath, AnyPath
from google.cloud import storage
import click

# Process image files or directories
@click.command()
@click.argument(
    "file-or-dir", type=click.Path(path_type=AnyPath)
)
def hash_images(file_or_dir):
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
            entry = {"id": file.name, "embedding": hash.tolist()} # UPDATE TO DB ENTRY

            # INSERT IN DB

            i+= 1
            if i == 5: return
        except:
            print("Skipping a non-image file.")

    print(len(hashes))
    print(i)