import json
import base64
import zlib


with open("./templates/images/cyber.jpg", "rb") as imageFile:
    imz = str(zlib.compress(imageFile.read()))
    im = base64.b64encode(imz)
    print len(im)

images = {'cyber.jpg': im}

with open('images.json', 'w') as outfile:
    json.dump(images, outfile)
