import xml.etree.ElementTree as ET
import re

def remove_namespace(xml_string):
    """ Removes XML namespace declarations (xmlns) from the XML string """
    return re.sub(r'\s+xmlns="[^"]+"', '', xml_string)

def chunk_xml_recursive(element, parent_path="", depth=1, max_depth=5, processed_elements=None):
    """ Recursively chunks XML while limiting depth """
    if processed_elements is None:
        processed_elements = set()

    chunks = {}

    # Define a unique key for each chunk
    element_key = f"{parent_path}/{element.tag}" if parent_path else element.tag

    # Convert the current element into a string and remove xmlns if present
    element_xml = ET.tostring(element, encoding="unicode").strip()
    element_xml = remove_namespace(element_xml)

    # Stop further chunking if depth > max_depth
    if depth >= max_depth:
        chunks[element_key] = element_xml
        return chunks

    # Process children recursively while maintaining depth
    if len(element):
        for child in element:
            child_key = f"{element_key}/{child.tag}"
            if child_key not in processed_elements:
                processed_elements.add(child_key)
                chunks.update(chunk_xml_recursive(child, element_key, depth + 1, max_depth, processed_elements))

    # Store the parent node as well
    if element_key not in processed_elements:
        processed_elements.add(element_key)
        chunks[element_key] = element_xml

    return chunks

def chunk_complex_xml(xml_string, max_depth=5):
    """ Parses XML and chunks it into logical nodes while ignoring xmlns """
    xml_string = remove_namespace(xml_string)  # Remove xmlns globally before parsing
    root = ET.fromstring(xml_string)
    return chunk_xml_recursive(root, depth=1, max_depth=max_depth)

if __name__ == "__main__":
    with open("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/xml_comparator/ovrs2.xml", "r") as file:
        input = file.read()
          
    xml_data = remove_namespace(input)
    root = ET.fromstring(xml_data)

    # Run function
    chunks = chunk_complex_xml(xml_data, max_depth=5)
    # print(chunks)

    # Display results
    output_file = "output_chunks3.txt"

    try:
        for tag, xml_chunk in chunks.items():
            print(tag, xml_chunk)
        with open(output_file, "w") as file:
            for tag, xml_chunk in chunks.items():
                file.write(f"Chunk for {tag}:\n{xml_chunk}\n\n")
        print(f"Chunks successfully written to {output_file}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")