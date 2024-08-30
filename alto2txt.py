import os
import tarfile
import sys
from lxml import etree as ET
import io

def get_fileseq(mets_xml):
    """Takes a parsed XML document and returns the fileseq"""
    ns = {'MODS': 'http://www.loc.gov/mods/v3', 'METS': 'http://www.loc.gov/METS/'}
    fileSec = mets_xml.find("METS:fileSec", ns)
    if fileSec is not None:
        files = fileSec[0].findall('METS:file', ns)
        for file in files:
            if len(files) == 1:
                seqNumber = 1
            else:
                seqNumber = int(file.get('SEQ'))
            for subfile in file.findall('METS:file', ns):
                if subfile.get('ID').startswith('ALTO_'):
                    url = subfile.find('METS:FLocat[@LOCTYPE="URL"]', ns).get("{http://www.w3.org/1999/xlink}href")
                    url = url.replace('file://ocr/', '')
                    yield (url, seqNumber)

def process_alto(alto_file_content):
    """Hent ut alle ordene i alto-filen, og legg til paragraf og sidenummer."""

    # Delte ord blir lagt i variabelen hyph,
    # teksten i text. Alle ord får et sekvensnummer relativt til boka det står i, samtidig
    # som alle avsnitt blir nummerert fortløpende

    text = []

    # parse XML-fila og få tak i rotelementet root
    root = ET.fromstring(alto_file_content)
    # evt. prøv å åpne som huge tree (for enorme XML-filer, skrudd av her)
    #root = ET.fromstring(alto_file_content, parser=ET.XMLParser(huge_tree=True))

    # Gå gjennom XML-strukturen via TextBlock, som er avsnittselementet

    paras = []

    for paragraph in root.findall(".//{*}TextBlock"):

        # Finn alle ordene i avsnittet, som attributter til elementet String,
        # og sjekk om det foreligger en orddeling -
        # i så fall ligger hele ordet i attributtet SUBS_CONTENT, mens første ledd av orddelingen
        # ligger i CONTENT. Om det ikke er noen orddeling ligger ordet i attributtet CONTENT.
        # Burde fungere også med orddelinger over sideskift

        # Ordet lagres sammen med sekvensnummeret og sekvensnummeret for avsnittet står i,
        # i tillegg til sidenummeret, som kan være greit for oppslag i bokhylla, i forbindelse
        # med generering av konkordanser.

        para = []

        for textline in paragraph.findall(".//{*}TextLine"):
            line = []

            for string in textline.findall(".//{*}String"):
                if 'SUBS_TYPE' in string.attrib:
                    if string.attrib['SUBS_TYPE'] == "HypPart1":
                        token = string.attrib['SUBS_CONTENT']
                        line.append(token)
                else:
                    token = string.attrib['CONTENT']
                    line.append(token)

            para.append(line)

        paras.append(para)
    # returner teksten som en sekvens av tupler, sammen med orddelingene, også som en sekvens av tupler
    return paras

def extract_text_pages(fileStr):
    """Pakk ut tarball fra byte-objekt, parallellisering"""    
    pages = []
    ft = []

    # åpne tar-fil, uten å pakke ut hele
    with tarfile.open(fileobj=fileStr, mode='r') as tar:
        files_in_tar = tar.getmembers()
        # fjern METS fra filliste
        filtered_files_in_tar = [x for x in files_in_tar if not x.name.lower().endswith('-mets.xml')]

        # bruk mets for sortering, fallback til URN hvis denne ikke finnes/kan brukes
        try:
            mets_filename = [x for x in files_in_tar if x.name.lower().endswith('-mets.xml')][0]
            mets_file = tar.getmember(mets_filename)
            f = tar.extractfile(mets_file)
            if f is not None:
                xml = ET.fromstring(f.read())
                for tup in get_fileseq(xml):
                    pages.append(tup)
        except:
            pages = []
            # hent ut sidenummer, ignorer sider uten sidetall
            for file in filtered_files_in_tar:
                try:
                    page_nr = int(file.name.split('.xml')[0].split('_')[-1])
                    pages.append((file, page_nr))
                except:
                    continue

        # sorter altofiler etter sidetall
        for page in sorted(pages, key=lambda x: x[1]):
            filename = page[0]
            page_nr = page[1]

            # extraher fil
            f = tar.extractfile(filename)
            if f is not None:
                content = f.read()
                # parse innhold i alto-fil, returner tekst, sekvensnumre og orddelinger
                try:
                    paras = process_alto(content)
                except:
                    print("XML error, reading", filename.name, "skippping")
                    continue

                with open('out/' + filename.name.replace(".xml", ".txt"), 'a') as f:
                    for para in paras:
                        for line in para:
                            f.write(' '.join(line) + "\n")
                        f.write("\n")
  

def main():
    file = sys.argv[1]
    with open(file, 'rb') as f:
        fileStr = io.BytesIO(f.read())
        extract_text_pages(fileStr)

if __name__ == "__main__":
    main()