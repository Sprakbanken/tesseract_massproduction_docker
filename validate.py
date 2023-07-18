from lxml import etree as ET
from collections import Counter
import sys

def tokenize(text):
    # simple whitespace tokenizer
    return text.split()

def process_alto(alto_file):
    text = []
    root = ET.parse(alto_file)
    # extract text from ALTO
    for paragraph in root.findall(".//{*}TextBlock"):
        for string in paragraph.findall(".//{*}String"):
            if 'SUBS_TYPE' in string.attrib:
                if string.attrib['SUBS_TYPE'] == "HypPart1":
                    tokens = tokenize(string.attrib['SUBS_CONTENT'])
                    for token in tokens:
                        text.append(token)
            else:
                tokens = tokenize(string.attrib['CONTENT'])
                for token in tokens:
                    text.append(token)
    return text

text = []

for line in sys.stdin:
    try:
        file_text = process_alto(line.strip())
    except:
        continue
    # open ALTO file
    if file_text != None:
        text.extend(file_text)

# count and sort
x = Counter(text)
x = {k: v for k, v in sorted(x.items(), key=lambda item: item[1], reverse=True)}

for item in x.items():
    print(item[0], item[1])
