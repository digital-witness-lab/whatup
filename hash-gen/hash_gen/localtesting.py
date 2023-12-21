'''
This is just for local testing. Cannot run through docker, run as a normal python file. 
'''
from PIL import Image
import imagehash
import json
from cloudpathlib import CloudPath, AnyPath
from google.cloud import storage
from google.cloud.storage import Client, transfer_manager
import click

image_folder = "/Users/aa3576/Desktop/Whatsapp-images-test/"

# Simple example
cloud_object = AnyPath('gs://whatup-message-archive/120363166051808934@g.us/media/0734mfFbmQCsIRppp-YqY5DDCSG-a1VqVuCz2ApzGPs=.jpg')
local_object = AnyPath('/Users/aa3576/Desktop/Whatsapp-images/sim1.jpg')
hash = imagehash.phash(Image.open(local_object.open("rb")))

# this function takes a file or directory, local or gcloud bucket object, hashes it using phash, 
# and then uploads a json file per image to dwl-vertex, our bucket for vertex indexing.
@click.command()
@click.argument(
    "file-or-dir", type=click.Path(path_type=AnyPath)
)
def hash_images(file_or_dir): # can make bucket an argument later 
    file_or_dir = AnyPath(file_or_dir)
    files = []
    hashes = [] 
    storage_client = Client()
    bucket = storage_client.bucket("dwl-vertex")

    if file_or_dir.is_dir(): 
        files.extend(file_or_dir.rglob("*"))
        files = [path for path in files if path.is_file()]
    else:
        files.append(file_or_dir)
    i = 0
    for file in files:
        file = AnyPath(file)
        if not file.name.startswith('.'):
            hash = 1 * imagehash.phash(Image.open(file.open("rb"))).hash.flatten()
            hashes.append(hash)

            blob = bucket.blob(f"{file.stem}.json")
            entry = {"id": file.name, "embedding": hash.tolist()}
            with blob.open("w",encoding='utf8') as fd: 
                fd.write(json.dumps(entry))
        i+= 1
        if i == 100: return
    print(len(hashes))
    print(i)

if __name__ == '__main__':
    hash_images()