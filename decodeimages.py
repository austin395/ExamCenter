import json
import zlib

with open('images.json', 'r') as imagefile:
    images = json.load(imagefile)

imagez = images['cyber.jpg'].decode('base64')
image = zlib.decompress(imagez)

fh = open("./templates/images/cyber.jpg", "wb")
fh.write(image)
fh.close()