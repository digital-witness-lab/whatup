from PIL import Image
import imagehash
from cloudpathlib import CloudPath, AnyPath
from google.cloud import storage
import click

image_folder = "/Users/aa3576/Desktop/Whatsapp-images-test/"

# Simple example
cloud_object = AnyPath('gs://whatup-message-archive/120363166051808934@g.us/media/0734mfFbmQCsIRppp-YqY5DDCSG-a1VqVuCz2ApzGPs=.jpg')
local_object = AnyPath('/Users/aa3576/Desktop/Whatsapp-images/sim1.jpg')
hash = imagehash.phash(Image.open(local_object.open("rb")))

# Process image files or directories
link_images = AnyPath('gs://whatup-message-archive/120363166051808934@g.us/media/')
files = []
hashes = [] 
if link_images.is_dir():
    files.extend(link_images.glob("*"))
else:
    files.append(link_images)
for file in files:
    file = AnyPath(file)
    if not file.name.startswith('.'):
        hash = imagehash.phash(Image.open(file.open("rb")))
        hashes.append(str(hash))

print(hashes)


@click.command()
@click.argument(
    "file-or-dir", type=click.Path(path_type=AnyPath), nargs=-1
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
            hashes.append(str(hash))

    print(hashes)

if __name__ == '__main__':
    hash_images()

# something is wrong with above