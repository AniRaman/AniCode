"""Utility for caching XSLT template refinements based on structural fingerprint.

A "fingerprint" is a SHA-256 hash computed from the ordered list of XSLT control-structure
 tags (for-each / choose / when / otherwise / if / attribute / value-of / copy-of) that
 appear in the template.  All attributes and literal result elements are ignored so that
 templates with the same control-flow skeleton map to a single fingerprint.

The module also contains a *rule-based* refiner that performs optimizations
 so that repeated shapes can be refined without an LLM round-trip:
    1. Remove <xsl:variable name="var*_cur" select="." /> boilerplate.
    2. Merge simple attribute loops into a single xsl:copy-of (if <=10 attributes).
    3. Collapse trivial nested for-each loops into literal result elements (best-effort).
    4. Optimize direct attribute copying to xsl:copy-of.
    5. Convert conditional attribute patterns to xsl:copy-of.
    6. Merge multiple consecutive xsl:copy-of elements.
    7. Optimize simple element copying patterns.
    8. Eliminate trivial for-each loops.
    9. Standardize boolean type conversion patterns.
    10. Simplify complex boolean patterns (Rule 8).

These rules are *safe* – they will skip a template if they detect any unexpected complexity.
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
from pathlib import Path
import json
from typing import List, Tuple, Optional, Dict, Any

from lxml import etree

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_DB_DIR = Path("xslt_generator/database")
_DB_DIR.mkdir(parents=True, exist_ok=True)
_DB_PATH = _DB_DIR / "refine_cache.db"

_ALLOWED_TAGS = {
    "for-each",
    "choose",
    "when",
    "otherwise",
    "if",
    "attribute",
    "value-of",
    "copy-of",
    "variable",
}
XSLT_NS = "http://www.w3.org/1999/XSL/Transform"
NSMAP = {"xsl": XSLT_NS}

# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS refinements (
                fingerprint   TEXT PRIMARY KEY,
                actions_json  TEXT
            )"""
    )
    # Ensure the new column exists when upgrading from old schema
    cols = [row[1] for row in conn.execute("PRAGMA table_info(refinements)")]
    if "actions_json" not in cols:
        conn.execute("ALTER TABLE refinements ADD COLUMN actions_json TEXT")
        conn.commit()
    return conn


