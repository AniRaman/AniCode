"""Tree diffing utilities for XSLT templates using Zhang-Shasha algorithm."""
from typing import List, Dict, Any, Tuple, Optional
import xml.etree.ElementTree as ET
from lxml import etree
import zss

# Semantically similar XSLT control-flow tags. Treat an `xsl:if` and
# `xsl:when` as interchangeable for diff-cost purposes when they share the
# same predicate.
CONTROL_TAGS = {
    '{http//www.w3.org/1999/XSL/Transform}if',
    '{http//www.w3.org/1999/XSL/Transform}when',
}

def _get_test(attr_str: str) -> str:
    """Return the value of the `test` attribute from a flattened attr string.

    When building labels we flatten the attribute dict into
    ``key1=val1:key2=val2``.  This helper retrieves the `test` value if
    present so we can compare predicates.
    """
    if not attr_str:
        return ''
    for part in attr_str.split(':'):
        if part.startswith('test='):
            return part[len('test='):]
    return ''

class XSLTNode:
    """Wrapper class for XSLT nodes to work with zss."""
    
    def __init__(self, tag: str, attrib: Dict[str, str] = None):
        self.tag = tag
        self.attrib = attrib or {}
        self.children: List['XSLTNode'] = []
        self.parent: Optional['XSLTNode'] = None
        self.value: Optional[str] = None
    
    def add_child(self, node: 'XSLTNode'):
        """Add a child node."""
        node.parent = self
        self.children.append(node)
    
    def to_xml(self) -> str:
        """Convert back to XML string."""
        elem = etree.Element(self.tag, **self.attrib)
        if self.value:
            elem.text = self.value
        for child in self.children:
            elem.append(etree.fromstring(child.to_xml()))
        return etree.tostring(elem, encoding="unicode")


def xml_to_tree(elem: etree._Element) -> XSLTNode:
    """Convert lxml element to XSLTNode tree."""
    node = XSLTNode(
        tag=elem.tag,
        attrib=dict(elem.attrib)
    )
    
    if elem.text and elem.text.strip():
        node.value = elem.text.strip()
    
    for child in elem:
        node.add_child(xml_to_tree(child))

    # print(f"Created XSLTNode: {elem.tag}")
    # print("node : ", node)
    return node


def tree_to_xml(node: XSLTNode) -> etree._Element:
    """Convert XSLTNode tree back to lxml element."""
    elem = etree.Element(node.tag, **node.attrib)
    if node.value:
        elem.text = node.value
    for child in node.children:
        elem.append(tree_to_xml(child))
    return elem

