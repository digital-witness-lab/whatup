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
    if file_or_dir.is_dir():
        files.extend(file_or_dir.glob("*"))
    else:
        files.append(file_or_dir)
    for file in files:
        file = AnyPath(file)
        if not file.name.startswith('.'):
            hash = imagehash.phash(Image.open(file.open("rb")))
            hashes.append(hash.hash)
            hash_file : AnyPath = f"{file.name}.json"
            entry = {"id": file.name, "embedding": hash.hash}
            with hash_file.open("w") as fd:
                fd.write(entry)

    print(hashes)