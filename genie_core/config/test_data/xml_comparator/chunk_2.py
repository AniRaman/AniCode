import streamlit as st
import os
import sys
import re

# Add project directories to the system path

with open("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/xml_comparator/ovrs1.xml","r") as f:
    data = f.read()

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

elements = list_elements(data)
print(elements)