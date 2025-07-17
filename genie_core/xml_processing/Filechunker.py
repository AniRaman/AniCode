import xml.etree.ElementTree as ET
import streamlit as st
# Class to represent a tree node for the XML tree structure
class TreeNode:
    def __init__(self, tag, path, element):
        self.tag = tag
        self.path = path
        self.element = element
        self.n_occurrences = 1  # Initialize with 1 occurrence
        self.children = {}  # Dictionary to store child nodes by tag
        self.subtree_depth = 0  # To be calculated later

    def increment_occurrence(self):
        self.n_occurrences += 1

    def add_child(self, child_node):
        tag = child_node.tag
        # If the child already exists, increment its occurrence
        if tag in self.children:
            self.children[tag].increment_occurrence()
        else:
            self.children[tag] = child_node

    def calculate_subtree_depth(self):
        # Recursively calculate depth for each child
        if not self.children:
            self.subtree_depth = 0
        else:
            self.subtree_depth = 1 + max(
                child.calculate_subtree_depth() for child in self.children.values()
            )
        return self.subtree_depth

    def __repr__(self):
        return f"TreeNode(tag={self.tag}, occurrences={self.n_occurrences}, subtree_depth={self.subtree_depth})"
    
# Recursive function to build the tree from XML
def build_tree_node(element, current_path, node_dict=None):
    if node_dict is None:
        node_dict = {}

    tag = element.tag
    # Build the full path to the current element
    full_path = f"{current_path}/{tag}" if current_path else tag

    # Check if the node for this tag already exists, or create a new one
    if full_path in node_dict:
        current_node = node_dict[full_path]
        current_node.increment_occurrence()
    else:
        current_node = TreeNode(tag, full_path, element)
        node_dict[full_path] = current_node

    # Recursively build the tree for each child element
    for child in element:
        child_node_dict = current_node.children
        build_tree_node(child, full_path, child_node_dict)

    return current_node

# Load and parse the XML file
def parse_xml_file_to_tree(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Build the tree starting from the root element, with an empty path
    root_node = build_tree_node(root, "")

    # Calculate subtree depths starting from the root
    root_node.calculate_subtree_depth()

    return root_node

def get_leaf_nodes(node):
    leaf_nodes = []

    # A leaf node has no children
    if not node.children:
        leaf_nodes.append(f"{node.path}/{node.tag}")
    else:
        # Recursively collect leaf nodes from the children
        for child in node.children.values():
            leaf_nodes.extend(get_leaf_nodes(child))

    return leaf_nodes

subtrees = []

def select_tags(node, tags_to_select = {}, depth = 3):
    if node.subtree_depth <= depth:
        if node.path not in tags_to_select:
            tags_to_select[node.path] = []
        tags_to_select[node.path].append(ET.tostring(node.element, encoding="unicode").strip())
        subtrees.append(get_leaf_nodes(node))
    else:
        for child in node.children.values():
            select_tags(child, tags_to_select, depth)
    return tags_to_select

if __name__ == "__main__":      
    # tree = parse_xml_file_to_tree(f"/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/xml_comparator/10OrderViewRS_PaySeat.xml")
    # tags_to_select = select_tags(tree)

    tree = parse_xml_file_to_tree(f"/Users/nlepakshi/Documents/GitHub/genie/genie_core/config/test_data/xml_comparator/ovrs2.xml")
    print(tree)
    tags_to_select = select_tags(tree)
    
    print(tags_to_select)

    # Print the tags_to_select with XML content
    # output_file = "/Users/nlepakshi/Documents/GitHub/demo_master/genie/genie_core/config/test_data/xml_comparator/tags_and_content8.txt"

    # try:
    #     with open(output_file, "w") as file:
    #         for tag, xml_contents in tags_to_select.items():
    #             for xml_content in xml_contents:
    #                 file.write(f"Tag: {tag}\nXML Content:\n{xml_content}\n\n")
    #     print(f"Tags and XML content successfully written to {output_file}")
    # except Exception as e:
    #     print(f"An error occurred while writing to the file: {e}")
    
    