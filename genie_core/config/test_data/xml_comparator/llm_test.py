import xml.etree.ElementTree as ET
import re

def remove_namespace(xml_string):
    """ Removes XML namespace declarations (xmlns) from the XML string """
    return re.sub(r'\s+xmlns="[^"]+"', '', xml_string)

def chunk_xml_iterative(xml_string, max_depth=5):
    """ Iterative XML chunking with controlled depth """
    xml_string = remove_namespace(xml_string)  # Remove namespaces once
    root = ET.fromstring(xml_string)

    stack = [(root, root.tag, 1)]
    chunks = {}

    while stack:
        element, path, depth = stack.pop()

        # Stop further processing if max depth reached
        if depth > max_depth:
            continue

        # Convert element to string and store
        chunks[path] = ET.tostring(element, encoding="unicode").strip()

        # Add children to stack
        for child in reversed(element):
            child_path = f"{path}/{child.tag}"
            stack.append((child, child_path, depth + 1))

    return chunks

if __name__ == "__main__":
    with open("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/xml_comparator/ovrs2.xml", "r") as file:
        input_xml = file.read()
          
    chunks = chunk_xml_iterative(input_xml, max_depth=5)
    print(chunks)
    
        # Display results
    output_file = "output_chunks_new.txt"

    try:
        for tag, xml_chunk in chunks.items():
            print(tag, xml_chunk)
        with open(output_file, "w") as file:
            for tag, xml_chunk in chunks.items():
                file.write(f"Chunk for {tag}:\n{xml_chunk}\n\n")
        print(f"Chunks successfully written to {output_file}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")