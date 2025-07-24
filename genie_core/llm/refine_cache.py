"""Utility for caching XSLT template refinements based on structural fingerprint.

A "fingerprint" is a SHA-256 hash computed from the ordered list of XSLT control-structure
 tags (for-each / choose / when / otherwise / if / attribute / value-of / copy-of) that
 appear in the template.  All attributes and literal result elements are ignored so that
 templates with the same control-flow skeleton map to a single fingerprint.

The module also contains a *rule-based* refiner that performs the three hard-coded
 clean-ups requested by the user, so that repeated shapes can be refined without an LLM
 round-trip:
    1. Remove <xsl:variable name="var*_cur" select="." /> boilerplate.
    2. Merge simple attribute loops into a single xsl:copy-of (if <=10 attributes).
    3. Collapse trivial nested for-each loops into literal result elements (best-effort).

Only the first two rules are implemented deterministically; rule 3 is a noop placeholder
 that can be expanded later.  These rules are *safe* – they will skip a template if it
 detects any unexpected complexity.
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
    # Create table for learned transformations from LLM
    conn.execute(
        """CREATE TABLE IF NOT EXISTS learned_transformations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_pattern_hash TEXT NOT NULL,
                original_pattern TEXT NOT NULL,
                optimized_pattern TEXT NOT NULL,
                transformation_type TEXT NOT NULL,
                pattern_regex TEXT,
                replacement_template TEXT,
                is_rule_candidate BOOLEAN DEFAULT 1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