def compute_edit_script(before: str, after: str) -> List[Dict[str, Any]]:
    """
    Compute edit script to transform before XML to after XML.
    Returns a list of edit operations.
    """
    try:
        print("Parsing before XML...")
        before_elem = etree.fromstring(before.encode())
        print("Parsing after XML...")
        after_elem = etree.fromstring(after.encode())
        
        print("Converting before to tree...")
        before_tree = xml_to_tree(before_elem)
        print("Converting after to tree...")
        after_tree = xml_to_tree(after_elem)
        
        print(f"Before tree type: {type(before_tree)}, After tree type: {type(after_tree)}")
        
        def split_at_second_colon(s):
            parts = s.split(":", 2)
            if len(parts) == 2:
                return parts[0], parts[1]
            elif len(parts) == 3:
                return parts[0] + parts[1] , parts[2]
            else:
                return s, ""  # fallback
        
        def get_children(node):
            # Safely get children, return empty list if node has no children attribute
            #print("get children: ", getattr(node, 'children', []))
            return getattr(node, 'children', [])
            
        def get_label(node):
            # Handle case where node is not an XSLTNode (shouldn't happen, but be defensive)
            if not hasattr(node, 'tag'):
                print("get label: ", str(node))
                #print(f"Warning: Node has no tag attribute: {node}")
                return str(node)
                
            # Get attributes safely
            attrs = getattr(node, 'attrib', {})
            if not isinstance(attrs, dict):
                attrs = {}
                
            # Create label with tag and attributes
            attr_str = ':'.join(f'{k}={v}' for k, v in attrs.items()) if attrs else ''
            #print("get label 2: ", f"{node.tag}:{attr_str}")

            return f"{node.tag}:{attr_str}"
            
        def label_dist(a, b) -> int:
            #print("a and b : ",a, " : ",b)

            # # print("Comparing nodes:")
            # # print("Type A:", type(a), "Tag:", getattr(a, 'tag', None))
            # # print("Type B:", type(b), "Tag:", getattr(b, 'tag', None))
            # # Handle case where either node is a string (shouldn't happen, but being defensive)
            # if not hasattr(a, 'tag') or not hasattr(b, 'tag'):
            #     #print(f"Warning: Received non-node in label_dist: {type(a)}, {type(b)}")
            #     #print("label dist: ", 1)
            #     return 1
                        
            if not isinstance(a, str) or not isinstance(b, str):
                # Non-string labels (should not happen) – assign neutral distance
                return 1

            tag_a, attrs_a_str = split_at_second_colon(a)
            tag_b, attrs_b_str = split_at_second_colon(b)
            #print("tag_a : ", tag_a, "tag_b : ", tag_b)
            # Special rule: treat `xsl:if` and `xsl:when` as *nearly identical* when
            # they have the exact same predicate.  This encourages ZSS to align them
            # and generate a cheap *update-tag* instead of remove+insert.
            if tag_a in CONTROL_TAGS and tag_b in CONTROL_TAGS:
                if _get_test(attrs_a_str) == _get_test(attrs_b_str):
                    #print("I am hereeeeeeeeeeeeee")
                    return 1

            # Fallback to generic comparison rules
            if tag_a != tag_b:
                return 3  # different element types – higher cost

            # Same tag but different attributes – higher cost so that matching
            # tags with identical predicates is preferred over mismatched ones.
            return 2 if attrs_a_str != attrs_b_str else 0
            
        # Compute edit script using Zhang-Shasha
        result, ops = zss.simple_distance(
            before_tree, 
            after_tree,
            get_children,
            get_label,
            label_dist,
            return_operations=True
        )
        print("ops: ", ops)
        # Handle case where we get a float (distance) instead of operations
        if isinstance(ops, (int, float)):
            print(f"Warning: zss returned distance value instead of operations: {ops}")
            # Fall back to a simple replacement for now
            return [{
                'op': 'replace',
                'content': after
            }]
            
        # Otherwise, process the operations
        operations = []
        for op in ops:
            #print("op : ", op, "op type : ", op.type)
            if not hasattr(op, 'type'):
                print("hasattr")
                #print(f"Warning: Unexpected operation format: {op}")
                continue
                
            if op.type == 0:
                print("remove")
                operations.append({
                    'op': 'remove',
                    'path': _get_node_path(op.arg1) if hasattr(op, 'arg1') else ''
                })
            elif op.type == 1:
                print("insert")
                if not hasattr(op, 'arg1') or not hasattr(op, 'arg2'):
                    print(f"Warning: Malformed insert operation: {op}")
                    continue
                    
                parent_path = ''
                position = 0
                if hasattr(op.arg1, 'parent') and op.arg1.parent:
                    parent_path = _get_node_path(op.arg1.parent)
                    if hasattr(op.arg1.parent, 'children') and hasattr(op.arg1, 'tag'):
                        try:
                            position = op.arg1.parent.children.index(op.arg1)
                        except (ValueError, AttributeError):
                            pass
                
                operations.append({
                    'op': 'insert',
                    'node': op.arg2.to_xml() if hasattr(op.arg2, 'to_xml') else str(op.arg2),
                    'parent_path': parent_path,
                    'position': position
                })
                
            elif op.type == 2:
                print("update")
                if not hasattr(op, 'arg1') or not hasattr(op, 'arg2'):
                    print(f"Warning: Malformed update operation: {op}")
                    continue
                    
                # Only generate update instructions for the pieces that actually
                # differ between the *before* and *after* nodes.  This prevents
                # us from overwriting chunk-specific attributes unnecessarily.
                tag_before = getattr(op.arg1, 'tag', '')
                tag_after = getattr(op.arg2, 'tag', '')
                attrib_before = getattr(op.arg1, 'attrib', {}) or {}
                attrib_after = getattr(op.arg2, 'attrib', {}) or {}
                value_before = getattr(op.arg1, 'value', None)
                value_after = getattr(op.arg2, 'value', None)

                tag_changed = tag_before != tag_after
                attrib_changed = attrib_before != attrib_after
                value_changed = value_before != value_after

                if not (tag_changed or attrib_changed or value_changed):
                    continue  # nothing really changed

                upd_op: Dict[str, Any] = {
                    'op': 'update',
                    'path': _get_node_path(op.arg1) if hasattr(op.arg1, 'tag') else ''
                }
                if tag_changed:
                    upd_op['new_tag'] = tag_after
                if attrib_changed:
                    upd_op['new_attrib'] = attrib_after
                if value_changed:
                    upd_op['new_value'] = value_after

                operations.append(upd_op)
        print("Operations: ", operations)        
        return operations
        
    except Exception as e:
        print(f"Error computing edit script: {e}")
        print("Empty List in edit compute action")
        return []


