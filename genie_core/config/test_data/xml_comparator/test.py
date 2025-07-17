import xml.etree.ElementTree as ET
import re
import math

def remove_namespace(xml_string):
    """Removes XML namespace declarations (xmlns) from the XML string"""
    return re.sub(r'\s+xmlns="[^"]+"', '', xml_string)

def split_into_chunks(elements, max_chunks):
    """Splits a list of elements into max_chunks parts safely"""
    if not elements:
        return []
    chunk_size = max(1, math.ceil(len(elements) / max_chunks))  # Ensure at least 1
    return [elements[i:i + chunk_size] for i in range(0, len(elements), chunk_size)]

def chunk_xml_recursive(element, parent_path="", depth=1, max_depth=5, chunks=None):
    """Recursively chunks an XML document based on depth"""
    if chunks is None:
        chunks = {}

    element_key = f"{parent_path}/{element.tag}" if parent_path else element.tag
    element_xml = ET.tostring(element, encoding="unicode").strip()

    # Remove xmlns if present
    element_xml = remove_namespace(element_xml)

    # If element has no children and depth is within max_depth, store as-is
    if len(element) == 0 and depth <= max_depth:
        chunks[element_key] = element_xml
        return chunks

    # If depth exceeds max_depth, split into max_depth/2 chunks
    if depth > max_depth:
        max_chunks = max(1, math.ceil(max_depth / 2))
        child_groups = split_into_chunks(list(element), max_chunks)

        for idx, group in enumerate(child_groups, start=1):
            if not group:
                continue  # Skip empty groups

            new_element = ET.Element(element.tag)
            for child in group:
                new_element.append(child)
            chunk_key = f"{element_key}_part{idx}"
            chunk_xml_recursive(new_element, element_key, depth, max_depth, chunks)
    else:
        # If depth is within limit, process children normally
        for child in element:
            chunk_xml_recursive(child, element_key, depth + 1, max_depth, chunks)

    return chunks

# Complex XML Example
xml_data = """<root xmlns="http://example.com/schema">
    <Pax>
        <paxList>
            <pax>
                <name>John Doe</name>
                <details>
                    <passport>123456</passport>
                    <visa>
                        <country>USA</country>
                        <validity>
                            <from>2024</from>
                            <to>2030</to>
                        </validity>
                    </visa>
                </details>
            </pax>
            <pax>
                <name>Jane Doe</name>
                <details>
                    <passport>654321</passport>
                    <visa>
                        <country>Canada</country>
                        <validity>
                            <from>2022</from>
                            <to>2028</to>
                        </validity>
                    </visa>
                </details>
            </pax>
        </paxList>
    </Pax>
    <BaggageAllowance>
        <services>
            <service>
                <type>Extra Baggage</type>
                <weight>10kg</weight>
            </service>
            <service>
                <type>Priority Boarding</type>
                <weight>5kg</weight>
            </service>
        </services>
    </BaggageAllowance>
</root>"""

# Parse and remove namespaces
xml_data = remove_namespace(xml_data)
root = ET.fromstring(xml_data)

# Run function
chunks = chunk_xml_recursive(root, max_depth=8)

# Display results
for tag, xml_chunk in chunks.items():
    print(f"Chunk for {tag}:\n{xml_chunk}\n")
