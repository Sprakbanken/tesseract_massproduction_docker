from lxml import etree
import re
import os
import requests
import sys

input_folder = sys.argv[1]

try:
    factor = int(sys.argv[2])
except:
    factor = 1

def insert_styles(input_path, output_path):
    tree = etree.parse(input_path)
    root = tree.getroot()
    # lag style-element
    elem = etree.Element("Styles")
    se1 = etree.SubElement(elem, 'TextStyle', attrib={"ID": "TXT_0", "FONTSIZE": "32", "FONTFAMILY": "Times Roman"})
    se2 = etree.SubElement(elem, 'ParagraphStyle', attrib={"ID": "PAR_BLOCK", "ALIGN": "Block"})
    
    for item in root.iter():
        t = item.tag.split("}")[1][0:]
        if t == 'String':
            item.set('STYLEREFS', 'TXT_0')
        if t == 'TextBlock':
            item.set('STYLEREFS', 'TXT_0 PAR_BLOCK')
            
    root.insert(1, elem)
    
    tree.write(output_path, xml_declaration=True, encoding='UTF-8')

def pix2mm(pix):
    return int((pix*254)//400)

def get_iiif_images(urn):
    manifest_url = "https://api.nb.no/catalog/v1/iiif/%s/manifest" % (urn)
    manifest = requests.get(manifest_url)
    manifest_json = manifest.json()
    rows = []

    for idx,canvas in enumerate(manifest_json["sequences"][0]["canvases"]):
        image_id = canvas["images"][0]["@id"].split('/')[-1]
        image_url = canvas["images"][0]["resource"]["@id"]
        rows.append([image_id, image_url])
    return rows

def create_filesec(urn, output_folder):
    images = get_iiif_images(urn)
    
    basexml = """<?xml version="1.0"?>
            <mets xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.loc.gov/METS/" xsi:schemaLocation="http://www.loc.gov/METS/ http://schema.ccs-gmbh.com/metae/mets-metae.xsd" xmlns:MODS="http://www.loc.gov/mods/v3" xmlns:mix="http://www.loc.gov/mix/" xmlns:xlink="http://www.w3.org/1999/xlink" TYPE="METAe_Monograph" LABEL="">
            <fileSec>
            <fileGrp ID="IMGGRP" USE="Images">
            </fileGrp>
            </fileSec>
            </mets>
            """
    
    tree = etree.fromstring(basexml)
    
    filegrp = tree.find(".//{*}fileGrp")
    
    for idx,image in enumerate(images):
        image_index = "IMG" + str(idx+1).zfill(5)
        file = etree.Element("file", attrib={"ID": image_index})
        flocat = etree.Element("Flocat", attrib={"LOCTYPE": "URL", "{http://www.w3.org/1999/xlink}href": image[1]})
        
        filepath = os.path.join(output_folder, image[0] + ".xml")
        
        if not os.path.exists(filepath):
            print("WARNING: file does not exist (but will still be listed)", filepath)
            pass
        
        file.append(flocat)
        filegrp.append(file)
    
    with open(os.path.join(output_folder, urn + "-mets.xml"), 'w') as f:
        f.write(etree.tostring(tree, encoding="UTF-8").decode("UTF-8"))

def convert_xml(input_path, output_path):
    tree = etree.parse(input_path)
    
    # set measurement unit
    elem_measurement = tree.find(".//{*}MeasurementUnit")
    elem_measurement.text = 'mm10'
    
    # convert attributes to mm
    attrib_names = ["BASELINE", "HEIGHT", "WIDTH", "VPOS", "HPOS"]
    for elem in tree.iter():
        attribs = elem.attrib
        for attrib_name in attrib_names:
            if attrib_name in attribs:
                value = int(attribs[attrib_name])
                if attrib_name in ["HPOS", "VPOS"]:
                    if value <= 0:
                        value = '0'
                    else:
                        value = str(abs(pix2mm(value)) * factor)
                else:
                    value = str(abs(pix2mm(value)) * factor)
                attribs[attrib_name] = value
    
    # "de-hyphenation"
    lines = tree.findall(".//{*}TextLine")
    line_split = False

    for idx,line in enumerate(lines):
        strings = line.findall(".//{*}String")
        words = [x.attrib.get("CONTENT") for x in strings]

        if line_split == True:
            fullword = firstpart + words[0]
            strings[0].attrib["SUBS_TYPE"] = "HypPart2"
            strings[0].attrib["SUBS_CONTENT"] = fullword
            strings_previous_line[-1].attrib["SUBS_CONTENT"] = fullword
            
            line_split = False
            strings_previous_line = []

        if words[-1].endswith("-") and words[-1] != "-" and idx+1 != len(lines):
            # check position (hyphen = 5 mm), if previous element is shorter, do not hyphenate
            try:
                previous_width = int(strings[-1].attrib["WIDTH"])
            except:
                continue

            if previous_width > 5:
                hyphen_width = 5
            else:
                continue
        
        # remove hyphen from content
            firstpart = words[-1][:-1]
            
            strings[-1].attrib["SUBS_TYPE"] = "HypPart1"
            strings[-1].attrib["CONTENT"] = firstpart            
            
            strings_previous_line = strings.copy()
            line_split = True
            
            # insert HYP element
            hyp = etree.Element("{http://www.loc.gov/standards/alto/ns-v3#}HYP")
            hyp.attrib["CONTENT"] = '-'

            strings[-1].attrib["WIDTH"] = str(int(strings[-1].attrib["WIDTH"]) - hyphen_width)
            hyp.attrib["HPOS"] = str(int(strings[-1].attrib["HPOS"]) + int(strings[-1].attrib["WIDTH"]))
            hyp.attrib["VPOS"] = strings[-1].attrib["VPOS"]
            hyp.attrib["WIDTH"] = str(hyphen_width)
            
            strings[-1].addnext(hyp)
    
    with open(output_path, 'w') as f: 
        f.write(etree.tostring(tree, pretty_print = True, encoding="UTF-8").decode("UTF-8"))

# RUN SCRIPT
if not input_folder.endswith("_transformed"):
    print(input_folder)
    output_folder = input_folder + '_transformed'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        try:
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file)
            insert_styles(input_path=input_path, output_path=output_path)
            convert_xml(input_path=output_path, output_path=output_path)
        except etree.XMLSyntaxError:
            print("XML-feil, tom fil, hopper over", input_path)
        continue

    urn = os.path.basename(input_folder)
    create_filesec(urn=urn, output_folder=output_folder)
