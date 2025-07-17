import streamlit as st
import os
import sys
import pandas as pd
import difflib
import re
from lxml import etree
import html2text
from bs4 import BeautifulSoup
from io import StringIO
from llama_index.core import Document
import html
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
from genie_core.common.confluence_utils import *

def convert_html_to_markdown(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    markdown_content = h.handle(html_content)
    return markdown_content

def inject_custom_css():
    st.markdown("""
        <style>
        .stDownloadButton button {
            background-color: #007bff;
            color: white;
        }
        .diff_add { background-color: #ccffcc; }  /* Green background for additions */
        .diff_sub { background-color: #ffcccc; }  /* Red background for deletions */
        table { width: 100%; }                    /* Full width table */
        td { padding: 8px; border: 1px solid #ddd; } /* Table cell styling */
        </style>
        """, unsafe_allow_html=True)

inject_custom_css()


# with st.sidebar:
#     st.header("Upload Files")
#     source_xml_file = st.text_input("Specifications URL")

#     def extract_space_and_page_name(url):
#         try:
#             parts = url.split('/')
#             space_index = parts.index('spaces') + 1
#             space = parts[space_index]
#             page_name = parts[-1]
#             return space, page_name
#         except (ValueError, IndexError):
#             return None, None

#     if source_xml_file:
#         space, page_name = extract_space_and_page_name(source_xml_file)
#         page_name = page_name.replace("+", " ")
#         if space and page_name:
#             st.write(f"Space: {space}, Page Name: {page_name}")
#         else:
#             st.error("Invalid URL format")

# output_placeholder_html = st.empty()
# output_placeholder_md = st.empty()

# if source_xml_file:
#     html_content = get_body(space, page_name)
#     if html_content:
#         html_content = html_content.replace('<', '&lt;').replace('>', '&gt;')
#         html_content = f"<pre>{html_content}</pre>"
#         height = min(800, len(html_content) * 30)
#         output_placeholder_html.markdown(html_content, unsafe_allow_html=True)
#     else:
#         st.info("Please upload a valid URL.")

# else:
#     st.info("Please upload a valid URL.")

def extract_space_and_page_name(url):
    try:
        parts = url.split('/')
        space_index = parts.index('spaces') + 1
        space = parts[space_index]
        page_name = parts[-1]
        return space, page_name
    except (ValueError, IndexError):
        return None, None
    
def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def display_generated_xslt():
    st.title("Generated XSLT")
    output_placeholder = st.empty()
    updated_xslt = st.session_state.updated_xslt
    if updated_xslt:
        height = min(400, len(updated_xslt) * 30)
        output_placeholder.text_area("", updated_xslt, height)
        st.download_button(label="Download XSLT", data=updated_xslt, file_name="updated_xslt.xslt", mime="application/xslt")
    else:
        height = min(100, 200)
        output_placeholder.markdown(f"<div style='border: 1px solid #3c3c73; padding: 10px; height: {height}px; overflow-y: auto;'>XSLT will appear here</div>", unsafe_allow_html=True)

def display_generated_specs():
    st.title("Generated specs")
    output_placeholder = st.empty()
    generated_specs = st.session_state.updated_specs
    if generated_specs:
        height = min(400, len(generated_specs) * 30)
        output_placeholder.text_area("", generated_specs, height)
        st.download_button(label="Download Specs", data=generated_specs, file_name="generated_specs.txt", mime="application/txt")
    else:
        height = min(100, 200)
        output_placeholder.markdown(f"<div style='border: 1px solid #3c3c73; padding: 10px; height: {height}px; overflow-y: auto;'>Specs will appear here</div>", unsafe_allow_html=True)

def refine_xslt(xslt_content):
    xslt_tree = etree.XML(xslt_content)
    return etree.tostring(xslt_tree, pretty_print=True).decode()

def compare_xmls(xml1, xml2):
    xml1_normalized = normalize_xml(xml1)
    xml2_normalized = normalize_xml(xml2)
    diff = difflib.HtmlDiff().make_table(xml1_normalized, xml2_normalized, "Source XML", "Target XML", context=True)
    matcher = difflib.SequenceMatcher(None, xml1_normalized, xml2_normalized)
    match_percentage = matcher.ratio() * 100
    return diff, match_percentage

def normalize_xml(xml_string):
    xml_clean = remove_encoding_declaration(xml_string)
    parser = etree.XMLParser(remove_blank_text=True)
    xml_tree = etree.fromstring(xml_clean.encode('utf-8'), parser)
    pretty_xml = etree.tostring(xml_tree, pretty_print=True).decode('utf-8')
    return pretty_xml.strip().splitlines()

def remove_encoding_declaration(xml_string):
    return re.sub(r'<\?xml.*?\?>', '', xml_string)

def refine_and_display_markdown_update(markdown_content):
    lines = markdown_content.split('\n')
    print("Lines : " ,lines)
    modified_content = []
    field_number = 1
    for line in lines[2:]:
        columns = line.split('| ')
        if len(columns) >= 3:
            input_value = columns[1].strip()
            output_value = columns[2].strip()
            remarks = columns[3].strip()
            Type = columns[4].strip()[:-1]
            modified_line = ""
            if input_value or input_value != "NA":
                modified_line += f" Input: {input_value}"
            if output_value or output_value != "NA":
                modified_line += f", Output: {output_value}"
            if remarks or remarks != "NA":
                modified_line += f", Remarks: {remarks}"
            if Type or Type != "NA":
                modified_line += f", Type: {Type}"
            modified_content.append(modified_line)
            field_number += 1
        else:
            modified_content.append(line)
    markdown_content = '\n'.join(modified_content)
    return markdown_content

def refine_and_display_markdown(markdown_content):
    lines = markdown_content.split('\n')
    print("Lines : " ,lines)
    start_index = 0
    for i, item in enumerate(lines):
        if item.strip().startswith('|:---') or item.strip().startswith('|---') :
            start_index = i + 1
            break
    print("start index : ", start_index)
    modified_content = []
    vector_document = []
    field_number = 1

    for line in lines[start_index:]:
        if not line:
            continue
        columns = line.split('|')
        if len(columns) >= 3:
            input_value = columns[2].strip()
            output_value = columns[3].strip()
            remarks = columns[6].strip()
            modified_line = ""
            if input_value and input_value != "NA":
                modified_line += f" Input Xpath: {input_value}"
            else:
                modified_line += f" Input Xpath: NA"
            if output_value and output_value != "NA":
                modified_line += f", Output Xpath: {output_value}"
            if remarks and remarks != "NA":
                modified_line += f", Description: {remarks}"
            modified_content.append(modified_line)
            field_number += 1
        else:
            modified_content.append(line)

    VectorDocument = [Document(text=doc) for doc in modified_content]
    refined_markdown_content = '\n'.join(modified_content)
    return refined_markdown_content,VectorDocument

def convert_html_to_csv(html_content):
    # Importing the required modules 

    # empty list
    data = []
    list_header = []
    soup = BeautifulSoup(html_content,'html.parser')
    header = soup.find_all("table")[0].find("tr")

    for items in header:
        try:
            list_header.append(items.get_text())
        except:
            continue

    # for getting the data 
    HTML_data = soup.find_all("table")[0].find_all("tr")[1:]

    for element in HTML_data:
        sub_data = []
        for sub_element in element:
            try:
                sub_data.append(sub_element.get_text())
            except:
                continue
        data.append(sub_data)

    # Storing the data into Pandas
    # DataFrame 
    dataFrame = pd.DataFrame(data = data, columns = list_header)

    # Converting Pandas DataFrame
    # into CSV file
    csv_buffer = StringIO()
    dataFrame.to_csv(csv_buffer, index=False, encoding='utf-8')  # Write to buffer
    csv_buffer.seek(0)  # Reset buffer pointer to the beginning
    csv_data = csv_buffer.getvalue()  # Get the binary content
    return csv_data,dataFrame


def markdown_to_html_table(md_str):
    headers = ["Input", "Output", "Remarks", "Type"]
    html_rows = ['<table data-table-width="1800" data-layout="full-width">']
    html_rows.append('<tr>' + ''.join(f'<th><p>{h}</p></th>' for h in headers) + '</tr>')
    field_pattern = re.compile(
        r'(Input|Output|Remarks|Type):\s*(.*?)'
        r'(?=,(?:\s*)(?:Input|Output|Remarks|Type):|$)',
        re.IGNORECASE
    )
    if isinstance(md_str, str):
        for row in md_str.strip().split('\n'):
            matches = field_pattern.findall(row)
            field_map = {k.capitalize(): v.strip() for k, v in matches}
            values = [html.escape(field_map.get(h, '')) for h in headers]
            html_rows.append('<tr>' + ''.join(f'<td><p>{v}</p></td>' for v in values) + '</tr>')
    elif isinstance(md_str, list):
        for entry in md_str:
            values = [html.escape(str(entry.get(h) or entry.get(h.lower()) or '')) for h in headers]
            html_rows.append('<tr>' + ''.join(f'<td><p>{v}</p></td>' for v in values) + '</tr>')
    else:
        html_rows.append('<tr><td colspan="4"><p>Invalid specifications format</p></td></tr>')
    html_rows.append('</table>')
    return '\n'.join(html_rows)
