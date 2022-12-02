# Tesseract docker images for use in mass production

This repository contains instructions for building and using a Tesseract system in mass production (operationalizing the instructions at: https://tesseract-ocr.github.io/tessdoc/Compiling-%E2%80%93-GitInstallation.html#release-builds-for-mass-production). Essentially, this forces Tesseract to use single-threading on image-level, parallelizing over images. The system is used in the DHLAB at the National Library of Norway.

## Build docker image

```bash
docker build -t tesseract_massproduction .
```

## Test run
```bash
docker run --rm tesseract_massproduction tesseract
```

# Example pipeline for local files, using GNU Parallel (returning HOCR)
```bash
find * -type f -name "*.tif" | parallel -j 5 "echo {} && docker run -v /path/to/models:/usr/local/share/tessdata -v /path/to/data:/data --rm tesseract_massproduction tesseract /data/{} /data/{} -c tessedit_create_hocr=1 -c hocr_font_info=0 -l eng"
```
# Example pipeline for IIIF (returning ALTO XML)

## Run tesseract on a specific URN

```bash
docker run -it -v /data/ocr/models/:/usr/local/share/tessdata -v /data/ocr/data:/data tesseract_massproduction python3 process.py URN MODELNAME alto"
```

## Create folders for each URN (expects one folder with all pages in a flat structure)
```bash
python create_folders.py INPUT_FOLDER OUTPUT_FOLDER
```

## Transform each object (pixel to mm, de-hyphenation etc.)
```bash
cd OUTPUT_FOLDER
find * -type d | parallel -j 10 -u python ../create_nb_alto.py {}
```

## Make tarballs of each object
```bash
find * -type d -name "*_transformed" | parallel -j10 -u "cd {} && tar cf ../{=s/_transformed// =}_ocr_xml.tar *"
```
