import xml.etree.ElementTree as ET

def parse_and_divide_xml(xml_string):
    # Parse the XML string
    root = ET.fromstring(xml_string)
    
    # Function to recursively print elements and their children
    def print_element(element, level=0):
        indent = "  " * level
        print(f"{indent}<{element.tag}>")
        
        # Print attributes if any
        if element.attrib:
            for attr, value in element.attrib.items():
                print(f"{indent}  @{attr} = {value}")
        
        # Print text content if any
        if element.text and element.text.strip():
            print(f"{indent}  {element.text.strip()}")
        
        # Recursively print child elements
        for child in element:
            print_element(child, level + 1)
        
        print(f"{indent}</{element.tag}>")
    
    # Start printing from the root
    print_element(root)

# Example XML string
xml_string = """
<root>
    <section1>
        <item id="1">Item 1</item>
        <item id="2">Item 2</item>
    </section1>
    <section2>
        <entry key="A">Entry A</entry>
        <entry key="B">Entry B</entry>
    </section2>
</root>
"""

# Parse and divide the XML
with open("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/xml_comparator/ovrs1.xml", "r") as f:
    data = f.read()
parse_and_divide_xml(data)