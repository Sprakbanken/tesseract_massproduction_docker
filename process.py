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
    output = 'text'

manifest_url = "https://api.nb.no/catalog/v1/iiif/%s/manifest" % (urn)
manifest = requests.get(manifest_url)
manifest_json = manifest.json()

folder_path = os.path.join('/data', urn)

if not os.path.exists(folder_path):
    os.mkdir(folder_path)

for idx,canvas in enumerate(manifest_json["sequences"][0]["canvases"]):
    image_id = canvas["images"][0]["@id"].split('/')[-1]
    image_url = canvas["images"][0]["resource"]["@id"]
    out_path = os.path.join(folder_path, image_id)
    image_url = image_url.replace('/full/full/', '/full/pct:50/')
    print(image_url)
    if output == "alto":
        subprocess.run(["tesseract", image_url, out_path, "-l", model, "--dpi", "400", "-c", "tessedit_create_alto=1", "-c", "preserve_interword_spaces=1"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    elif output == "hocr":
        subprocess.run(["tesseract", image_url, out_path, "-l", model, "--dpi", "400", "-c", "tessedit_create_hocr=1", "-c", "preserve_interword_spaces=1"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    elif output == "page":
        subprocess.run(["tesseract", image_url, out_path, "-l", model, "--dpi", "400", "-c", "tessedit_create_page_xml=1", "-c", "preserve_interword_spaces=1"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    elif output == "pdf":
        subprocess.run(["tesseract", image_url, out_path, "-l", model, "--dpi", "400", "-c", "tessedit_create_pdf=1", "-c", "preserve_interword_spaces=1"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    elif output == "text":
        subprocess.run(["tesseract", image_url, 'stdout', "-l", model, "--dpi", "400"])
    else:
        subprocess.run(["tesseract", image_url, 'stdout', "-l", model, "--dpi", "400"])
