import re
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import streamlit as st

def process_xml(input_file_name):
    
    try:
        tree = ET.parse(input_file_name)
        root = tree.getroot()
        xml_content = ET.tostring(root, encoding='unicode', method='xml')
    except:
        xml_content = "YOU DID NOT UPLOAD AN XML FILE!! TRY AGAIN!!"
    
    return xml_content

def verify_prerequisite(input_xml, output_xml):
    message = ""
    if not input_xml:
        message = "Upload input XML"
        if not output_xml:
            message += " & upload output XML"
    elif not output_xml:
        message = "Upload output XML"
    return  message

def copy_text(data):
    return data

def list_elements(xml_text):
    elements = []
    elements_dict = {}
    pattern = re.compile(r"<[^/].*>")
    for i, line in enumerate(xml_text.split("\n")):
        search = pattern.search(line)
        if search:
            element = pattern.findall(line)[0]
            element = re.search(r"<([^>]*)>", element)
            element = element.group(1)
            elements.append(element)
            elements_dict[element] = [i]
    
    return elements

def chunk_xml_by_tags(xml_text, nodes_to_select):
    # Parse the XML content
    root = ET.fromstring(xml_text)
    # st.info(nodes_to_select)
    # Function to extract XML content for a given tag
    def extract_content_for_tag(root, tag):
        elements = root.findall(f".//{tag}")
        extracted_content = []
        for elem in elements:
            extracted_content.append(ET.tostring(elem, encoding='unicode', method='xml'))
        return extracted_content
    
    # Extract content for each specified node
    chunks = {}
    if nodes_to_select:
        for tag in nodes_to_select:
            chunks[tag] = extract_content_for_tag(root, tag)
    return chunks


if __name__ == "__main__":
    with open("/Users/nlepakshi/Documents/GitHub/genie/genie_core/config/test_data/LATAM/OVRS_Singapore_Airlines_18_1.xml", "r") as file:
        xml_text = file.read() 
    
    nodes_to_select = ["BaggageAllowanceList", "ContactInfoList"]
    
    chunks = chunk_xml_by_tags(xml_text, nodes_to_select)
    
    print(chunks)