def get_cached_actions(fingerprint: str) -> Optional[List[Dict[str, Any]]]:
    """Return the list of recorded actions for the fingerprint, if present."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT actions_json FROM refinements WHERE fingerprint = ?", (fingerprint,)
        ).fetchone()
        return json.loads(row[0]) if row and row[0] else None


def cache_actions(fingerprint: str, actions: List[Dict[str, Any]]) -> None:
    """Cache the actions for the fingerprint."""
    with _get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO refinements (fingerprint, actions_json) VALUES (?, ?)",
            (fingerprint, json.dumps(actions)),
        )
        conn.commit()
    print(f"Recorded actions for pattern {fingerprint[:8]} in SQLite cache")


def apply_cached_actions(template_text: str, fingerprint: str) -> str:
    """Apply cached actions to the template text."""
    actions = get_cached_actions(fingerprint)
    if actions:
        return apply_actions(template_text, actions)
    return template_text


def apply_actions(template_text: str, actions: List[Dict[str, Any]]) -> str:
    """
    Apply the recorded actions to the template text using tree diffing.
    
    Args:
        template_text: The original XSLT template text
        actions: List of actions to apply
        
    Returns:
        The refined XSLT template text
    """
    if not actions:
        return template_text
        
    # Handle special passthrough created from LLM diff placeholder (legacy)
    if len(actions) == 1 and actions[0].get("op") == "llm_passthrough":
        print("After applying actions", actions[0].get("refined", template_text))
        return actions[0].get("refined", template_text)
    
    # Apply each action in sequence
    result = template_text
    for act in actions:
        op = act.get("op")
        try:
            if op == "tree_edit":
                # Apply tree edit operations
                result = apply_edit_script(result, act["edit_script"])
                
                # Apply XPath placeholders if any
                if "xpath_placeholders" in act and act["xpath_placeholders"]:
                    for placeholder, xpath in act["xpath_placeholders"].items():
                        result = result.replace(placeholder, xpath)
                        
            # Keep legacy actions for backward compatibility
            elif op in ["remove_var_cur", "merge_attr_loops", "collapse_nested_loops"]:
                # Parse the current result
                elem = etree.fromstring(result.encode())
                
                # Apply the legacy action
                if op == "remove_var_cur":
                    _remove_var_cur(elem)
                elif op in ("merge_attr_loops", "merge_attr_loops_partial"):
                    _merge_simple_attr_loops(elem)
                elif op == "collapse_nested_loops":
                    _collapse_nested_loops(elem)
                    
                # Convert back to string
                result = etree.tostring(elem, encoding="unicode", pretty_print=True)
                
        except Exception as e:
            print(f"Error applying action {op}: {e}")
            continue
    
    print("After applying actions:", result)
    return result


# ---------------------------------------------------------------------------
# Fingerprint computation
# ---------------------------------------------------------------------------

def _collect_tag_sequence(elem: etree._Element, seq: List[str]) -> None:
    """DFS collecting tag local-names for whitelisted XSLT instructions."""
    if isinstance(elem.tag, str):
        q = etree.QName(elem)
        if q.namespace == XSLT_NS and q.localname in _ALLOWED_TAGS:
            seq.append(q.localname)
    for child in elem:
        _collect_tag_sequence(child, seq)


def compute_fingerprint(template_elem: etree._Element) -> str:
    """Compute the fingerprint for the template element."""
    seq: List[str] = []
    _collect_tag_sequence(template_elem, seq)
    joined = ",".join(seq)
    return hashlib.sha256(joined.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Rule-based refiner for repeated shapes
# ---------------------------------------------------------------------------

def _remove_var_cur(elem: etree._Element) -> bool:
    """Delete <xsl:variable name="var*_cur" select="."/> nodes in-place."""
    to_remove = elem.xpath(
        ".//xsl:variable[starts-with(@name, 'var') and contains(@name, '_cur') and @select='.']",
        namespaces=NSMAP,
    )
    for node in to_remove:
        parent = node.getparent()
        if parent is not None:
            parent.remove(node)
    return bool(to_remove)


def _merge_simple_attr_loops(template: etree._Element, placeholder_map=None, placeholder_counter=None) -> Tuple[bool, List[str], bool]:
    """Collapse consecutive attribute for-each loops into **one** union loop.

    This rule finds any block of consecutive <xsl:for-each> siblings that select
    a single attribute and rewrites them into a single loop using a union
    in the select. It works anywhere in the template tree.

    Pattern recognised:
        <xsl:for-each select="@Foo | ./@Foo | $input/@Foo">
            <xsl:attribute name="Foo">
                <xsl:value-of select="."/>
            </xsl:attribute>
        </xsl:for-each>

    """
    overall_changed = False
    all_merged_attrs: List[str] = []
    is_template_pure_block = False

    # Find all elements that are parents of for-each loops to check for merges
    candidate_parents = template.xpath(".//*[xsl:for-each]", namespaces=NSMAP)
    if template.xpath("./xsl:for-each", namespaces=NSMAP):
        candidate_parents.append(template)

    for parent in set(candidate_parents):
        # Filter out insignificant whitespace to allow merging across formatted code
        children = [c for c in parent if not (isinstance(c, etree._Comment) or (not hasattr(c, 'tag') and str(c).isspace()))]
        i = 0
        while i < len(children):
            # Find a starting for-each that matches our simple pattern
            block_loops: List[etree._Element] = []
            block_attr_names: List[str] = []
            block_prefixes: List[str] = []
            block_valueof_select: str = ""

            j = i
            while j < len(children):
                child = children[j]
                if not (isinstance(child.tag, str) and etree.QName(child).localname == "for-each"):
                    break  # Not a for-each, block ends

                sel = child.get("select", "")
                prefix = ""
                attr_name = ""
                
                if sel.startswith("$input/@"):
                    prefix = "$input/@"
                    attr_name = sel[len(prefix):]
                elif sel.startswith("./@"):
                    prefix = "./@"
                    attr_name = sel[len(prefix):]
                elif sel.startswith("@"):
                    prefix = "@"
                    attr_name = sel[len(prefix):]
                else:
                    # Check for namespace patterns like "ns0:Element/@Attribute"
                    import re
                    ns_match = re.match(r'^([^@]+)/@(\w+)$', sel)
                    if ns_match:
                        prefix = ns_match.group(1) + "/@"
                        attr_name = ns_match.group(2)
                    else:
                        break # select pattern not recognized

                if not attr_name or "/" in attr_name or "[" in attr_name:
                    break # too complex

                attr_elems = child.xpath("./xsl:attribute", namespaces=NSMAP)
                if len(attr_elems) != 1 or attr_elems[0].get("name") != attr_name:
                    break # must have one attribute child that matches

                # Check value-of expression compatibility
                value_of_elems = attr_elems[0].xpath("./xsl:value-of", namespaces=NSMAP)
                if len(value_of_elems) != 1:
                    break # must have exactly one value-of
                
                current_valueof_select = value_of_elems[0].get("select", "")
                
                # For first loop in block, store the value-of expression
                if j == i:
                    block_valueof_select = current_valueof_select
                else:
                    # For subsequent loops, check if value-of expressions match
                    if current_valueof_select != block_valueof_select:
                        print(f"Breaking tree-based merge: value-of mismatch ({block_valueof_select} vs {current_valueof_select})")
                        break # Different value-of expressions, can't merge

                # Pattern matches, add to current block
                block_loops.append(child)
                block_attr_names.append(attr_name)
                block_prefixes.append(prefix)
                j += 1

            if len(block_loops) > 1:
                # Merge the collected block
                overall_changed = True
                all_merged_attrs.extend(block_attr_names)

                # If placeholders are enabled, create placeholder for this merge
                if placeholder_map is not None and placeholder_counter is not None:
                    # Create optimized content as string
                    base_prefix = block_prefixes[0]
                    
                    # For namespace patterns, we need to reconstruct properly
                    if "/" in base_prefix and not base_prefix.startswith(("$input/@", "./@", "@")):
                        # This is a namespace pattern like "ns0:VehRentalCore/@"
                        # Remove trailing /@ to get base element
                        base_element = base_prefix.rstrip("/@")
                        select_parts = [f"{base_element}/@{attr}" for attr in block_attr_names]
                    else:
                        # Traditional pattern
                        select_parts = [f"{base_prefix}{attr}" for attr in block_attr_names]
                    
                    # Create optimized content string
                    union_select = " | ".join(select_parts)
                    optimized_content = f'''<xsl:for-each select="{union_select}">
\t\t\t<xsl:attribute name="{{name()}}">
\t\t\t\t<xsl:value-of select="."/>
\t\t\t</xsl:attribute>
\t\t</xsl:for-each>'''
                    
                    # Create placeholder
                    placeholder = f"<simpletag{placeholder_counter[0]}/>"
                    placeholder_map[placeholder] = optimized_content
                    placeholder_counter[0] += 1
                    
                    # Replace all block loops with a single placeholder element
                    placeholder_elem = etree.Element(placeholder.replace('<', '').replace('/>', '').replace('>', ''))
                    
                    # Insert placeholder at position of first loop
                    parent.insert(list(parent).index(block_loops[0]), placeholder_elem)
                    
                    # Remove all original loops
                    for loop in block_loops:
                        parent.remove(loop)
                        
                    print(f"Created placeholder for attribute merge: {len(block_attr_names)} attributes -> {placeholder}")
                else:
                    # No placeholders - direct tree modification (existing behavior)
                    base_prefix = block_prefixes[0]
                    first_fe = block_loops[0]
                    
                    # For namespace patterns, we need to reconstruct properly
                    if "/" in base_prefix and not base_prefix.startswith(("$input/@", "./@", "@")):
                        # This is a namespace pattern like "ns0:VehRentalCore/@"
                        # Remove trailing /@ to get base element
                        base_element = base_prefix.rstrip("/@")
                        select_parts = [f"{base_element}/@{attr}" for attr in block_attr_names]
                    else:
                        # Traditional pattern
                        select_parts = [f"{base_prefix}{attr}" for attr in block_attr_names]
                    
                    first_fe.set("select", " | ".join(select_parts))

                    for var in first_fe.xpath("./xsl:variable", namespaces=NSMAP):
                        var.getparent().remove(var)
                    
                    attr_elem = first_fe.xpath("./xsl:attribute", namespaces=NSMAP)[0]
                    attr_elem.set("name", "{name()}")

                    for fe_to_remove in block_loops[1:]:
                        parent.remove(fe_to_remove)
                
                # A merge happened. The list of children has changed.
                # We restart the scan on the modified parent.
                children = [c for c in parent if not (isinstance(c, etree._Comment) or (not hasattr(c, 'tag') and str(c).isspace()))]
                i = 0
            else:
                # No merge occurred. Advance `i` to the next position to scan.
                # If the inner `j` loop made no progress, advance by 1. Otherwise, jump to the end of the scanned block.
                if i == j:
                    i += 1
                else:
                    i = j

    if overall_changed:
        # Final check for pure_block status of the whole template
        def _is_ignorable(child: etree._Element) -> bool:
            if not isinstance(child.tag, str):
                return True  # text, comments etc.
            q = etree.QName(child)
            if q.namespace != XSLT_NS:
                return False  # literal result element
            if q.localname == "param" and child.get("name") == "input":
                return True
            if q.localname == "value-of":
                return True
            return False

        # A template is a pure block if it has one child (the merged loop) or ignorable nodes
        num_children = 0
        for child in template:
            if not _is_ignorable(child):
                num_children += 1
        is_template_pure_block = (num_children == 1)

    print("DEBUG merge_simple called, changed?", overall_changed, "merged:", all_merged_attrs[:10])
    return overall_changed, all_merged_attrs, is_template_pure_block


def _collapse_nested_loops(template: etree._Element, placeholder_map=None, placeholder_counter=None) -> bool:
    """Collapse trivial nested for-each loops into literal result elements (best-effort)."""
    # TODO: implement this
    return False

from .tree_diff import compute_edit_script, apply_edit_script

def _compute_edit_actions(before_elem: etree._Element, after_elem: etree._Element) -> List[Dict[str, Any]]:
    """
    Compute edit actions to transform before_elem into after_elem using tree diffing.
    Returns a list of actions that can be replayed on similar templates.
    """
    # Convert elements to strings for diffing
    before_str = etree.tostring(before_elem, encoding="unicode")
    after_str = etree.tostring(after_elem, encoding="unicode")
    
    # Get the edit script using Zhang-Shasha algorithm
    edit_script = compute_edit_script(before_str, after_str)
    
    # Store the original XPath expressions for later restoration
    xpath_placeholders = {}
    for attr in ['select', 'test', 'match']:
        if attr in before_elem.attrib:
            xpath_placeholders[f'{{{attr}}}'] = before_elem.attrib[attr]
    
    # Add the edit script to our actions
    actions = [{
        'op': 'tree_edit',
        'edit_script': edit_script,
        'xpath_placeholders': xpath_placeholders
    }]
    
    return actions

def _process_simple_matches(template_text: str, matches):
    """Process simple @attr matches like select='@Status' name='Status'."""
    return _process_matches_with_base_selector(template_text, matches, "@", extract_attr_from_group=1)


def _process_complex_matches(template_text: str, matches):
    """Process complex matches like select='ns0:Element/@attr' name='attr'."""
    return _process_matches_with_dynamic_selector(template_text, matches, group_for_full_select=1, group_for_attr=2)


def _process_complex_matches_with_valueof(template_text: str, matches):
    """Process complex matches grouped by value-of expression."""
    import re
    
    # Group matches by both base selector and value-of expression
    groups_by_selector_and_valueof = {}
    
    for match in matches:
        full_select = match.group(1)  # e.g., "ns0:VehRentalCore/@PickUpDateTime"
        attr_name = match.group(2)    # e.g., "PickUpDateTime"
        valueof_expr = match.group(3) # e.g., "." or "number(.)"
        
        # Extract base path (everything before the last /@)
        base_match = re.match(r'(.*)/@\w+$', full_select)
        if base_match:
            base_path = base_match.group(1)  # e.g., "ns0:VehRentalCore"
        else:
            base_path = ""
        
        # Create a key that combines base path and value-of expression
        key = f"{base_path}|{valueof_expr}"
        
        if key not in groups_by_selector_and_valueof:
            groups_by_selector_and_valueof[key] = []
        
        groups_by_selector_and_valueof[key].append({
            'match': match,
            'full_select': full_select,
            'attr': attr_name,
            'valueof': valueof_expr
        })
    
    # Process each group that has the same base path and value-of expression
    result = template_text
    offset = 0
    
    for key, group in groups_by_selector_and_valueof.items():
        if len(group) < 2:
            continue  # Need at least 2 to merge
        
        base_path, valueof_expr = key.split('|', 1)
        
        # Sort by position to ensure proper consecutive grouping
        group.sort(key=lambda x: x['match'].start())
        
        # Group consecutive matches
        consecutive_groups = []
        current_group = [group[0]]
        
        for i in range(1, len(group)):
            if group[i]['match'].start() - current_group[-1]['match'].end() < 200:
                current_group.append(group[i])
            else:
                if len(current_group) > 1:
                    consecutive_groups.append(current_group)
                current_group = [group[i]]
        
        if len(current_group) > 1:
            consecutive_groups.append(current_group)
        
        # Process consecutive groups
        for cons_group in consecutive_groups:
            # Create merged for-each with the same value-of expression
            if base_path:
                select_expr = ' | '.join(f'{base_path}/@{item["attr"]}' for item in cons_group)
            else:
                select_expr = ' | '.join(f'@{item["attr"]}' for item in cons_group)
            
            # Use the original value-of expression for this group
            merged_for_each = f'''<xsl:for-each select="{select_expr}">
                                                                <xsl:attribute name="{{name()}}" namespace="">
                                                                        <xsl:value-of select="{valueof_expr}"/>
                                                                </xsl:attribute>
                                                        </xsl:for-each>'''
            
            # Replace the entire group
            start_pos = cons_group[0]['match'].start() + offset
            end_pos = cons_group[-1]['match'].end() + offset
            
            result = result[:start_pos] + merged_for_each + result[end_pos:]
            offset += len(merged_for_each) - (end_pos - start_pos)
    
    return result


def _process_matches_with_base_selector(template_text: str, matches, base_selector: str, extract_attr_from_group: int, placeholder_map=None, placeholder_counter=None):
    """Helper to process matches where all have the same base selector."""
    import re
    
    # Group consecutive matches, but only if there are no structural patterns between them
    consecutive_groups = []
    current_group = [matches[0]]
    
    for i in range(1, len(matches)):
        # Check if this match is close to the previous one (within 200 chars)
        distance = matches[i].start() - current_group[-1].end()
        if distance < 200:
            # Check if there are any structural patterns between these matches
            between_start = current_group[-1].end()
            between_end = matches[i].start()
            between_content = template_text[between_start:between_end]
            
            # Look for structural tags (non-xsl tags) between matches
            structural_pattern = r'<(?!/?xsl:|/?\s*xsl:)[^>]+>'
            has_structural_tags = bool(re.search(structural_pattern, between_content))
            
            if has_structural_tags:
                # Structural elements found between - start new group
                if len(current_group) > 1:
                    consecutive_groups.append(current_group)
                current_group = [matches[i]]
                print(f"Breaking consecutive group due to structural elements between attribute matches")
            else:
                # No structural barriers - safe to group
                current_group.append(matches[i])
        else:
            if len(current_group) > 1:
                consecutive_groups.append(current_group)
            current_group = [matches[i]]
    
    if len(current_group) > 1:
        consecutive_groups.append(current_group)
    
    if not consecutive_groups:
        return template_text
    
    # Process each group
    result = template_text
    offset = 0
    
    for group in consecutive_groups:
        # Extract attribute names
        attr_names = [match.group(extract_attr_from_group) for match in group]
        
        # Create merged for-each
        select_expr = ' | '.join(f'{base_selector}{attr}' for attr in attr_names)
        merged_for_each = f'''<xsl:for-each select="{select_expr}">
                                                                <xsl:attribute name="{{name()}}" namespace="">
                                                                        <xsl:value-of select="."/>
                                                                </xsl:attribute>
                                                        </xsl:for-each>'''
        
        # Replace the entire group
        start_pos = group[0].start() + offset
        end_pos = group[-1].end() + offset
        
        # If placeholder parameters provided, create placeholder
        if placeholder_map is not None and placeholder_counter is not None:
            placeholder = f"<simpletag{placeholder_counter[0]}/>"
            placeholder_map[placeholder] = merged_for_each
            placeholder_counter[0] += 1
            replacement = placeholder
        else:
            replacement = merged_for_each
        
        result = result[:start_pos] + replacement + result[end_pos:]
        offset += len(replacement) - (end_pos - start_pos)
    
    return result


def _process_matches_with_dynamic_selector(template_text: str, matches, group_for_full_select: int, group_for_attr: int, placeholder_map=None, placeholder_counter=None):
    """Helper to process matches where we need to extract the base selector dynamically."""
    import re
    print("inside dynamic selector")
    
    # Group consecutive matches, but only if they have the same value-of expression
    consecutive_groups = []
    current_group = [matches[0]]
    
    for i in range(1, len(matches)):
        # Check proximity first
        if matches[i].start() - current_group[-1].end() < 200:
            # Now check if value-of expressions are identical
            current_valueof = current_group[0].group(3) if len(current_group[0].groups()) >= 3 else "."
            new_valueof = matches[i].group(3) if len(matches[i].groups()) >= 3 else "."
            
            # Check if there are structural elements between matches
            between_start = current_group[-1].end()
            between_end = matches[i].start()
            between_content = template_text[between_start:between_end]
            
            # Look for structural tags (non-xsl tags) between matches
            structural_pattern = r'<(?!/?xsl:|/?\s*xsl:)[^>]+>'
            has_structural_tags = bool(re.search(structural_pattern, between_content))
            
            if current_valueof == new_valueof and not has_structural_tags:
                current_group.append(matches[i])
                print(f"Grouped attribute with same value-of: {current_valueof}")
            else:
                if len(current_group) > 1:
                    consecutive_groups.append(current_group)
                    print(f"Starting new group: value-of mismatch ({current_valueof} vs {new_valueof}) or structural barrier")
                current_group = [matches[i]]
        else:
            if len(current_group) > 1:
                consecutive_groups.append(current_group)
            current_group = [matches[i]]
    
    if len(current_group) > 1:
        consecutive_groups.append(current_group)
    
    if not consecutive_groups:
        return template_text
    
    # Process each group
    result = template_text
    offset = 0
    
    for group in consecutive_groups:
        # Extract the base selector from the first match
        first_select = group[0].group(group_for_full_select)  # e.g., "ns0:VehRentalCore/@PickUpDateTime"
        base_match = re.match(r'(.*)/@\w+$', first_select)
        if base_match:
            base_selector = base_match.group(1) + "/@"  # e.g., "ns0:VehRentalCore/@"
        else:
            base_selector = "@"  # fallback
        
        # Extract attribute names
        attr_names = [match.group(group_for_attr) for match in group]
        
        # Create merged for-each
        select_expr = ' | '.join(f'{base_selector}{attr}' for attr in attr_names)
        merged_for_each = f'''<xsl:for-each select="{select_expr}">
                                                                <xsl:attribute name="{{name()}}" namespace="">
                                                                        <xsl:value-of select="."/>
                                                                </xsl:attribute>
                                                        </xsl:for-each>'''
        
        # Replace the entire group
        start_pos = group[0].start() + offset
        end_pos = group[-1].end() + offset
        
        # If placeholder parameters provided, create placeholder
        if placeholder_map is not None and placeholder_counter is not None:
            placeholder = f"<simpletag{placeholder_counter[0]}/>"
            placeholder_map[placeholder] = merged_for_each
            placeholder_counter[0] += 1
            replacement = placeholder
        else:
            replacement = merged_for_each
        
        result = result[:start_pos] + replacement + result[end_pos:]
        offset += len(replacement) - (end_pos - start_pos)

    return result


def _process_element_creation_patterns(template_text: str, matches):
    """Process element creation patterns like <xsl:for-each select='ns0:StreetText'><StreetText><xsl:value-of select='.'/></StreetText></xsl:for-each>."""
    import re
    
    result = template_text
    offset = 0
    
    for match in matches:
        select_expr = match.group(1)  # e.g., "ns0:StreetText" or "*[name()='ns0:StreetText']"
        element_name = match.group(2)  # e.g., "StreetText"
        
        # Check if this is a simple element copying pattern:
        # - for-each selects from source elements
        # - creates elements with same name (just without namespace)
        # - uses xsl:value-of select="." to copy content
        
        # Extract element name from select expression for validation
        if "name()=" in select_expr:
            # Handle complex XPath like "*[name()='ns0:StreetText']"
            name_match = re.search(r"name\(\)='[^:]*:?([^']+)'", select_expr)
            if name_match:
                select_element = name_match.group(1)  # Extract "StreetText" from "ns0:StreetText"
            else:
                select_element = ""
        else:
            # Handle simple XPath like "ns0:StreetText"
            select_element = select_expr.split(':')[-1] if ':' in select_expr else select_expr
        
        # Only optimize if element names match (ignoring namespace prefixes)
        if select_element == element_name:
            # This is a simple copy pattern - optimize to copy-of
            optimized = f'<xsl:copy-of select="{select_expr}"/>'
            print(f"Optimizing element pattern: {select_expr} -> copy-of")
        else:
            # Different element names - keep as for-each but remove unnecessary variable
            # Remove the variable declaration if present
            original_match = match.group(0)
            if 'xsl:variable' in original_match:
                # Remove variable and clean up
                optimized = re.sub(
                    r'<xsl:variable[^>]*name="var\d+_cur"[^>]*select="\."[^>]*(?:/>|></xsl:variable>)\s*',
                    '',
                    original_match
                )
                print(f"Removing unnecessary variable from element pattern: {element_name}")
            else:
                optimized = original_match
        
        # Replace in result
        start_pos = match.start() + offset
        end_pos = match.end() + offset
        
        result = result[:start_pos] + optimized + result[end_pos:]
        offset += len(optimized) - (end_pos - start_pos)
    
    return result


def _process_element_creation_patterns_safe(current_result: str, matches_from_original: list, original_text: str):
    """Process element creation patterns where matches were found on original text but need to be applied to current result."""
    import re
    
    # For each match found on original text, try to find the same pattern in current result
    for match in matches_from_original:
        select_expr = match.group(1)  # e.g., "ns0:StreetText" or "*[name()='ns0:StreetText']"
        element_name = match.group(2)  # e.g., "StreetText"
        
        # Re-search for the pattern in current result using flexible matching
        element_pattern = r'<xsl:for-each\s+select="' + re.escape(select_expr) + r'"[^>]*>\s*(?:\s*<xsl:variable[^>]*name="var\d+_cur"[^>]*select="\."[^>]*(?:/>|></xsl:variable>)\s*)?<' + re.escape(element_name) + r'[^>]*>\s*<xsl:value-of\s+select="\."[^>]*/?>\s*</' + re.escape(element_name) + r'>\s*</xsl:for-each>'
        
        pattern_match = re.search(element_pattern, current_result, re.DOTALL)
        if pattern_match:
            # Pattern found in current result - we can optimize it
            current_pattern = pattern_match.group(0)
            
            # Extract element name from select expression for validation
            if "name()=" in select_expr:
                # Handle complex XPath like "*[name()='ns0:StreetText']"
                name_match = re.search(r"name\(\)='[^:]*:?([^']+)'", select_expr)
                if name_match:
                    select_element = name_match.group(1)  # Extract "StreetText" from "ns0:StreetText"
                else:
                    select_element = ""
            else:
                # Handle simple XPath like "ns0:StreetText"
                select_element = select_expr.split(':')[-1] if ':' in select_expr else select_expr
            
            # Only optimize if element names match (ignoring namespace prefixes)
            if select_element == element_name:
                # This is a simple copy pattern - optimize to copy-of
                optimized = f'<xsl:copy-of select="{select_expr}"/>'
                print(f"Optimizing element pattern: {select_expr} -> copy-of")
            else:
                # Different element names - keep as for-each but remove unnecessary variable
                if 'xsl:variable' in current_pattern:
                    # Remove variable and clean up
                    optimized = re.sub(
                        r'<xsl:variable[^>]*name="var\d+_cur"[^>]*select="\."[^>]*(?:/>|></xsl:variable>)\s*',
                        '',
                        current_pattern
                    )
                    print(f"Removing unnecessary variable from element pattern: {element_name}")
                else:
                    optimized = current_pattern
            
            # Replace in current result
            current_result = current_result.replace(current_pattern, optimized)
        else:
            # Pattern was already modified by earlier processing - skip it
            print(f"Skipping element pattern (not found in current result): {select_expr}")
    
    return current_result


def _process_direct_attribute_patterns(template_text: str, matches):
    """Process direct attribute copy patterns like <xsl:attribute name='Type'><xsl:value-of select='@Type'/></xsl:attribute>."""
    result = template_text
    offset = 0
    
    for match in matches:
        attr_name = match.group(1)  # e.g., "Type"
        original_pattern = match.group(0)
        
        # Convert to copy-of
        optimized = f'<xsl:copy-of select="@{attr_name}"/>'
        print(f"Optimizing direct attribute copy: @{attr_name} -> copy-of")
        
        # Replace in result
        start_pos = match.start() + offset
        end_pos = match.end() + offset
        
        result = result[:start_pos] + optimized + result[end_pos:]
        offset += len(optimized) - (end_pos - start_pos)
    
    return result


def _process_simple_element_patterns(template_text: str, matches):
    """Process simple element copy patterns like <ContactInfo><xsl:value-of select='path/ContactInfo'/></ContactInfo>."""
    result = template_text
    offset = 0
    
    for match in matches:
        element_name = match.group(1)  # e.g., "ContactInfo"
        select_path = match.group(2)   # e.g., "ns0:ContactInfo" or "path/ContactInfo"
        original_pattern = match.group(0)
        
        # Convert to copy-of
        optimized = f'<xsl:copy-of select="{select_path}"/>'
        print(f"Optimizing simple element copy: {element_name} -> copy-of")
        
        # Replace in result
        start_pos = match.start() + offset
        end_pos = match.end() + offset
        
        result = result[:start_pos] + optimized + result[end_pos:]
        offset += len(optimized) - (end_pos - start_pos)
    
    return result

def _process_flexible_matches(template_text: str, matches):
    """Process matches with flexible pattern where select and attribute names might differ."""
    import re
    
    # Group matches by their base selector path
    groups_by_base = {}
    
    for match in matches:
        select_expr = match.group(1)  # Full select expression like "ns0:VehRentalCore/@PickUpDateTime"
        attr_name = match.group(2)    # Attribute name like "PickUpDateTime"
        
        # Extract base path (everything before the last /@)
        base_match = re.match(r'(.*)/@\w+$', select_expr)
        if base_match:
            base_path = base_match.group(1)  # e.g., "ns0:VehRentalCore"
        else:
            base_path = ""  # Direct attribute reference
        
        if base_path not in groups_by_base:
            groups_by_base[base_path] = []
        
        groups_by_base[base_path].append({
            'match': match,
            'select': select_expr,
            'attr': attr_name
        })
    
    # Process each group
    result = template_text
    offset = 0
    
    for base_path, group in groups_by_base.items():
        if len(group) < 2:
            continue  # Need at least 2 to merge
        
        # Check if matches are consecutive, but avoid consuming element patterns
        group.sort(key=lambda x: x['match'].start())
        consecutive_groups = []
        current_group = [group[0]]
        
        for i in range(1, len(group)):
            distance = group[i]['match'].start() - current_group[-1]['match'].end()
            if distance < 200:
                # Check if there are any element patterns between these matches (same logic as simple processing)
                between_start = current_group[-1]['match'].end()
                between_end = group[i]['match'].start()
                between_content = template_text[between_start:between_end]
                
                # Look for element creation patterns in between
                element_pattern = r'<xsl:for-each\s+select="([^"@]+)"[^>]*>\s*(?:\s*<xsl:variable[^>]*name="var\d+_cur"[^>]*select="\."[^>]*(?:/>|></xsl:variable>)\s*)?<(\w+)[^>]*>\s*<xsl:value-of\s+select="[^"]*"[^>]*/?>\s*</\2>\s*</xsl:for-each>'
                
                if re.search(element_pattern, between_content, re.DOTALL):
                    # Element pattern found between - start new group
                    if len(current_group) > 1:
                        consecutive_groups.append(current_group)
                    current_group = [group[i]]
                    print(f"Breaking flexible consecutive group due to element pattern between attribute matches")
                else:
                    # No element patterns - safe to group
                    current_group.append(group[i])
            else:
                if len(current_group) > 1:
                    consecutive_groups.append(current_group)
                current_group = [group[i]]
        
        if len(current_group) > 1:
            consecutive_groups.append(current_group)
        
        # Process consecutive groups
        for cons_group in consecutive_groups:
            # Create merged for-each
            if base_path:
                select_expr = ' | '.join(f'{base_path}/@{item["attr"]}' for item in cons_group)
            else:
                select_expr = ' | '.join(f'@{item["attr"]}' for item in cons_group)
            
            merged_for_each = f'''<xsl:for-each select="{select_expr}">
                                                                <xsl:attribute name="{{name()}}" namespace="">
                                                                        <xsl:value-of select="."/>
                                                                </xsl:attribute>
                                                        </xsl:for-each>'''
            
            # Replace the entire group
            start_pos = cons_group[0]['match'].start() + offset
            end_pos = cons_group[-1]['match'].end() + offset
            
            result = result[:start_pos] + merged_for_each + result[end_pos:]
            offset += len(merged_for_each) - (end_pos - start_pos)
    
    return result


# ---------------------------------------------------------------------------
# Additional Rule-Based Optimizations
# ---------------------------------------------------------------------------

def _optimize_direct_attribute_copy(elem: etree._Element, placeholder_map=None, placeholder_counter=None) -> bool:
    """
    Convert direct attribute copying patterns to xsl:copy-of.
    
    Pattern: <xsl:attribute name="Type" namespace=""><xsl:value-of select="@Type"/></xsl:attribute>
    Optimized: <xsl:copy-of select="@Type"/>
    """
    changed = False
    
    # Find all attribute elements with direct attribute copying
    attr_elements = elem.xpath(
        ".//xsl:attribute[xsl:value-of]", 
        namespaces=NSMAP
    )
    
    for attr_elem in attr_elements:
        attr_name = attr_elem.get("name")
        if not attr_name:
            continue
            
        # Check if it has a single xsl:value-of child with matching @attribute
        value_of_elems = attr_elem.xpath("./xsl:value-of", namespaces=NSMAP)
        if len(value_of_elems) == 1:
            select_expr = value_of_elems[0].get("select", "")
            
            # Check if it's a direct attribute reference: @AttrName
            if select_expr == f"@{attr_name}":
                print(f"Optimizing direct attribute copy: @{attr_name} -> copy-of")
                
                # Create optimized version
                optimized_content = f'<xsl:copy-of select="{select_expr}"/>'
                
                # If placeholder parameters provided, create placeholder
                if placeholder_map is not None and placeholder_counter is not None:
                    placeholder = f"<simpletag{placeholder_counter[0]}/>"
                    placeholder_map[placeholder] = optimized_content
                    placeholder_counter[0] += 1
                    
                    # Replace original with placeholder
                    placeholder_elem = etree.Element("placeholder")
                    placeholder_elem.tag = placeholder.replace('<', '').replace('/>', '').replace('>', '')
                    
                    parent = attr_elem.getparent()
                    if parent is not None:
                        parent.replace(attr_elem, placeholder_elem)
                        changed = True
                else:
                    # No placeholders - direct replacement
                    copy_of_elem = etree.Element("{http://www.w3.org/1999/XSL/Transform}copy-of")
                    copy_of_elem.set("select", select_expr)
                    
                    parent = attr_elem.getparent()
                    if parent is not None:
                        parent.replace(attr_elem, copy_of_elem)
                        changed = True
    
    return changed


def _optimize_conditional_attribute_to_copy_of(elem: etree._Element, placeholder_map=None, placeholder_counter=None) -> bool:
    """
    Convert conditional attribute patterns to xsl:copy-of.
    
    Pattern: <xsl:for-each select="@Language">
                <xsl:attribute name="Language" namespace="">
                    <xsl:value-of select="."/>
                </xsl:attribute>
             </xsl:for-each>
    Optimized: <xsl:copy-of select="@Language"/>
    """
    changed = False
    
    # Find for-each elements that select attributes
    for_each_elements = elem.xpath(
        ".//xsl:for-each[starts-with(@select, '@')]", 
        namespaces=NSMAP
    )
    
    for for_each_elem in for_each_elements:
        select_attr = for_each_elem.get("select", "")
        
        # Extract attribute name from select (e.g., "@Language" -> "Language")
        if select_attr.startswith("@"):
            attr_name = select_attr[1:]
            
            # Check if it has a single xsl:attribute child with matching name
            attr_children = for_each_elem.xpath("./xsl:attribute", namespaces=NSMAP)
            if len(attr_children) == 1:
                attr_elem = attr_children[0]
                attr_elem_name = attr_elem.get("name")
                
                if attr_elem_name == attr_name:
                    # Check if attribute has single xsl:value-of with select="."
                    value_of_elems = attr_elem.xpath("./xsl:value-of[@select='.']", namespaces=NSMAP)
                    if len(value_of_elems) == 1:
                        # Create xsl:copy-of
                        copy_of_elem = etree.Element("{http://www.w3.org/1999/XSL/Transform}copy-of")
                        copy_of_elem.set("select", select_attr)
                        
                        # If placeholder parameters provided, create placeholder
                        if placeholder_map is not None and placeholder_counter is not None:
                            # Store optimized content
                            optimized_content = etree.tostring(copy_of_elem, encoding="unicode")
                            placeholder = f"<simpletag{placeholder_counter[0]}/>"
                            placeholder_map[placeholder] = optimized_content
                            
                            # Create placeholder element 
                            placeholder_elem = etree.Element(f"simpletag{placeholder_counter[0]}")
                            
                            # Replace the for-each element with placeholder
                            parent = for_each_elem.getparent()
                            if parent is not None:
                                parent.replace(for_each_elem, placeholder_elem)
                                changed = True
                                placeholder_counter[0] += 1
                        else:
                            # Original behavior - replace with copy-of directly
                            parent = for_each_elem.getparent()
                            if parent is not None:
                                parent.replace(for_each_elem, copy_of_elem)
                                changed = True
    
    return changed


def _optimize_multiple_copy_of_merge(elem: etree._Element, placeholder_map=None, placeholder_counter=None) -> bool:
    """
    Merge multiple consecutive xsl:copy-of elements into a single union.
    
    Pattern: <xsl:copy-of select="@Type"/>
             <xsl:copy-of select="@Language"/>
             <xsl:copy-of select="@Status"/>
    Optimized: <xsl:copy-of select="@Type | @Language | @Status"/>
    """
    changed = False
    
    # Find all elements that are parents of copy-of elements
    candidate_parents = elem.xpath(".//*[xsl:copy-of]", namespaces=NSMAP)
    if elem.xpath("./xsl:copy-of", namespaces=NSMAP):
        candidate_parents.append(elem)
    
    for parent in set(candidate_parents):
        # Get all children, filtering out whitespace-only text nodes
        children = [c for c in parent if not (not hasattr(c, 'tag') and str(c).isspace())]
        
        i = 0
        while i < len(children):
            # Find consecutive copy-of elements
            copy_of_group = []
            j = i
            
            while j < len(children):
                child = children[j]
                if (isinstance(child.tag, str) and 
                    etree.QName(child).localname == "copy-of" and
                    etree.QName(child).namespace == "http://www.w3.org/1999/XSL/Transform"):
                    
                    select_expr = child.get("select", "")
                    # Only merge attribute selectors for now
                    if select_expr.startswith("@"):
                        copy_of_group.append(child)
                        j += 1
                    else:
                        break
                else:
                    break
            
            # If we found 2 or more consecutive copy-of elements, merge them
            if len(copy_of_group) >= 2:
                # Create merged copy-of element
                select_exprs = [elem.get("select", "") for elem in copy_of_group]
                merged_select = " | ".join(select_exprs)
                
                merged_copy_of = etree.Element("{http://www.w3.org/1999/XSL/Transform}copy-of")
                merged_copy_of.set("select", merged_select)
                
                # If placeholder parameters provided, create placeholder
                if placeholder_map is not None and placeholder_counter is not None:
                    # Store optimized content
                    optimized_content = etree.tostring(merged_copy_of, encoding="unicode")
                    placeholder = f"<simpletag{placeholder_counter[0]}/>"
                    placeholder_map[placeholder] = optimized_content
                    
                    # Create placeholder element 
                    placeholder_elem = etree.Element(f"simpletag{placeholder_counter[0]}")
                    
                    # Replace the first copy-of element with placeholder
                    parent.replace(copy_of_group[0], placeholder_elem)
                    placeholder_counter[0] += 1
                else:
                    # Original behavior - replace with merged copy-of directly
                    parent.replace(copy_of_group[0], merged_copy_of)
                
                # Remove the rest
                for copy_of_elem in copy_of_group[1:]:
                    parent.remove(copy_of_elem)
                
                changed = True
                
                # Update children list after modification
                children = [c for c in parent if not (not hasattr(c, 'tag') and str(c).isspace())]
                i = 0  # Restart scanning from beginning
            else:
                i = j if j > i else i + 1
    
    return changed


def _optimize_simple_element_copy(elem: etree._Element, placeholder_map=None, placeholder_counter=None) -> bool:
    """
    Optimize simple element copying patterns.
    
    Pattern: <xsl:for-each select="ns0:Success">
                <Success/>
             </xsl:for-each>
    Optimized: <xsl:copy-of select="ns0:Success"/>
    """
    changed = False
    
    # Find for-each elements
    for_each_elements = elem.xpath(".//xsl:for-each", namespaces=NSMAP)
    
    for for_each_elem in for_each_elements:
        select_expr = for_each_elem.get("select", "")
        
        # Check if for-each has a single child element
        child_elements = [c for c in for_each_elem if isinstance(c.tag, str)]
        if len(child_elements) == 1:
            child_elem = child_elements[0]
            
            # Check if it's a simple empty element (self-closing)
            if (len(child_elem) == 0 and 
                (child_elem.text is None or child_elem.text.strip() == "")):
                
                # Extract element name from select expression
                # Handle patterns like "ns0:Success" -> "Success"
                if ":" in select_expr:
                    expected_name = select_expr.split(":")[-1]
                else:
                    expected_name = select_expr
                
                # Check if child element name matches
                child_name = etree.QName(child_elem).localname
                if child_name == expected_name:
                    # Replace with xsl:copy-of
                    copy_of_elem = etree.Element("{http://www.w3.org/1999/XSL/Transform}copy-of")
                    copy_of_elem.set("select", select_expr)
                    
                    # If placeholder parameters provided, create placeholder
                    if placeholder_map is not None and placeholder_counter is not None:
                        # Store optimized content
                        optimized_content = etree.tostring(copy_of_elem, encoding="unicode")
                        placeholder = f"<simpletag{placeholder_counter[0]}/>"
                        placeholder_map[placeholder] = optimized_content
                        
                        # Create placeholder element 
                        placeholder_elem = etree.Element(f"simpletag{placeholder_counter[0]}")
                        
                        # Replace the for-each element with placeholder
                        parent = for_each_elem.getparent()
                        if parent is not None:
                            parent.replace(for_each_elem, placeholder_elem)
                            changed = True
                            placeholder_counter[0] += 1
                    else:
                        # Original behavior - replace with copy-of directly
                        parent = for_each_elem.getparent()
                        if parent is not None:
                            parent.replace(for_each_elem, copy_of_elem)
                            changed = True
    
    return changed


def _optimize_trivial_for_each_elimination(elem: etree._Element, placeholder_map=None, placeholder_counter=None) -> bool:
    """
    Eliminate trivial for-each loops that can be simplified.
    
    Pattern: <xsl:for-each select="ns0:Element">
                <Element><xsl:value-of select="."/></Element>
             </xsl:for-each>
    Optimized: <xsl:copy-of select="ns0:Element"/>
    """
    changed = False
    
    # Find for-each elements
    for_each_elements = elem.xpath(".//xsl:for-each", namespaces=NSMAP)
    
    for for_each_elem in for_each_elements:
        select_expr = for_each_elem.get("select", "")
        
        # Check if for-each has a single child element
        child_elements = [c for c in for_each_elem if isinstance(c.tag, str)]
        if len(child_elements) == 1:
            child_elem = child_elements[0]
            
            # Check if child element has single xsl:value-of with select="."
            value_of_elems = child_elem.xpath("./xsl:value-of[@select='.']", namespaces=NSMAP)
            if (len(value_of_elems) == 1 and 
                len([c for c in child_elem if isinstance(c.tag, str)]) == 1):
                
                # Extract element name from select expression
                if ":" in select_expr:
                    expected_name = select_expr.split(":")[-1]
                else:
                    expected_name = select_expr
                
                # Check if child element name matches
                child_name = etree.QName(child_elem).localname
                if child_name == expected_name:
                    # Replace with xsl:copy-of
                    copy_of_elem = etree.Element("{http://www.w3.org/1999/XSL/Transform}copy-of")
                    copy_of_elem.set("select", select_expr)
                    
                    # If placeholder parameters provided, create placeholder
                    if placeholder_map is not None and placeholder_counter is not None:
                        # Store optimized content
                        optimized_content = etree.tostring(copy_of_elem, encoding="unicode")
                        placeholder = f"<simpletag{placeholder_counter[0]}/>"
                        placeholder_map[placeholder] = optimized_content
                        
                        # Create placeholder element 
                        placeholder_elem = etree.Element(f"simpletag{placeholder_counter[0]}")
                        
                        # Replace the for-each element with placeholder
                        parent = for_each_elem.getparent()
                        if parent is not None:
                            parent.replace(for_each_elem, placeholder_elem)
                            changed = True
                            placeholder_counter[0] += 1
                    else:
                        # Original behavior - replace with copy-of directly
                        parent = for_each_elem.getparent()
                        if parent is not None:
                            parent.replace(for_each_elem, copy_of_elem)
                            changed = True
    
    return changed


def _optimize_boolean_type_conversion(elem: etree._Element, placeholder_map=None, placeholder_counter=None) -> bool:
    """
    Standardize boolean type conversion patterns.
    
    Pattern: <xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
    Optimized: <xsl:value-of select="boolean(.)"/>
    """
    changed = False
    
    # Find xsl:value-of elements with boolean conversion
    value_of_elements = elem.xpath(".//xsl:value-of", namespaces=NSMAP)
    
    for value_of_elem in value_of_elements:
        select_expr = value_of_elem.get("select", "")
        
        # Check for the specific boolean conversion pattern
        if "boolean(translate(normalize-space(string(.))," in select_expr:
            # Replace with simplified boolean conversion
            value_of_elem.set("select", "boolean(.)")
            changed = True
    
    return changed


def _optimize_complex_boolean_patterns(elem: etree._Element, placeholder_map=None, placeholder_counter=None) -> bool:
    """
    Rule 8: Complex Boolean Pattern Optimization
    
    Simplify overly complex boolean test patterns.
    
    Pattern 1: boolean(translate(normalize-space($var), ' 0', ''))
    Pattern 2: number(boolean(...))
    """
    changed = False
    
    # Pattern 1: Simplify boolean(translate(normalize-space(...), ' 0', '')) in if tests
    if_elements = elem.xpath(".//xsl:if[contains(@test, 'boolean(translate(normalize-space(')]", namespaces=NSMAP)
    
    for if_elem in if_elements:
        test_expr = if_elem.get("test", "")
        
        # Simple pattern: boolean(translate(normalize-space($var), ' 0', ''))
        if "', ' 0', ''))" in test_expr:
            import re
            # Extract the variable reference
            match = re.search(r'boolean\(translate\(normalize-space\(([^)]+)\)', test_expr)
            if match:
                var_ref = match.group(1)
                # Simplify to direct variable test
                if_elem.set("test", f"{var_ref} and {var_ref} != '0'")
                changed = True
    
    # Pattern 2: Optimize number(boolean(...)) patterns in value-of
    value_of_elements = elem.xpath(".//xsl:value-of[contains(@select, 'number(boolean(')]", namespaces=NSMAP)
    
    for value_of_elem in value_of_elements:
        select_expr = value_of_elem.get("select", "")
        
        # Pattern: number(boolean(translate(...)))
        if "number(boolean(translate(" in select_expr and "'false0 '" in select_expr:
            import re
            # Extract the inner expression
            match = re.search(r'number\(boolean\(translate\(([^,]+),', select_expr)
            if match:
                inner_expr = match.group(1)
                # Convert to if-then-else
                value_of_elem.set("select", f"if ({inner_expr} and {inner_expr} != '0' and {inner_expr} != 'false') then 1 else 0")
                changed = True
    
    return changed


def rule_based_refine(template_text: str) -> Tuple[str, List[Dict[str, Any]], Dict[str, str]]:
    """Attempt deterministic refinement with per-rule placeholders. Returns (text_with_placeholders, actions, placeholder_map)."""
    wrapper_used = False
    placeholder_map = {}
    placeholder_counter = [1]  # Use list to pass by reference
    try:
        elem = etree.fromstring(template_text.encode())
    except Exception:
        # Attempt to parse fragment by wrapping inside a dummy element that declares common namespaces.
        wrapper_used = True
        wrapped = (
            f"<dummy xmlns:xsl='{XSLT_NS}' "
            f"xmlns:ns0='http://www.opentravel.org/OTA/2003/05' "
            f"xmlns:tbf='http://www.altova.com/MapForce/UDF/tbf' "
            f"xmlns:xs='http://www.w3.org/2001/XMLSchema'>"
            f"{template_text}"
            "</dummy>"
        )
        try:
            elem = etree.fromstring(wrapped.encode())
        except Exception as e:
            print("Cannot parse template text even after wrapping")
            # Try one more time with a more aggressive approach
            try:
                # If the fragment starts with incomplete XML, try to fix it
                if template_text.strip().startswith('<'):
                    # It's an XML fragment, try to make it parseable
                    simple_wrapped = f"<fragment>{template_text}</fragment>"
                    elem = etree.fromstring(simple_wrapped.encode())
                    wrapper_used = True
                else:
                    # It's text content, skip rule-based processing
                    return template_text, [], {}
            except Exception:
                print("Final fallback: Cannot parse template text, skipping tree-based processing")
                # Try text-based for-each merging as a last resort
                text_merged, text_placeholder_map = _text_based_for_each_merge_with_placeholders(template_text, placeholder_counter)
                if text_merged != template_text:
                    print("Applied text-based for-each merging")
                    return text_merged, [{"op": "text_based_merge"}], text_placeholder_map
                return template_text, [], {}

    changed = False
    actions: List[Dict[str, Any]] = []

    # 1. remove variable
    if _remove_var_cur(elem):
        print("remove_var_cur applied")
        changed = True
        actions.append({"op": "remove_var_cur"})

    # 2. optimize direct attribute copying  
    if _optimize_direct_attribute_copy(elem, placeholder_map, placeholder_counter):
        print("direct_attribute_copy applied")
        changed = True
        actions.append({"op": "direct_attribute_copy"})

    # 3. optimize conditional attributes to copy-of
    if _optimize_conditional_attribute_to_copy_of(elem, placeholder_map, placeholder_counter):
        print("conditional_attribute_to_copy_of applied")
        changed = True
        actions.append({"op": "conditional_attribute_to_copy_of"})

    # 4. optimize simple element copying
    if _optimize_simple_element_copy(elem, placeholder_map, placeholder_counter):
        print("simple_element_copy applied")
        changed = True
        actions.append({"op": "simple_element_copy"})

    # 5. optimize trivial for-each elimination
    if _optimize_trivial_for_each_elimination(elem, placeholder_map, placeholder_counter):
        print("trivial_for_each_elimination applied")
        changed = True
        actions.append({"op": "trivial_for_each_elimination"})

    # 6. optimize boolean type conversion
    if _optimize_boolean_type_conversion(elem, placeholder_map, placeholder_counter):
        print("boolean_type_conversion applied")
        changed = True
        actions.append({"op": "boolean_type_conversion"})

    # 7. merge simple loops
    merged, attr_list, pure_block = _merge_simple_attr_loops(elem, placeholder_map, placeholder_counter)
    if merged:
        changed = True
        op_name = "merge_attr_loops" if pure_block else "merge_attr_loops_partial"
        actions.append({"op": op_name, "attrs": attr_list})

    # 8. merge multiple copy-of elements
    if _optimize_multiple_copy_of_merge(elem, placeholder_map, placeholder_counter):
        print("multiple_copy_of_merge applied")
        changed = True
        actions.append({"op": "multiple_copy_of_merge"})

    # 9. collapse nested loops (simple implementation)
    if _collapse_nested_loops(elem, placeholder_map, placeholder_counter):
        changed = True
        actions.append({"op": "collapse_nested_loops"})

    # 10. optimize complex boolean patterns (Rule 8)
    if _optimize_complex_boolean_patterns(elem, placeholder_map, placeholder_counter):
        print("complex_boolean_patterns applied")
        changed = True
        actions.append({"op": "complex_boolean_patterns"})

    if not changed:
        return template_text, actions, {}

    # Generate the text with placeholders
    if wrapper_used:
        # Strip the dummy wrapper and serialize only its children
        refined_parts = [
            etree.tostring(child, encoding="unicode", pretty_print=True)
            for child in elem
        ]
        text_with_placeholders = "".join(refined_parts)
    else:
        text_with_placeholders = etree.tostring(elem, encoding="unicode", pretty_print=True)

    return text_with_placeholders, actions, placeholder_map


def _text_based_for_each_merge_with_placeholders(template_text: str, placeholder_counter) -> Tuple[str, Dict[str, str]]:
    """Apply text-based for-each merging and create placeholders for ALL patterns.
    
    This function handles 6 different XSLT optimization patterns:
    1. Simple attribute merging: @Status + @Type -> union selector
    2. Complex attribute merging: ns0:Element/@attr1 + ns0:Element/@attr2 -> union selector  
    3. Flexible attribute merging: catch-all for remaining attribute patterns
    4. Element creation optimization: for-each with element creation -> copy-of
    5. Direct attribute copy: attribute with value-of @attr -> copy-of
    6. Simple element copy: element with value-of select -> copy-of
    
    Each optimization creates individual placeholders for granular LLM integration.
    """
    import re
    
    placeholder_map = {}
    result = template_text
    
    # 1. Process simple attribute patterns (@AttrName) - merge consecutive simple attribute loops
    # Pattern: <xsl:for-each select="@Status"><xsl:attribute name="Status"><xsl:value-of select="."/></xsl:attribute></xsl:for-each>
    # Optimized: <xsl:for-each select="@Status | @Language | @Type"><xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute></xsl:for-each>
    simple_attr_pattern = r'<xsl:for-each\s+select="@(\w+)"[^>]*>\s*(?:\s*<xsl:variable[^>]*(?:/>|>[^<]*</xsl:variable>)\s*)?<xsl:attribute\s+name="\1"[^>]*>\s*<xsl:value-of\s+select="\."[^>]*/?>\s*</xsl:attribute>\s*</xsl:for-each>'
    simple_matches = list(re.finditer(simple_attr_pattern, result, re.DOTALL))
    
    if len(simple_matches) >= 2:
        result = _process_matches_with_base_selector(result, simple_matches, "@", extract_attr_from_group=1, placeholder_map=placeholder_map, placeholder_counter=placeholder_counter)
        print("Applied simple pattern merging")
    
    # 2. Process complex attribute patterns (ns0:Element/@AttrName) - merge namespaced attribute loops
    # Pattern: <xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime"><xsl:attribute name="PickUpDateTime"><xsl:value-of select="."/></xsl:attribute></xsl:for-each>
    # Optimized: <xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime | ns0:VehRentalCore/@ReturnDateTime"><xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute></xsl:for-each>
    complex_attr_pattern = r'<xsl:for-each\s+select="([^"]*[^@]/@(\w+))"[^>]*>\s*(?:\s*<xsl:variable[^>]*(?:/>|>[^<]*</xsl:variable>)\s*)?<xsl:attribute\s+name="\2"[^>]*>\s*<xsl:value-of\s+select="([^"]*)"[^>]*/?>\s*</xsl:attribute>\s*</xsl:for-each>'
    complex_matches = list(re.finditer(complex_attr_pattern, result, re.DOTALL))
    
    if len(complex_matches) >= 2:
        result = _process_matches_with_dynamic_selector(result, complex_matches, group_for_full_select=1, group_for_attr=2, placeholder_map=placeholder_map, placeholder_counter=placeholder_counter)
        print("Applied complex pattern merging with value-of grouping")
    
    # 3. Process flexible attribute patterns (catch-all) - merge remaining attribute patterns
    # Pattern: <xsl:for-each select="complex/@attr"><xsl:attribute name="attr"><xsl:value-of select="."/></xsl:attribute></xsl:for-each>
    # Optimized: <xsl:for-each select="complex/@attr1 | complex/@attr2"><xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute></xsl:for-each>
    flexible_pattern = r'<xsl:for-each\s+select="([^"]*@\w+)"[^>]*>\s*(?:\s*<xsl:variable[^>]*(?:/>|>[^<]*</xsl:variable>)\s*)?<xsl:attribute\s+name="(\w+)"[^>]*>\s*<xsl:value-of\s+select="\."[^>]*/?>\s*</xsl:attribute>\s*</xsl:for-each>'
    flexible_matches = list(re.finditer(flexible_pattern, result, re.DOTALL))
    
    if len(flexible_matches) >= 2:
        result = _process_matches_with_dynamic_selector(result, flexible_matches, group_for_full_select=1, group_for_attr=2, placeholder_map=placeholder_map, placeholder_counter=placeholder_counter)
        print("Applied flexible pattern merging")
    
    # 4. Process element creation patterns - optimize simple element copying
    # Pattern: <xsl:for-each select="ns0:Success"><Success><xsl:value-of select="."/></Success></xsl:for-each>
    # Optimized: <xsl:copy-of select="ns0:Success"/>
    element_pattern = r'<xsl:for-each\s+select="([^"]+)"[^>]*>\s*(?:\s*<xsl:variable[^>]*name="var\d+_cur"[^>]*select="\."[^>]*(?:/>|></xsl:variable>)\s*)?<(\w+)[^>]*>\s*<xsl:value-of\s+select="\."[^>]*/?>\s*</\2>\s*</xsl:for-each>'
    element_matches = list(re.finditer(element_pattern, template_text, re.DOTALL))
    
    if len(element_matches) >= 1:
        # Process each element match individually with placeholders
        current_result = result
        for match in element_matches:
            original_pattern = match.group(0)
            # Apply optimization to just this pattern
            temp_text = _process_element_creation_patterns_safe(original_pattern, [match], template_text)
            if temp_text != original_pattern:
                placeholder = f"<simpletag{placeholder_counter[0]}/>"
                placeholder_map[placeholder] = temp_text
                placeholder_counter[0] += 1
                current_result = current_result.replace(original_pattern, placeholder, 1)
        if current_result != result:
            result = current_result
            print("Applied element creation pattern optimization")
    
    # 5. Process direct attribute copy patterns - convert attribute patterns to copy-of
    # Pattern: <xsl:attribute name="Type"><xsl:value-of select="@Type"/></xsl:attribute>
    # Optimized: <xsl:copy-of select="@Type"/>
    direct_attr_pattern = r'<xsl:attribute\s+name="(\w+)"[^>]*>\s*<xsl:value-of\s+select="@\1"[^>]*/?>\s*</xsl:attribute>'
    direct_attr_matches = list(re.finditer(direct_attr_pattern, result, re.DOTALL))
    
    if len(direct_attr_matches) >= 1:
        # Process each direct attribute match individually with placeholders
        current_result = result
        for match in direct_attr_matches:
            original_pattern = match.group(0)
            attr_name = match.group(1)
            
            # Create optimized version directly
            optimized_content = f'<xsl:copy-of select="@{attr_name}"/>'
            print(f"Optimizing direct attribute copy: @{attr_name} -> copy-of")
            
            if optimized_content != original_pattern:
                placeholder = f"<simpletag{placeholder_counter[0]}/>"
                placeholder_map[placeholder] = optimized_content
                placeholder_counter[0] += 1
                current_result = current_result.replace(original_pattern, placeholder, 1)
        if current_result != result:
            result = current_result
            print("Applied direct attribute copy optimization")
            print("placeholder inside direct attribute copy optimization", placeholder_map)
    
    # 6. Process simple element copy patterns - convert element value copying to copy-of
    # Pattern: <ContactInfo><xsl:value-of select="ns0:ContactInfo"/></ContactInfo>
    # Optimized: <xsl:copy-of select="ns0:ContactInfo"/>
    simple_element_pattern = r'<(\w+)[^>]*>\s*<xsl:value-of\s+select="([^"]*\1)"[^>]*/?>\s*</\1>'
    simple_element_matches = list(re.finditer(simple_element_pattern, result, re.DOTALL))
    
    if len(simple_element_matches) >= 1:
        # Process each simple element match individually with placeholders
        current_result = result
        for match in simple_element_matches:
            original_pattern = match.group(0)
            # Apply optimization to just this pattern
            temp_text = _process_simple_element_patterns(original_pattern, [match])
            if temp_text != original_pattern:
                placeholder = f"<simpletag{placeholder_counter[0]}/>"
                placeholder_map[placeholder] = temp_text
                placeholder_counter[0] += 1
                current_result = current_result.replace(original_pattern, placeholder, 1)
        if current_result != result:
            result = current_result
            print("Applied simple element copy optimization")
    
    return result, placeholder_map


def replace_placeholders(text_with_placeholders: str, placeholder_map: Dict[str, str]) -> str:
    """Replace placeholders with their optimized content."""
    import re
    result = text_with_placeholders
    print("Inside replace_placeholders")
    
    # Sort placeholders by number to ensure correct replacement order
    sorted_placeholders = sorted(placeholder_map.items(), 
                                key=lambda x: int(x[0].replace('<simpletag', '').replace('/>', ''))
                                if x[0].startswith('<simpletag') else 999)
    
    for placeholder_key, optimized_content in sorted_placeholders:
        # Extract tag name from placeholder key (e.g., "<simpletag1/>" -> "simpletag1")
        tag_name = placeholder_key.replace('<', '').replace('/>', '')
        
        # Use regex to match the placeholder element with any attributes
        pattern = rf'<{tag_name}[^>]*/?>'
        result = re.sub(pattern, optimized_content, result)
        
    return result