def _get_node_path(node: XSLTNode) -> str:
    """Return an XPath-like path for a node.
    
    The index for each step is calculated **among siblings that share the same
    expanded tag name** (i.e. including the namespace). This makes the produced
    paths consistent with standard XPath positional predicates, where
    `xsl:for-each[1]` means *the first `xsl:for-each` child*, not necessarily
    the first child of any tag.
    """
    segments: List[str] = []
    current: Optional[XSLTNode] = node

    while current is not None and current.parent is not None:
        # Siblings that have the exact same tag (namespace-qualified)
        same_tag_siblings = [c for c in current.parent.children if c.tag == current.tag]
        # XPath is 1-based
        position = same_tag_siblings.index(current) + 1
        segments.append(f"{current.tag}[{position}]")
        current = current.parent

    # Build path from root to leaf
    return "/" + "/".join(reversed(segments)) if segments else ""


def fix_xpath_namespaces(path: str) -> str:
    return path.replace(
        '{http://www.w3.org/1999/XSL/Transform}', 'xsl:'
    ).replace(
        '{http://www.altova.com/MapForce/UDF/tbf}', 'tbf:'
    ).replace(
        '{http://www.opentravel.org/OTA/2003/05}', 'ns0:'
    ).replace(
        '{http://www.w3.org/2001/XMLSchema}', 'xs:'
    )

