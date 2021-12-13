# Build

```bash
docker build -t tesseract_massproduction .
```

# Test run
```bash
docker run --rm tesseract_massproduction tesseract
```

# Example pipeline using GNU Parallel
```bash
find * -type f -name "*.tif" | parallel -j 5 "echo {} && docker run -v /path/to/models:/usr/local/share/tessdata -v /path/to/data:/data --rm tesseract_massproduction tesseract /data/{} /data/{} -c tessedit_create_hocr=1 -c hocr_font_info=0 -l eng"
```
