'''
This is just for local testing. Cannot run through docker, run as a normal python file. 
'''

from PIL import Image
import imagehash
import json
from cloudpathlib import CloudPath, AnyPath
from google.cloud import storage
import click

image_folder = "/Users/aa3576/Desktop/Whatsapp-images-test/"

# Simple example
cloud_object = AnyPath('gs://whatup-message-archive/120363166051808934@g.us/media/0734mfFbmQCsIRppp-YqY5DDCSG-a1VqVuCz2ApzGPs=.jpg')
local_object = AnyPath('/Users/aa3576/Desktop/Whatsapp-images/sim1.jpg')
hash = imagehash.phash(Image.open(local_object.open("rb")))

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
            hash_file = AnyPath("/Users/aa3576/Desktop/Whatsapp-images/" + f"{file.name}.json")
            entry = {"id": file.name, "embedding": str(hash)}
            with hash_file.open("w") as fd:
                fd.write(json.dumps(entry))

    print(hashes)

if __name__ == '__main__':
    hash_images()

# [int(ch) for ch in str(hash).split()] 