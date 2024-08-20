# Tesseract docker images for use in mass production

This repository contains instructions for building and using a Tesseract system in mass production (operationalizing the instructions at: https://tesseract-ocr.github.io/tessdoc/Compiling-%E2%80%93-GitInstallation.html#release-builds-for-mass-production). Essentially, this forces Tesseract to use single-threading on image-level, parallelizing over images. The system is used in the DHLAB at the National Library of Norway.

## Build docker image

```bash
docker build -t tesseract_massproduction .
```

## Test run
```bash
docker run --rm tesseract_massproduction tesseract --list-langs
```

# Example pipeline for IIIF (returning ALTO XML) - modify your paths accordingly

## 1. Run tesseract on a specific URN

```bash
docker run -it -v $PWD/data:/data tesseract_massproduction sh -c "python3 process.py URN:NBN:no-nb_digibok_2018080126011 nor-frak alto"
```

## 2. Do a quick evaluation using word frequency lists

```bash
docker run -it -v $PWD/data:/data tesseract_massproduction sh -c "find /data -type f | python3 validate.py | head"
```

## 3. Transform each object (pixel to mm, de-hyphenation etc.)
```bash
find data -mindepth 1 -type d -printf "%f\n" | parallel -u -j 5 "docker run -i -v $PWD/data:/data tesseract_massproduction python3 transform_alto.py /data/{}"
```

## 4. Make tarballs of each object
```bash
cd data
find * -type d -name "*_transformed" | parallel -j10 -u "cd {} && tar cf ../{=s/_transformed// =}_ocr_xml.tar *"
```

# Example pipeline for local files, using GNU Parallel (returning HOCR)
```bash
find * -type f -name "*.tif" | parallel -j 5 "echo {} && docker run -v -v $PWD/data:/data --rm tesseract_massproduction tesseract /data/{} /data/{} -c tessedit_create_hocr=1 -c hocr_font_info=0 -l eng"
```