def store_learned_transformation(original_pattern: str, optimized_pattern: str, transformation_type: str) -> None:
    """Store a learned transformation from LLM output for potential rule creation."""
    import hashlib
    
    original_hash = hashlib.md5(original_pattern.encode()).hexdigest()
    
    # Don't store if we already have this exact transformation
    with _get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM learned_transformations WHERE original_pattern_hash = ?",
            (original_hash,)
        ).fetchone()
        
        if existing:
            return  # Already stored
        
        # Extract potential rule pattern
        pattern_regex, replacement_template = _extract_rule_pattern(original_pattern, optimized_pattern, transformation_type)
        
        conn.execute(
            """INSERT INTO learned_transformations 
               (original_pattern_hash, original_pattern, optimized_pattern, transformation_type, 
                pattern_regex, replacement_template) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (original_hash, original_pattern[:500], optimized_pattern[:500], 
             transformation_type, pattern_regex, replacement_template)
        )
        conn.commit()
        print(f"Stored learned transformation: {transformation_type}")


def get_learned_transformations() -> List[Dict[str, Any]]:
    """Get all learned transformations that could become rules."""
    with _get_conn() as conn:
        rows = conn.execute(
            """SELECT original_pattern, optimized_pattern, transformation_type, 
                      pattern_regex, replacement_template, created_date
               FROM learned_transformations 
               WHERE is_rule_candidate = 1 
               ORDER BY created_date DESC"""
        ).fetchall()
        
        return [
            {
                'original_pattern': row[0],
                'optimized_pattern': row[1], 
                'transformation_type': row[2],
                'pattern_regex': row[3],
                'replacement_template': row[4],
                'created_date': row[5]
            }
            for row in rows
        ]


def check_for_learned_pattern(pattern: str) -> Optional[str]:
    """Check if we have a learned optimization for this pattern."""
    pattern_hash = hashlib.md5(pattern.encode()).hexdigest()
    
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT optimized_pattern FROM learned_transformations WHERE original_pattern_hash = ?",
            (pattern_hash,)
        ).fetchone()
        
        return row[0] if row else None


def _extract_rule_pattern(original: str, optimized: str, transformation_type: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract regex pattern and replacement template from LLM transformation for potential rule creation."""
    
    if transformation_type == "variable_removal":
        # Look for variable removal pattern
        if 'xsl:variable' in original and 'xsl:variable' not in optimized:
            return (r'<xsl:variable\s+name="var\d+_cur"\s+select="\."\s*/>', "")
    
    elif transformation_type == "for_each_to_copy_of":
        # Look for for-each to copy-of conversion
        if 'xsl:for-each' in original and 'xsl:copy-of' in optimized:
            # Try to extract the select attribute pattern
            import re
            select_match = re.search(r'select="([^"]*@\w+)"', original)
            if select_match:
                select_attr = select_match.group(1)
                pattern = f'<xsl:for-each\\s+select="{re.escape(select_attr)}"[^>]*>.*?</xsl:for-each>'
                replacement = f'<xsl:copy-of select="{select_attr}"/>'
                return (pattern, replacement)
    
    elif transformation_type == "attribute_simplification":
        # Look for attribute simplification patterns
        if original.count('<xsl:attribute') > optimized.count('<xsl:attribute'):
            # Multiple attributes simplified - could be a pattern
            import re
            attr_pattern = r'<xsl:for-each\s+select="@(\w+)"[^>]*>\s*<xsl:attribute\s+name="\1"[^>]*>\s*<xsl:value-of\s+select="\."/>\s*</xsl:attribute>\s*</xsl:for-each>'
            if re.search(attr_pattern, original):
                return (attr_pattern, r'<xsl:copy-of select="@\1"/>')
    
    # Generic patterns - return None if we can't extract a clear rule
    return (None, None)


def print_learned_transformations_report():
    """Print a report of learned transformations for rule development."""
    transformations = get_learned_transformations()
    
    if not transformations:
        print("No learned transformations found.")
        return
    
    print(f"\n=== LEARNED TRANSFORMATIONS REPORT ===")
    print(f"Total transformations: {len(transformations)}")
    
    # Group by transformation type
    by_type = {}
    for t in transformations:
        t_type = t['transformation_type']
        if t_type not in by_type:
            by_type[t_type] = []
        by_type[t_type].append(t)
    
    for t_type, items in by_type.items():
        print(f"\n{t_type.upper()} ({len(items)} instances):")
        for i, item in enumerate(items[:3], 1):  # Show max 3 examples
            print(f"  Example {i}:")
            if item['pattern_regex']:
                print(f"    Regex: {item['pattern_regex']}")
                print(f"    Replace: {item['replacement_template']}")
            else:
                print(f"    Original (first 100 chars): {item['original_pattern'][:100]}...")
                print(f"    Optimized (first 100 chars): {item['optimized_pattern'][:100]}...")
        if len(items) > 3:
            print(f"    ... and {len(items) - 3} more")
    
    print("\n" + "=" * 50)


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


def _merge_simple_attr_loops(template: etree._Element) -> Tuple[bool, List[str], bool]:
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

                # Pattern matches, add to current block
                block_loops.append(child)
                block_attr_names.append(attr_name)
                block_prefixes.append(prefix)
                j += 1

            if len(block_loops) > 1:
                # Merge the collected block
                overall_changed = True
                all_merged_attrs.extend(block_attr_names)

                # Use the prefix from the first loop for the new select
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


def _collapse_nested_loops(template: etree._Element) -> bool:
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


def _text_based_for_each_merge(template_text: str) -> str:
    """Apply text-based for-each merging for unparseable fragments."""
    print("before template_text: ", template_text)
    import re
    
    # Look for patterns like consecutive for-each loops for attributes
    # Updated pattern to handle:
    # 1. Simple direct attributes (@attr)
    # 2. Namespace prefixes in selectors (ns0:Element/@attr)
    # 3. Variable whitespace and newlines
    # 4. Different attribute naming patterns
    # 5. Optional namespace attributes
    
    # Process ALL patterns in a single pass instead of early returns
    # This allows chunks with mixed simple and complex patterns to be fully processed
    
    result = template_text
    
    # 1. Process simple patterns first (@AttrName)
    simple_attr_pattern = r'<xsl:for-each\s+select="@(\w+)"[^>]*>\s*(?:\s*<xsl:variable[^>]*(?:/>|>[^<]*</xsl:variable>)\s*)?<xsl:attribute\s+name="\1"[^>]*>\s*<xsl:value-of\s+select="\."[^>]*/?>\s*</xsl:attribute>\s*</xsl:for-each>'
    
    simple_matches = list(re.finditer(simple_attr_pattern, result, re.DOTALL))
    
    if len(simple_matches) >= 2:
        result = _process_simple_matches(result, simple_matches)
        print("Applied simple pattern merging")
    
    # 2. Process complex patterns (ns0:Element/@AttrName) - enhanced to handle different value-of expressions
    # This pattern captures the value-of expression as well
    complex_attr_pattern = r'<xsl:for-each\s+select="([^"]*[^@]/@(\w+))"[^>]*>\s*(?:\s*<xsl:variable[^>]*(?:/>|>[^<]*</xsl:variable>)\s*)?<xsl:attribute\s+name="\2"[^>]*>\s*<xsl:value-of\s+select="([^"]*)"[^>]*/?>\s*</xsl:attribute>\s*</xsl:for-each>'
    
    complex_matches = list(re.finditer(complex_attr_pattern, result, re.DOTALL))
    
    if len(complex_matches) >= 2:
        result = _process_complex_matches_with_valueof(result, complex_matches)
        print("Applied complex pattern merging with value-of grouping")
    
    # 3. Process flexible patterns (catch-all for remaining cases)
    flexible_pattern = r'<xsl:for-each\s+select="([^"]*@\w+)"[^>]*>\s*(?:\s*<xsl:variable[^>]*(?:/>|>[^<]*</xsl:variable>)\s*)?<xsl:attribute\s+name="(\w+)"[^>]*>\s*<xsl:value-of\s+select="\."[^>]*/?>\s*</xsl:attribute>\s*</xsl:for-each>'
    
    flexible_matches = list(re.finditer(flexible_pattern, result, re.DOTALL))
    
    if len(flexible_matches) >= 2:
        result = _process_flexible_matches(result, flexible_matches)
        print("Applied flexible pattern merging")
    
    return result


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


def _process_matches_with_base_selector(template_text: str, matches, base_selector: str, extract_attr_from_group: int):
    """Helper to process matches where all have the same base selector."""
    # Group consecutive matches
    consecutive_groups = []
    current_group = [matches[0]]
    
    for i in range(1, len(matches)):
        # Check if this match is close to the previous one (within 200 chars)
        if matches[i].start() - current_group[-1].end() < 200:
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
        
        result = result[:start_pos] + merged_for_each + result[end_pos:]
        offset += len(merged_for_each) - (end_pos - start_pos)
    
    return result


def _process_matches_with_dynamic_selector(template_text: str, matches, group_for_full_select: int, group_for_attr: int):
    """Helper to process matches where we need to extract the base selector dynamically."""
    import re
    print("inside dynamic selector")
    # Group consecutive matches
    consecutive_groups = []
    current_group = [matches[0]]
    
    for i in range(1, len(matches)):
        if matches[i].start() - current_group[-1].end() < 200:
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
        
        result = result[:start_pos] + merged_for_each + result[end_pos:]
        offset += len(merged_for_each) - (end_pos - start_pos)
    print("result", result)
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
        
        # Check if matches are consecutive
        group.sort(key=lambda x: x['match'].start())
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

def _optimize_direct_attribute_copy(elem: etree._Element) -> bool:
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
                # Replace with xsl:copy-of
                copy_of_elem = etree.Element("{http://www.w3.org/1999/XSL/Transform}copy-of")
                copy_of_elem.set("select", select_expr)
                
                # Replace the attribute element with copy-of
                parent = attr_elem.getparent()
                if parent is not None:
                    parent.replace(attr_elem, copy_of_elem)
                    changed = True
    
    return changed


def _optimize_conditional_attribute_to_copy_of(elem: etree._Element) -> bool:
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
                        # Replace with xsl:copy-of
                        copy_of_elem = etree.Element("{http://www.w3.org/1999/XSL/Transform}copy-of")
                        copy_of_elem.set("select", select_attr)
                        
                        # Replace the for-each element with copy-of
                        parent = for_each_elem.getparent()
                        if parent is not None:
                            parent.replace(for_each_elem, copy_of_elem)
                            changed = True
    
    return changed


def _optimize_multiple_copy_of_merge(elem: etree._Element) -> bool:
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
                
                # Replace the first copy-of element with merged one
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


def _optimize_simple_element_copy(elem: etree._Element) -> bool:
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
                    
                    parent = for_each_elem.getparent()
                    if parent is not None:
                        parent.replace(for_each_elem, copy_of_elem)
                        changed = True
    
    return changed


def _optimize_trivial_for_each_elimination(elem: etree._Element) -> bool:
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
                    
                    parent = for_each_elem.getparent()
                    if parent is not None:
                        parent.replace(for_each_elem, copy_of_elem)
                        changed = True
    
    return changed


def _optimize_boolean_type_conversion(elem: etree._Element) -> bool:
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


def rule_based_refine(template_text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Attempt deterministic refinement. Returns (refined_text, actions)."""
    wrapper_used = False
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
            print(f"Cannot parse template text even after wrapping: {e}")
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
                    return template_text, []
            except Exception:
                print("Final fallback: Cannot parse template text, skipping rule-based processing")
                # Try text-based for-each merging as a last resort
                text_merged = _text_based_for_each_merge(template_text)
                if text_merged != template_text:
                    print("Applied text-based for-each merging")
                    return text_merged, [{"op": "text_based_merge"}]
                return template_text, []

    changed = False
    actions: List[Dict[str, Any]] = []

    # 1. remove variable
    if _remove_var_cur(elem):
        print("remove_var_cur applied")
        changed = True
        actions.append({"op": "remove_var_cur"})

    # 2. optimize direct attribute copying  
    if _optimize_direct_attribute_copy(elem):
        print("direct_attribute_copy applied")
        changed = True
        actions.append({"op": "direct_attribute_copy"})

    # 3. optimize conditional attributes to copy-of
    if _optimize_conditional_attribute_to_copy_of(elem):
        print("conditional_attribute_to_copy_of applied")
        changed = True
        actions.append({"op": "conditional_attribute_to_copy_of"})

    # 4. optimize simple element copying
    if _optimize_simple_element_copy(elem):
        print("simple_element_copy applied")
        changed = True
        actions.append({"op": "simple_element_copy"})

    # 5. optimize trivial for-each elimination
    if _optimize_trivial_for_each_elimination(elem):
        print("trivial_for_each_elimination applied")
        changed = True
        actions.append({"op": "trivial_for_each_elimination"})

    # 6. optimize boolean type conversion
    if _optimize_boolean_type_conversion(elem):
        print("boolean_type_conversion applied")
        changed = True
        actions.append({"op": "boolean_type_conversion"})

    # 7. merge simple loops
    merged, attr_list, pure_block = _merge_simple_attr_loops(elem)
    if merged:
        changed = True
        op_name = "merge_attr_loops" if pure_block else "merge_attr_loops_partial"
        actions.append({"op": op_name, "attrs": attr_list})

    # 8. merge multiple copy-of elements
    if _optimize_multiple_copy_of_merge(elem):
        print("multiple_copy_of_merge applied")
        changed = True
        actions.append({"op": "multiple_copy_of_merge"})

    # 9. collapse nested loops (simple implementation)
    if _collapse_nested_loops(elem):
        changed = True
        actions.append({"op": "collapse_nested_loops"})

    if not changed:
        return template_text, actions

    if wrapper_used:
        # Strip the dummy wrapper and serialize only its children
        refined_parts = [
            etree.tostring(child, encoding="unicode", pretty_print=True)
            for child in elem
        ]
        refined_text = "".join(refined_parts)
    else:
        refined_text = etree.tostring(elem, encoding="unicode", pretty_print=True)

    return refined_text, actions
