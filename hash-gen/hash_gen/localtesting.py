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
#local_object = AnyPath('/Users/aa3576/Desktop/Whatsapp-images/sim1.jpg')
#hash = imagehash.phash(Image.open(local_object.open("rb")))

# this function takes a file or directory, local or gcloud bucket object, hashes it using phash, 
# and then uploads a json file per image to dwl-vertex, our bucket for vertex indexing.
@click.command()
@click.argument(
    "file-or-dir", type=click.Path(path_type=AnyPath)
)
def hash_images(file_or_dir): # can make bucket/local an argument later 
    file_or_dir = AnyPath(file_or_dir)
    files = []
    hashes = [] 
    storage_client = Client()
    bucket = storage_client.bucket("dwl-vertex")

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
            blob = bucket.blob(f"{file.stem}.json")
            if blob.exists(): continue
            
            hash = 1 * imagehash.phash(Image.open(file.open("rb"))).hash.flatten()
            hashes.append(hash)
            entry = {"id": file.name, "embedding": hash.tolist()}

            with blob.open("w",encoding='utf8') as fd: 
                fd.write(json.dumps(entry))

            # write to local folder for testing
            # hash_file = AnyPath("/Users/aa3576/Desktop/Whatsapp-images-jsons/" + f"{file.stem}.json")
            # entry = {"id": file.name, "embedding": hash.tolist()}
            # with hash_file.open("w",encoding='utf8') as fd:
            #     fd.write(json.dumps(entry))

            i+= 1
            if i == 5: return
        except:
            print("Skipping a non-image file.")
    print(len(hashes))
    print(i)

if __name__ == '__main__':
    hash_images()