def apply_edit_script(xml_str: str, operations: List[Dict[str, Any]]) -> str:
    """
    Apply edit operations to XML string.
    
    Args:
        xml_str: The original XML as a string
        operations: List of edit operations to apply
        
    Returns:
        The modified XML as a string
    """
    #print("Operations inside apply edit script: ", operations)
    
    NSMAP = {
        'xsl': 'http://www.w3.org/1999/XSL/Transform',
        'tbf': 'http://www.altova.com/MapForce/UDF/tbf',
        'ns0': 'http://www.opentravel.org/OTA/2003/05',
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }

    # ------------------------------------------------------------------
    # Helper utilities to translate cached XPaths onto the *current* tree
    # ------------------------------------------------------------------
    import re  # local dependency only within this function

    def _resolve_path_on_tree(path: str, context: etree._Element):
        """Resolve an *index-based* path like `xsl:for-each[2]/xsl:attribute[1]` on
        `context` without relying on namespaces. Returns the matched element
        or None if traversal fails."""
        segments = re.findall(r'([^/\[]+)\[(\d+)\]', path)
        node = context
        for seg_tag, seg_idx in segments:
            idx = int(seg_idx)
            local = seg_tag.split(':')[-1]  # ignore prefix if present
            # keep only element children whose *local* tag matches
            matching = [c for c in node if isinstance(c.tag, str) and etree.QName(c).localname == local]
            if idx < 1 or idx > len(matching):
                return None  # structure diverged
            node = matching[idx - 1]
        return node

    def _find_nodes(context: etree._Element, original_path: str):
        """Find nodes in `context` matching a cached path. Tries namespace-aware
        XPath first, then falls back to the pure-localname walk above."""
        xpath_fixed = fix_xpath_namespaces(original_path.lstrip('/'))
        try:
            nodes = context.xpath(xpath_fixed, namespaces=NSMAP)
        except Exception:
            nodes = []
        if nodes:
            return nodes
        fallback = _resolve_path_on_tree(original_path.lstrip('/'), context)
        return [fallback] if fallback is not None else []

    if not operations:
        return xml_str
        
    try:
        # Parse the XML
        try:
            root = etree.fromstring(xml_str.encode())
            print("root : " , etree.tostring(root, pretty_print=True).decode())
        except etree.XMLSyntaxError as e:
            print(f"Error parsing XML: {e}")
            return xml_str
            
        # Split operations – apply non-removes first, then removes in a safe order
        remove_ops = []
        primary_ops = []
        for op in operations:
            if isinstance(op, dict) and op.get('op') == 'remove':
                remove_ops.append(op)
            else:
                primary_ops.append(op)

        # First run updates / inserts / replace / match in original order
        for op in primary_ops:
            if not isinstance(op, dict) or 'op' not in op:
                print(f"Warning: Invalid operation format: {op}")
                continue
                
            try:
                if op['op'] == 'remove':
                    # Handle remove operation
                    if 'path' not in op:
                        print("Warning: Missing 'path' in remove operation")
                        continue
                        
                    try:
                        if op['path'].startswith("/"):
                            op['path'] = op['path'].lstrip("/")
                        nodes = _find_nodes(root, op['path'])
                        if not nodes:
                            print(f"Warning: No node found at path, so not removing: {op['path']}")
                            continue
                        print(f"Success: Found node at path, now removing: {op['path']}") 
                        node = nodes[0]
                        parent = node.getparent()
                        if parent is not None:
                            # Hoist children of the removed node to preserve inner content
                            insert_pos = parent.index(node)
                            for child in list(node):
                                parent.insert(insert_pos, child)
                                insert_pos += 1
                            parent.remove(node)
                    except Exception as e:
                        print(f"Error in remove operation {op}: {e}")
                        
                elif op['op'] == 'insert':
                    # Handle insert operation
                    if 'node' not in op:
                        print("Warning: Missing 'node' in insert operation")
                        continue
                        
                    try:
                        if op['path'].startswith("/"):
                            op['path'] = op['path'].lstrip("/")
                        # Create new node
                        new_node = etree.fromstring(op['node'].encode())
                        
                        # Find parent node
                        parent = root
                        if 'parent_path' in op and op['parent_path']:
                            parents = _find_nodes(root, op['parent_path'])
                            if parents:
                                parent = parents[0]
                        
                        # Insert at position if specified
                        if 'position' in op and op['position'] is not None:
                            parent.insert(op['position'], new_node)
                        else:
                            parent.append(new_node)
                    except Exception as e:
                        print(f"Error in insert operation {op}: {e}")
                        
                elif op['op'] == 'update':
                    # Handle update operation
                    if 'path' not in op:
                        print("Warning: Missing 'path' in update operation")
                        continue
                        
                    try:
                        if op['path'].startswith("/"):
                            op['path'] = op['path'].lstrip("/")
                        nodes = _find_nodes(root, op['path'])
                        
                        if not nodes:
                            print(f"Warning: No node found at path, so not updating: {op['path']}")
                            continue
                        print(f"Success: Found node at path, now updating: {op['path']}")
                        node = nodes[0]
                        print("Node: ", node)
                        if 'new_tag' in op and op['new_tag']:
                            print("New tag: ", op['new_tag'])
                            node.tag = op['new_tag']
                        if 'new_attrib' in op and isinstance(op['new_attrib'], dict):
                            # Merge – update only the provided attributes to
                            # avoid dropping any that were not part of the diff.
                            for k, v in op['new_attrib'].items():
                                node.attrib[k] = v
                        if 'new_value' in op and op['new_value'] is not None:
                            node.text = str(op['new_value'])
                    except Exception as e:
                        print(f"Error in update operation {op}: {e}")
                        
                elif op['op'] == 'replace':
                    # Handle full content replacement
                    if 'content' in op:
                        print(f"Success: Found node at path, now replacing: {op.get('path', '(root)')}")
                        return op['content']
                        
                elif op['op'] == 'match':
                    # Preserve structure – nothing to do
                    continue

            except Exception as e:
                print(f"Unexpected error processing operation {op}: {e}")
                continue

        # Now process removes in a safe order: deepest paths first, highest sibling index first
        def _remove_sort_key(r):
            p = r.get('path', '')
            depth = p.count('/')
            import re
            m = re.search(r'\[(\d+)\]$', p)
            idx = int(m.group(1)) if m else 0
            return (depth, idx)
        remove_ops.sort(key=_remove_sort_key, reverse=True)

        for op in remove_ops:
            try:
                if 'path' not in op:
                    print("Warning: Missing 'path' in remove operation")
                    continue
                if op['path'].startswith('/'):
                    op['path'] = op['path'].lstrip('/')
                nodes = _find_nodes(root, op['path'])
                if not nodes:
                    print(f"Warning: No node found at path, so not removing: {op['path']}")
                    continue
                print(f"Success: Found node at path, now removing: {op['path']}")
                node = nodes[0]
                parent = node.getparent()
                if parent is not None:
                    # Hoist children to keep inner content when wrapper removed
                    insert_pos = parent.index(node)
                    for child in list(node):
                        parent.insert(insert_pos, child)
                        insert_pos += 1
                    parent.remove(node)
            except Exception as e:
                print(f"Error in deferred remove operation {op}: {e}")
                continue

        # Return the modified XML
        return etree.tostring(root, encoding="unicode", pretty_print=True)
        
    except Exception as e:
        print(f"Critical error in apply_edit_script: {e}")
        return xml_str
