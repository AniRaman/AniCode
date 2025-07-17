# Class to represent a tree node for the XML tree structure
class TreeNode:
    def __init__(self, tag, path):
        self.tag = tag
        self.path = path
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
        current_node = TreeNode(tag, full_path)
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

tree = parse_xml_file_to_tree(f"data/{example_name}/{example_name}_CLRS.xml")