import requests
import subprocess
import os
import sys

urn = sys.argv[1]

try:
    model = sys.argv[2]
except:
    model = 'nor-frak'

try:
    output = sys.argv[3]
except:
    output = 'alto'

manifest_url = "https://api.nb.no/catalog/v1/iiif/%s/manifest" % (urn)
manifest = requests.get(manifest_url)
manifest_json = manifest.json()

if manifest_json["license"] in ["https://www.nb.no/lisens/publicdomain", "https://www.nb.no/lisens/stromming"]:
    for idx,canvas in enumerate(manifest_json["sequences"][0]["canvases"]):
        image_id = canvas["images"][0]["@id"].split('/')[-1]
        image_url = canvas["images"][0]["resource"]["@id"]
        out_path = os.path.join('/data/', image_id)
        image_url = image_url.replace('/full/full/', '/full/pct:50/')
        print(image_url)
        if output == "alto":
            subprocess.run(["tesseract", image_url, out_path, "-l", model, "--dpi", "400", "-c", "tessedit_create_alto=1", "-c", "preserve_interword_spaces=1"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        else:
            subprocess.run(["tesseract", image_url, 'stdout', "-l", model, "--dpi", "400"])
else:
    print("%s not in the public domain, pipeline will not work." % (urn))
