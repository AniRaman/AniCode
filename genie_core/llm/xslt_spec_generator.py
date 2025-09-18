"""
Module: xslt_spec_generator
OOP-based XSLT specification generator that parses XSLT templates, extracts inputs, outputs,
calls, heuristically builds remarks, links call-chains, and computes transitive outputs.
"""
import re
from collections import defaultdict
from dataclasses import dataclass, field
from lxml import etree
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Tuple
import asyncio
from openai import AzureOpenAI
import httpx
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
import sys
# XML namespace for XSLT
XSLT_NS = "http://www.w3.org/1999/XSL/Transform"
NSMAP = {"xsl": XSLT_NS}

def _avt_to_string(avt: Optional[str]) -> str:
    if not avt:
        return ''
    return re.sub(r'[{}]', '', avt)

def _strip_xpath(expr: str, context_element: etree._Element = None) -> str:
    """Strip wrapping functions to extract the raw XPath expression."""
    expr = expr.strip()

    # Handle complex local-name() patterns with multiple elements
    localname_pattern = r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]"
    matches = re.findall(localname_pattern, expr)
    if matches:
        if len(matches) > 1:
            # Multiple local-name patterns - combine them into full path
            combined_path = '/' + '/'.join(matches)
            return combined_path
        elif matches and context_element is not None:
            # Single local-name pattern - use context resolution
            element_name = matches[0]
            # Find the full XML input path from for-each ancestors
            full_path = _extract_input_path_from_foreach(context_element, element_name)
            return full_path if full_path else ('/' + element_name)
        else:
            # Single local-name pattern without context
            element_name = matches[0]
            result_path = '/' + element_name
            return result_path

    # handle function wrappers
    m = re.match(r'^[A-Za-z_][A-Za-z0-9_-]*\((.*)\)$', expr)
    if m:
        inner = m.group(1)
        depth = 0
        part = ''
        for ch in inner:
            if ch == ',' and depth == 0:
                break
            if ch == '(': depth += 1
            elif ch == ')': depth -= 1
            part += ch
        return part.strip()

    return expr

def _resolve_select_with_variables(select_expr: str, context_element: etree._Element) -> str:
    """Resolve a select expression that may contain variables, returning the fully resolved path."""
    if not select_expr.startswith('$'):
        # No variable, handle local-names directly to avoid recursion
        localname_pattern = r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]"
        matches = re.findall(localname_pattern, select_expr)
        if matches:
            if len(matches) > 1:
                return '/' + '/'.join(matches)
            else:
                return '/' + matches[0]
        return select_expr

    # Extract variable part and remaining path
    parts = select_expr.split('/', 1)
    var_part = parts[0]  # $varname
    remaining_path = parts[1] if len(parts) > 1 else ""
    var_name = var_part[1:]  # Remove $

    # Find the variable definition
    root = context_element
    while root.getparent() is not None:
        root = root.getparent()

    xpath_expr = etree.XPath("//xsl:variable[@name=$v]", namespaces=NSMAP)
    var_nodes = xpath_expr(root, v=var_name)

    if not var_nodes:
        return select_expr

    var_node = var_nodes[0]
    var_select = var_node.get('select', '')

    # Recursively resolve the variable's select (in case it also has variables)
    resolved_var_path = _resolve_select_with_variables(var_select, var_node)

    # Combine with remaining path
    if remaining_path:
        # Handle local-names in remaining path directly to avoid recursion
        localname_pattern = r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]"
        matches = re.findall(localname_pattern, remaining_path)
        if matches:
            remaining_stripped = '/' + '/'.join(matches)
        else:
            remaining_stripped = remaining_path

        combined_path = resolved_var_path.rstrip('/') + '/' + remaining_stripped.lstrip('/')
        return combined_path
    else:
        return resolved_var_path

def _extract_input_path_from_foreach(context_element: etree._Element, element_name: str) -> str:
    """Extract full input XML path by walking up for-each ancestors and combining select paths."""
    # Walk up ancestors to find all xsl:for-each elements
    foreach_selects = []
    current = context_element

    while current is not None:
        if (current.tag.startswith('{http://www.w3.org/1999/XSL/Transform}') and
            etree.QName(current.tag).localname == 'for-each'):
            select_attr = current.get('select', '').strip()
            if select_attr:
                # Use the generalized variable resolution function
                resolved_select = _resolve_select_with_variables(select_attr, current)
                foreach_selects.insert(0, resolved_select)
        current = current.getparent()

    # Parse and combine all select paths
    combined_path = _combine_select_paths(foreach_selects)

    # Add the target element name if not already in path
    if element_name and element_name not in combined_path:
        if combined_path and not combined_path.endswith('/'):
            combined_path += '/' + element_name
        else:
            combined_path = (combined_path or '') + element_name

    # Ensure path starts with /
    if combined_path and not combined_path.startswith('/'):
        combined_path = '/' + combined_path

    final_path = combined_path or ('/' + element_name)
    return final_path

def _combine_select_paths(select_paths: list) -> str:
    """Combine multiple for-each select paths into a single input path."""
    if not select_paths:
        return ''

    combined_parts = []

    for i, select_path in enumerate(select_paths):
        path_parts = _parse_select_path(select_path)
        combined_parts.extend(path_parts)

    result = '/' + '/'.join(combined_parts) if combined_parts else ''
    return result

def _parse_select_path(select_path: str) -> list:
    """Parse a for-each select path and extract clean element names."""
    select_path = select_path.strip()

    # Handle complex expressions like (./node())[./self::text()]
    if select_path.startswith('(') and ')' in select_path:
        # For complex node selections, we're typically staying in the same context
        # The parent element context is what matters for "." resolution
        return []  # Don't add anything - stay in current context

    # Handle local-name() patterns: *[local-name()='ElementName' and namespace-uri()='']
    localname_pattern = r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]"
    matches = re.findall(localname_pattern, select_path)
    if matches:
        # For complex paths with multiple local-name patterns, combine them into a single path
        if len(matches) > 1:
            combined_path = '/'.join(matches)
            return [combined_path]
        else:
            return matches

    # Handle simple path patterns: Root/Contact/EmailAddress
    if '/' in select_path:
        # Split by / and clean each part
        parts = []
        for i, part in enumerate(select_path.split('/')):
            part = part.strip()
            if part and part != '.' and not part.startswith('@'):
                # Handle local-name patterns in path parts
                localname_match = re.search(r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]", part)
                if localname_match:
                    element_name = localname_match.group(1)
                    parts.append(element_name)
                else:
                    # Remove any predicates like [position()=1]
                    clean_part = re.sub(r'\[.*?\]', '', part)
                    if clean_part and clean_part != '*':
                        parts.append(clean_part)
        # Return the parts as a single combined path if there are multiple parts
        if len(parts) > 1:
            return ['/'.join(parts)]  # Return as single complete path
        else:
            return parts

    # Single element with local-name pattern
    localname_match = re.search(r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]", select_path)
    if localname_match:
        element_name = localname_match.group(1)
        return [element_name]

    # Single element
    if select_path and select_path != '.' and not select_path.startswith('@') and select_path != '*':
        clean_element = re.sub(r'\[.*?\]', '', select_path)
        return [clean_element] if clean_element else []

    return []

def _split_args(expr: str) -> List[str]:
    parts, depth, cur = [], 0, ''
    for ch in expr:
        if ch == ',' and depth == 0:
            parts.append(cur)
            cur = ''
        else:
            cur += ch
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
    if cur.strip():
        parts.append(cur)
    return parts

def _parse_functions(expr: str) -> List[Tuple[str, List[str]]]:
    expr = expr.strip()
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_-]*)\((.*)\)$', expr)
    if not m:
        return []
    name, inner = m.group(1), m.group(2)
    args = _split_args(inner)
    result = [(name, args)]
    for arg in args:
        result.extend(_parse_functions(arg.strip()))
    return result

def is_valid_path(item: str) -> bool:
    """Check if an item is a valid path/input and should be included in the inputs section."""
    item = item.strip()

    # Empty items
    if not item:
        return False

    # Variable references are valid
    if item.startswith('$') and re.match(r'^\$[a-zA-Z_][a-zA-Z0-9_]*', item):
        return True

    # Quoted literals are valid (like 'CIPAX', "somevalue")
    if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
        return True

    # Check alphanumeric ratio - should be mostly alphanumeric/path characters
    # This will catch the problematic strings like "./<>?abcdefg..."
    valid_chars = sum(1 for c in item if c.isalnum() or c in '/_-')
    ratio = valid_chars / len(item) if len(item) > 0 else 0
    if ratio < 0.6:  # At least 60% valid path chars
        return False

    # Valid path patterns (absolute or relative)
    if re.match(r'^/?[a-zA-Z_][a-zA-Z0-9_/-]*$', item):
        return True

    return False

def _extract_input_paths(expr: str) -> List[str]:
    expr = expr.strip()
    # capture literal strings without quotes, skip punctuation-only strings
    if expr.startswith(("'", '"')) and expr.endswith(("'", '"')):
        literal = expr[1:-1]
        # skip if it's just punctuation/symbols (length <= 2 and no alphanumeric)
        if len(literal) <= 2 and not any(c.isalnum() for c in literal):
                return []
        return [literal]
    # parse nested functions
    calls = _parse_functions(expr)
    if calls:
        paths: List[str] = []
        for func_name, args in calls:
            # Special handling for translate function - only process first argument for inputs
            if func_name == 'translate':
                if args:
                    first_arg = args[0]
                    sub_paths = _extract_input_paths(first_arg)
                    paths.extend(sub_paths)
                # Completely ignore 2nd and 3rd arguments of translate (including any nested functions)
            else:
                # For all other functions, process all arguments
                for arg in args:
                    sub_paths = _extract_input_paths(arg)
                    paths.extend(sub_paths)
        return paths
    # arithmetic at top-level: split into operands
    for op in (' div ', ' * ', ' + ', ' - '):
        if op in expr:
            parts = expr.split(op, 1)
            paths: List[str] = []
            for part in parts:
                sub_paths = _extract_input_paths(part)
                paths.extend(sub_paths)
            return paths
    # atomic expression
    return [expr]

def _resolve_variable_for_remarks(var_ref: str, context_node: etree._Element) -> str:
    """Resolve a variable reference for use in remarks. Returns a human-readable description."""
    if not var_ref.startswith('$'):
        return var_ref

    var_name = var_ref[1:].split('/')[0].split('[')[0]

    # Find the document root to search for variables
    root = context_node
    while root.getparent() is not None:
        root = root.getparent()

    # Find variable definition
    xpath_expr = etree.XPath("//xsl:variable[@name=$v]", namespaces=NSMAP)
    var_nodes = xpath_expr(root, v=var_name)

    if not var_nodes:
        return var_ref  # variable not found, return as-is

    var_node = var_nodes[0]

    # Simple resolution - just look for the first meaningful select
    # Check if variable itself has @select
    if var_node.get('select'):
        select_expr = var_node.get('select').strip()
        # Extract the main path from the select
        extracted_paths = _extract_input_paths(select_expr)
        for sub in extracted_paths:
            sub = sub.strip()
            if sub:  # Don't skip "." here - it's a valid result
                if sub.startswith('$'):
                    # Avoid deep recursion - just use the variable name
                    result = f"value from {sub}"
                    return result
                elif sub == '.':
                    # Resolve the actual path that "." refers to
                    resolved_path = _extract_input_path_from_foreach(context_node, '')
                    if resolved_path and resolved_path != '/':
                        result = f"current context from {resolved_path}"
                        return result
                    else:
                        return "current context"
                else:
                    result = _strip_xpath(sub, context_node)
                    return result

    # Check for select attributes in descendants
    descendant_selects = var_node.xpath('.//*[@select]', namespaces=NSMAP)
    for select_node in descendant_selects:
        select_expr = select_node.get('select', '').strip()
        if select_expr:
            extracted_paths = _extract_input_paths(select_expr)
            for sub in extracted_paths:
                sub = sub.strip()
                if sub:  # Don't skip "." here - it's a valid result
                    if sub.startswith('$'):
                        # Avoid deep recursion - just use the variable name
                        result = f"value from {sub}"
                        return result
                    elif sub == '.':
                        # Resolve the actual path that "." refers to
                        resolved_path = _extract_input_path_from_foreach(context_node, '')
                        if resolved_path and resolved_path != '/':
                            result = f"current context from {resolved_path}"
                            return result
                        else:
                            return "current context"
                    else:
                        result = _strip_xpath(sub, context_node)
                        return result

    # Fallback - return the original variable name
    return var_ref

def _phrase_value_of(node: etree._Element) -> str:
    sel = node.get('select', '').strip()

    # handle select="." by resolving context
    if sel == '.':
        # Get input path from for-each ancestors
        resolved_path = _extract_input_path_from_foreach(node, '')
        if resolved_path and resolved_path != '/':
            result = f"Outputs current context from {resolved_path}"
            return result
        else:
            return "Outputs current context"

    # Check if this is a function call (has parentheses)
    calls = _parse_functions(sel)
    if calls:
        # Process only the outermost function to avoid duplicates
        return _process_outermost_function(calls[0], node)

    # fallback arithmetic
    if ' div ' in sel:
        left, right = [p.strip() for p in sel.split(' div ', 1)]
        left = _resolve_variable_for_remarks(left, node) if left.startswith('$') else left
        right = _resolve_variable_for_remarks(right, node) if right.startswith('$') else right
        return f"Divide {left} by {right}"
    if ' * ' in sel:
        left, right = [p.strip() for p in sel.split(' * ', 1)]
        left = _resolve_variable_for_remarks(left, node) if left.startswith('$') else left
        right = _resolve_variable_for_remarks(right, node) if right.startswith('$') else right
        return f"Multiply {left} by {right}"
    if ' + ' in sel:
        left, right = [p.strip() for p in sel.split(' + ', 1)]
        left = _resolve_variable_for_remarks(left, node) if left.startswith('$') else left
        right = _resolve_variable_for_remarks(right, node) if right.startswith('$') else right
        return f"Add {left} and {right}"
    if ' - ' in sel:
        parts = sel.split(' - ', 1)
        if len(parts) == 2:
            left = _resolve_variable_for_remarks(parts[0].strip(), node) if parts[0].strip().startswith('$') else parts[0].strip()
            right = _resolve_variable_for_remarks(parts[1].strip(), node) if parts[1].strip().startswith('$') else parts[1].strip()
            return f"Subtract {right} from {left}"

    # Simple variable or path reference
    if sel.startswith('$'):
        return f"Outputs text of {_resolve_variable_for_remarks(sel, node)}"
    else:
        return f"Outputs text of {_strip_xpath(sel, node)}"

def _process_outermost_function(call_info, node):
    """Process the outermost function with proper nested function resolution."""
    name, args = call_info

    # Resolve all arguments, handling nested functions properly
    resolved_args = []
    for arg in args:
        arg = arg.strip()
        if arg.startswith('$'):
            resolved_args.append(_resolve_variable_for_remarks(arg, node))
        elif '(' in arg and ')' in arg:
            # This is a nested function - resolve it to a human-readable description
            nested_calls = _parse_functions(arg)
            if nested_calls:
                nested_result = _process_outermost_function(nested_calls[0], node)
                # Extract just the description part without "Outputs text of" prefix
                if nested_result.startswith("Outputs text of "):
                    nested_result = nested_result[16:]  # Remove "Outputs text of " prefix
                resolved_args.append(nested_result)
            else:
                resolved_args.append(_strip_xpath(arg, node))
        elif arg.strip() == '.':
            # Resolve dot context to actual path
            resolved_path = _extract_input_path_from_foreach(node, '')
            if resolved_path and resolved_path != '/' and resolved_path != '.':
                resolved_args.append(resolved_path)
            else:
                resolved_args.append("current context")
        else:
            resolved_args.append(arg)

    # Special formatting for common functions, generic for others
    if name == 'concat':
        non_literals = [arg for arg in resolved_args if not arg.startswith(("'", '"'))]
        return f"concat {', '.join(non_literals)}, " if non_literals else "concat, "
    elif name == 'substring':
        if len(resolved_args) >= 3:
            return f"Substring of {resolved_args[0]} from pos {resolved_args[1]} length {resolved_args[2]}, "
        elif len(resolved_args) == 2:
            return f"Substring of {resolved_args[0]} from pos {resolved_args[1]}, "
        else:
            return f"Substring of {resolved_args[0]}, "
    elif name == 'translate':
        if len(resolved_args) >= 3:
            return f"Translate {resolved_args[0]} from '{resolved_args[1]}' to '{resolved_args[2]},'"
        else:
            return f"Call {name} on {', '.join(resolved_args)}"
    elif name == 'normalize-space':
        return f"Normalize whitespace in {resolved_args[0] if resolved_args else 'text'},"
    elif name == 'string':
        return f"Convert {resolved_args[0] if resolved_args else 'value'} to string"
    elif name == 'number':
        return f"Convert {resolved_args[0] if resolved_args else 'value'} to number"
    elif name == 'contains':
        if len(resolved_args) >= 2:
            return f"Check if {resolved_args[0]} contains '{resolved_args[1]}'"
        else:
            return f"Call {name} on {', '.join(resolved_args)}"
    else:
        # Generic function call - works for any function
        return f"Call {name} on {', '.join(resolved_args)}"

PHRASE_HANDLERS = {
    # skip dot selections
    'for-each': lambda n: f"Iterate over {_strip_xpath(n.get('select','').strip())}" if n.get('select') and _strip_xpath(n.get('select','').strip()) != '.' else '',
    'choose': lambda n: "Has conditional logic",
    'when': lambda n: f"Branch on {n.get('test')}",
    'if': lambda n: f"Condition when {n.get('test')}",
    'element': lambda n: f"Creates element {_avt_to_string(n.get('name'))}",
    'copy-of': lambda n: f"Copies nodes via select={_strip_xpath(n.get('select','').strip())}" if n.get('select') and _strip_xpath(n.get('select','').strip()) != '.' else '',
    'apply-templates': lambda n: f"Applies templates on {_strip_xpath(n.get('select','').strip())}" if n.get('select') and _strip_xpath(n.get('select','').strip()) != '.' else '',
    # value-of handler covers arithmetic, substring, and concatenation
    'value-of': _phrase_value_of,
}

def _collect_phrases(node) -> List[str]:
    phrases: List[str] = []
    local = etree.QName(node.tag).localname
    if local in PHRASE_HANDLERS:
        phrase = PHRASE_HANDLERS[local](node)
        phrases.append(phrase)
    for child in node:
        phrases.extend(_collect_phrases(child))
    return phrases

@dataclass
class TemplateSpec:
    name: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    remarks: str = ""
    formatted_remarks: Optional[str] = None
    transitive_outputs: List[str] = field(default_factory=list)
    complexity: int = 0
    snippet: str = ""

def needs_llm_formatting(remark: str) -> bool:
    """Determine if a remark needs LLM formatting."""
    if not remark or ',' not in remark:  # Single operation
        return False
        
    # Skip simple patterns
    simple_patterns = [
        r'^Outputs text of ',
        r'^Creates element '
    ]
    
    if any(re.search(pattern, remark) for pattern in simple_patterns):
        return False
        
    # Check for complex patterns
    complex_patterns = [
        r'\bconcat\b',
        r'\bTranslate\b',
        r'\bsubstring\b',
        r'\bdiv\b',
        r'\*',
        r'\+',
        r'-',
        r'\bwhen\b',
        r'\bif\b',
        r'\bchoose\b',
        r'\bfor-each\b',
        r'\bapply-templates\b',
        r'Copies nodes via ',
        r'Iterate over ',
        r'Branch on ',
        r'Condition when ',
        r'Applies templates on ',
        r'\[.*?\]'  # XPath predicates
    ]
    print("remark : ",remark,"  Needs LLM Formatting:",any(re.search(pattern, remark, re.IGNORECASE) for pattern in complex_patterns))
    return any(re.search(pattern, remark, re.IGNORECASE) for pattern in complex_patterns)

async def batch_format_remarks(remarks: List[str], batch_size: int = 50) -> Dict[str, str]:
    """
    Format a batch of remarks using LLM.
    Returns a dictionary mapping original remarks to their formatted versions.
    """
    if not remarks:
        return {}
        
    # Initialize LLM client
    client = AzureOpenAI(
        azure_endpoint=os.getenv("o3_mini_AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("o3_mini_AZURE_OPENAI_KEY"),
        api_version=os.getenv("o3_mini_AZURE_API_VERSION"),
        http_client=httpx.Client(verify=False)
    )
    
    results = {}
    
    # Process in batches
    for i in range(0, len(remarks), batch_size):
        print("Length of remakrs:",len(remarks))
        batch = remarks[i:i + batch_size]
        #print("batch",batch)
        # Prepare the prompt
        system_prompt = """You are a helpful assistant that explains XSLT transformations in simple, clear language. 
        For each transformation description, rewrite it to be more readable and understandable, 
        focusing on what the transformation is doing in business terms. Keep the explanation concise."""
        
        user_prompt = """Please explain these XSLT transformations in simple terms. 
        For each transformation, provide a clear, concise explanation on a new line.
        
        """ + "\n---\n".join(f"{i+1}. {remark}" for i, remark in enumerate(batch))
        
        try:
            # Call the LLM
            response_obj = client.chat.completions.create(
                model=os.getenv("o3_mini_MODEL_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            response = response_obj.choices[0].message.content
            print(f"RESPONSE: {response}")
            
            # Parse the response
            choices = getattr(response_obj, 'choices', None)
            if choices and choices[0].message and choices[0].message.content:
                formatted_responses = choices[0].message.content.split('\n')
                formatted_responses = [r.strip() for r in formatted_responses if r.strip()]
                
                #print("formatted_responses",formatted_responses)
                
                # Map responses back to original remarks
                for orig, formatted in zip(batch, formatted_responses):
                    # Clean up the response (remove numbering if present)
                    formatted = re.sub(r'^\d+\.?\s*', '', formatted).strip()
                    results[orig] = formatted
        
        except Exception as e:
            print(f"Error in batch formatting: {e}")
            # Fallback: use original remarks for this batch
            for remark in batch:
                results[remark] = remark
    print("results",results)
    return results

class XsltSpecGenerator:
    def __init__(self, xslt_path: str):
        self.xslt_path = Path(xslt_path)
        self.tree: Optional[etree._ElementTree] = None
        self.templates: Dict[str, etree._Element] = {}
        self.specs: Dict[str, TemplateSpec] = {}
        self.remarks_to_format: Dict[str, List[TemplateSpec]] = defaultdict(list)

    def load(self) -> None:
        parser = etree.XMLParser(remove_comments=True, recover=True)
        self.tree = etree.parse(str(self.xslt_path), parser)

    def index_templates(self) -> None:
        # collect all <xsl:template> elements by name or match
        self.templates.clear()
        for t in self.tree.xpath('//xsl:template', namespaces=NSMAP):
            key = t.get('name') or t.get('match')
            if key:
                self.templates[key] = t

    def link_calls(self) -> None:
        # build call graph and compute transitive outputs
        graph: Dict[str, List[str]] = defaultdict(list)
        for spec in self.specs.values():
            for c in spec.calls:
                if c.startswith('call:'):
                    tgt = c.split(':', 1)[1]
                    if tgt in self.specs:
                        graph[spec.name].append(tgt)
        def dfs(node: str, visited: Set[str] = None) -> Set[str]:
            if visited is None:
                visited = set()
            visited.add(node)
            outs = set(self.specs[node].outputs)
            for child in graph.get(node, []):
                if child not in visited:
                    outs |= dfs(child, visited)
            return outs
        for spec in self.specs.values():
            spec.transitive_outputs = sorted(dfs(spec.name))

    def generate(self) -> List[TemplateSpec]:
        """Generate specs for all templates in the XSLT."""
        self.load()
        self.index_templates()
        
        # First pass: collect all specs and identify remarks that need formatting
        self.specs = {}
        for name, tpl in self.templates.items():
            spec = self.spec_from_element(tpl)
            self.specs[name] = spec
            
            # Check if remark needs formatting
            if spec.remarks and needs_llm_formatting(spec.remarks):
                self.remarks_to_format[spec.remarks].append(spec)
        
        # Format remarks in batches
        if self.remarks_to_format:
            try:
                # Try to run async batch formatting
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Event loop is running, skip LLM formatting to avoid conflicts
                        print("Warning: Event loop is running, skipping LLM remark formatting")
                        formatted_remarks = {}
                    else:
                        # Get unique remarks to format
                        unique_remarks = list(self.remarks_to_format.keys())
                        formatted_remarks = loop.run_until_complete(
                            batch_format_remarks(unique_remarks)
                        )
                except RuntimeError:
                    # No event loop exists, create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        unique_remarks = list(self.remarks_to_format.keys())
                        formatted_remarks = loop.run_until_complete(
                            batch_format_remarks(unique_remarks)
                        )
                    finally:
                        loop.close()

                # Update specs with formatted remarks
                for orig, formatted in formatted_remarks.items():
                    for spec in self.remarks_to_format[orig]:
                        spec.formatted_remarks = formatted
                        spec.remarks = formatted

            except Exception as e:
                print(f"Warning: Could not format remarks with LLM: {e}")
                # Continue without formatting - remarks will remain as-is
        
        # Compute transitive outputs across call graph
        self.link_calls()
        return list(self.specs.values())

    def generate_specs_for_xml(self, xml_path: str) -> List[Dict[str, Any]]:
        """
        XML-first spec: for each XML node, find XSLT snippets that process its attributes and child elements,
        generate specs for each snippet, and return a list of dicts.
        """
        # ensure XSLT loaded
        if self.tree is None:
            self.load()
        # parse XML
        xml_tree = etree.parse(str(Path(xml_path)))
        rows: List[Dict[str, Any]] = []
        # for each element in XML
        for elem in xml_tree.iter():
            if not isinstance(elem.tag, str):
                continue
            # build readable XPath using element local names
            ancestors = list(elem.iterancestors())
            ancestors.reverse()
            path_parts = [etree.QName(a.tag).localname for a in ancestors] + [etree.QName(elem.tag).localname]
            xml_path_str = '/' + '/'.join(path_parts)
            xml_tag = etree.QName(elem.tag).localname
            # attribute specs
            for attr in elem.attrib.keys():
                # find all candidate XSLT snippets for this attribute
                xpath_expr = (
                    f"//xsl:for-each[contains(@select, '@{attr}') or contains(@select, \"local-name()='{attr}\")]|"
                    f"//xsl:value-of[contains(@select, '@{attr}') or contains(@select, \"local-name()='{attr}\")]|"
                    f"//xsl:attribute[@name='{attr}']"
                )
                snippets = self.tree.xpath(xpath_expr, namespaces=NSMAP)
                # Filter snippets by matching output path
                matching_snippets = []
                for snippet in snippets:
                    snippet_path = self._extract_output_path_from_xslt(snippet)
                    if snippet_path == xml_path_str:
                        matching_snippets.append(snippet)
                
                if matching_snippets:
                    # pick best snippet: prefer for-each, then value-of, then attribute
                    best = next((sn for sn in matching_snippets if etree.QName(sn.tag).localname == 'for-each'), None)
                    if best is None:
                        best = next((sn for sn in matching_snippets if etree.QName(sn.tag).localname == 'value-of'), None)
                    if best is None:
                        best = next((sn for sn in matching_snippets if etree.QName(sn.tag).localname == 'attribute'), None)
                    spec = self.spec_from_element(best)
                    rows.append({
                        'xml_output_node_path': xml_path_str,
                        'xml_output_node_tag': xml_tag,
                        'spec_type': 'attribute',
                        'field_name': attr,
                        'xslt_snippet': etree.tostring(best, encoding='unicode', pretty_print=True),
                        'inputs': spec.inputs,
                        'outputs': spec.outputs,
                        'summa': [],
                        'calls': spec.calls,
                        'remarks': spec.formatted_remarks or spec.remarks
                    })
                else:
                    # fallback if no explicit mapping
                    rows.append({
                        'xml_output_node_path': xml_path_str,
                        'xml_output_node_tag': xml_tag,
                        'spec_type': 'attribute',
                        'field_name': attr,
                        'xslt_snippet': "",
                        'inputs': [],
                        'outputs': [],
                        'calls': [],
                        'remarks': f"No info found for @{attr} in XSLT"
                    })
            # child-element specs
            # literal elements in XSLT matching this XML tag
            xpath_el = f"//xsl:template//*[local-name()='{xml_tag}' and namespace-uri()!='{XSLT_NS}']"
            snippets_el = self.tree.xpath(xpath_el, namespaces=NSMAP)
            # Filter element snippets by matching output path
            matching_element_snippets = []
            for snippet in snippets_el:
                snippet_path = self._extract_output_path_from_xslt(snippet)
                if snippet_path == xml_path_str:
                    matching_element_snippets.append(snippet)
            
            if matching_element_snippets:
                for sn in matching_element_snippets:
                    spec = self.spec_from_element(sn)
                    rows.append({
                        'xml_output_node_path': xml_path_str,
                        'xml_output_node_tag': xml_tag,
                        'spec_type': 'element',
                        'field_name': xml_tag,
                        'xslt_snippet': etree.tostring(sn, encoding='unicode', pretty_print=True),
                        'inputs': spec.inputs,
                        'outputs': spec.outputs,
                        'calls': spec.calls,
                        'remarks': spec.formatted_remarks or spec.remarks
                    })
            else:
                # fallback for element copy
                rows.append({
                    'xml_output_node_path': xml_path_str,
                    'xml_output_node_tag': xml_tag,
                    'spec_type': 'element',
                    'field_name': xml_tag,
                    'xslt_snippet': "",
                    'inputs': [],
                    'outputs': [],
                    'calls': [],
                    'remarks': f"No info found for <{xml_tag}> in XSLT"
                })
        # Remove duplicate rows with same spec_type and xml_output_node_path
        seen = set()
        unique_rows = []
        for row in rows:
            # Include xslt_snippet in key to allow different XSLT logic for same XML path
            key = (row['spec_type'], row['xml_output_node_path'], row.get('xslt_snippet', ''))
            if key not in seen:
                seen.add(key)
                unique_rows.append(row)
        rows = unique_rows
        # Remove rows where both inputs and outputs have more than 3 elements
        rows = [
            row for row in rows
            if not (len(row.get('inputs', [])) > 3 and len(row.get('outputs', [])) > 3)
        ]
        # Batch format mapping remarks
        #print("rows",rows)
        unique_remarks = sorted({row['remarks'] for row in rows if row.get('remarks') and needs_llm_formatting(row['remarks'])})
        #print("unique_remarks",unique_remarks)
        if unique_remarks:
            try:
                # Try to run async batch formatting
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Event loop is running, skip LLM formatting to avoid conflicts
                        print("Warning: Event loop is running, skipping LLM remark formatting")
                        formatted_map = {}
                    else:
                        formatted_map = loop.run_until_complete(batch_format_remarks(unique_remarks))
                except RuntimeError:
                    # No event loop exists, create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        formatted_map = loop.run_until_complete(batch_format_remarks(unique_remarks))
                    finally:
                        loop.close()

                # Apply formatted remarks
                for row in rows:
                    orig = row.get('remarks')
                    if orig in formatted_map:
                        row['remarks'] = formatted_map[orig]

            except Exception as e:
                print(f"Warning: Could not format remarks with LLM: {e}")
                # Continue without formatting - remarks will remain as-is
        # Keep original before merging
        original_rows = rows.copy()
        merged_rows = self._merge_duplicate_paths(rows)
        
        # Store both for file writing
        self._original_specs = original_rows
        self._merged_specs = merged_rows
        
        return merged_rows

    def _merge_duplicate_paths(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge specs that have same spec_type and xml_output_node_path."""
        
        # Group by (spec_type, xml_output_node_path)
        groups = defaultdict(list)
        for row in rows:
            key = (row.get('spec_type'), row.get('xml_output_node_path'))
            groups[key].append(row)
        
        merged_rows = []
        seen_keys = set()
        
        # Maintain original order, merge duplicates
        for row in rows:
            key = (row.get('spec_type'), row.get('xml_output_node_path'))
            
            if key in seen_keys:
                continue  # Skip, already processed
                
            seen_keys.add(key)
            group = groups[key]
            
            if len(group) == 1:
                # No duplicates, keep as-is
                merged_rows.append(row)
            else:
                # Merge duplicates
                merged = self._merge_spec_group(group)
                merged_rows.append(merged)
        
        return merged_rows
    
    def _merge_spec_group(self, specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge a group of specs with same spec_type and xml_output_node_path."""
        if not specs:
            return {}
            
        # Start with first spec as base
        merged = specs[0].copy()
        
        # Collect all unique inputs (filter out empty lists)
        all_inputs = set()
        for spec in specs:
            inputs = spec.get('inputs', [])
            if inputs:  # Skip empty lists
                all_inputs.update(inputs)
        merged['inputs'] = list(all_inputs) if all_inputs else []
        
        # Collect all unique outputs (filter out empty lists) 
        all_outputs = set()
        for spec in specs:
            outputs = spec.get('outputs', [])
            if outputs:  # Skip empty lists
                all_outputs.update(outputs)
        merged['outputs'] = list(all_outputs) if all_outputs else []
        
        # Collect all unique calls (filter out empty lists)
        all_calls = set()
        for spec in specs:
            calls = spec.get('calls', [])
            if calls:  # Skip empty lists
                all_calls.update(calls)
        merged['calls'] = list(all_calls) if all_calls else []
        
        # Concatenate remarks with " OR "
        remarks_parts = []
        for spec in specs:
            remark = spec.get('remarks', '').strip()
            if remark and remark not in remarks_parts:
                remarks_parts.append(remark)
        merged['remarks'] = ' OR '.join(remarks_parts) if remarks_parts else ''
        
        return merged

    def _extract_output_path_from_xslt(self, snippet_element: etree._Element) -> str:
        """Extract the output XML path from an XSLT snippet by walking up literal elements."""
        # Find the target element (the one being processed - usually the snippet_element itself or a descendant)
        target = snippet_element
        
        # If this is a for-each or other control element, find the literal output element
        if etree.QName(snippet_element.tag).localname in ('for-each', 'if', 'choose', 'when', 'otherwise', 'variable'):
            # Find first literal (non-xsl) descendant element
            for desc in snippet_element.iter():
                if not desc.tag.startswith('{http://www.w3.org/1999/XSL/Transform}'):
                    target = desc
                    break
        
        # Walk up ancestors to build path, collecting all literal elements
        path_parts = []
        current = target
        
        while current is not None:
            # Skip xsl: namespace elements but continue walking up
            if not current.tag.startswith('{http://www.w3.org/1999/XSL/Transform}'):
                tag = etree.QName(current.tag).localname
                path_parts.insert(0, tag)
            current = current.getparent()
            # Stop only when we reach the root (no more parents)
        
        return '/' + '/'.join(path_parts) if path_parts else ''

    def _resolve_variable_or_template(self, var_name: str, context_element: etree._Element = None, visited: Set[str] = None) -> Set[str]:
        """Recursively resolve a variable by chasing @select attributes until reaching actual paths."""
        if visited is None:
            visited = set()

        # Prevent infinite recursion
        if var_name in visited:
            return {f"${var_name}"}  # fallback to variable name
        visited.add(var_name)

        inputs = set()

        # Find variable definition
        xpath_expr = etree.XPath("//xsl:variable[@name=$v]", namespaces=NSMAP)
        var_nodes = xpath_expr(self.tree, v=var_name)

        if not var_nodes:
            return {f"${var_name}"}  # variable not found, return as-is

        var_node = var_nodes[0]

        # Search for ALL @select attributes within this variable (including the variable itself)
        select_expressions = []

        # Check if variable itself has @select
        if var_node.get('select'):
            select_val = var_node.get('select').strip()
            select_expressions.append(select_val)

        # Check all descendant elements with @select
        descendant_selects = var_node.xpath('.//*[@select]', namespaces=NSMAP)
        for select_node in descendant_selects:
            select_expr = select_node.get('select', '').strip()
            if select_expr:
                select_expressions.append(select_expr)

        # Process all found select expressions
        for i, select_expr in enumerate(select_expressions):
            extracted_paths = _extract_input_paths(select_expr)
            for sub in extracted_paths:
                sub = sub.strip()
                if not sub:
                    continue

                if sub.startswith('$'):
                    # Chase the variable recursively
                    nested_var = sub[1:].split('/')[0].split('[')[0]
                    resolved = self._resolve_variable_or_template(nested_var, context_element, visited.copy())
                    inputs.update(resolved)
                elif re.match(r'^[0-9]+(\.[0-9]+)?$', sub):
                    continue  # skip numeric literals
                else:
                    # Found actual path - use context resolution for "."
                    if sub == '.':
                        # Use for-each ancestor path resolution (already implemented)
                        if context_element is not None:
                            # Walk up to find for-each with meaningful select
                            anc = context_element
                            while anc is not None:
                                if (anc.tag.startswith('{http://www.w3.org/1999/XSL/Transform}') and
                                    etree.QName(anc.tag).localname == 'for-each'):
                                    parent_sel = anc.get('select', '').strip()
                                    if parent_sel and parent_sel != '.':
                                        stripped_path = _strip_xpath(parent_sel, anc)
                                        inputs.add(stripped_path)
                                        break
                                anc = anc.getparent()
                        else:
                            inputs.add('.')  # fallback
                    else:
                        stripped = _strip_xpath(sub, context_element)
                        inputs.add(stripped)

        result = inputs if inputs else {f"${var_name}"}
        return result

    def _combine_foreach_selects(self, foreach_selects: List[str]) -> str:
        """Combine for-each select paths into a single path."""
        return _combine_select_paths(foreach_selects)


    def spec_from_element(self, element: etree._Element) -> TemplateSpec:
        # Name of spec: XSLT template name/match, else element localname
        name = element.get('name') or element.get('match') or etree.QName(element.tag).localname
        # initialize spec container
        spec = TemplateSpec(name=name)
        # cache raw template snippet
        spec.snippet = etree.tostring(element, encoding='unicode', pretty_print=True)
        # extract inputs, outputs, calls
        inputs, outputs, calls = set(), set(), set()
        # capture snippet's own select attribute (resolve '.' context)
        sel0 = element.get('select')
        if sel0:
            sel0 = sel0.strip()
            # if loop context, find nearest non-dot select ancestor
            if sel0 == '.':
                anc = element.getparent()
                while anc is not None:
                    parent_sel = anc.get('select')
                    if parent_sel and parent_sel.strip() != '.':
                        sel0 = parent_sel.strip()
                        break
                    anc = anc.getparent()
            # flatten expressions into atomic paths (skip vars & numbers)
            for sub in _extract_input_paths(sel0):
                sub = sub.strip()
                if not sub or sub == '.':
                    continue
                if sub.startswith('$'):
                    var_name = sub[1:].split('/')[0].split('[')[0]
                    resolved_inputs = self._resolve_variable_or_template(var_name, element)
                    inputs.update(resolved_inputs)
                elif re.match(r'^[0-9]+(\.[0-9]+)?$', sub):
                    continue
                else:
                    inputs.add(_strip_xpath(sub, element))
        # capture xsl:param inside snippet
        for p in element.xpath('.//xsl:param', namespaces=NSMAP):
            inputs.add(f"${p.get('name')}" )
        # capture descendant value-of select attributes, resolve with parent for-each context
        for node in element.xpath('.//xsl:value-of[@select]', namespaces=NSMAP):
            sel = node.get('select', '').strip()
            if not sel:
                continue

            # Use _extract_input_paths to parse functions and extract components
            extracted_parts = _extract_input_paths(sel)
            for sub in extracted_parts:
                sub = sub.strip()
                if not sub:
                    continue

                # Check if original select was a literal (since _extract_input_paths strips quotes)
                # or if extracted value is a simple literal from functions like concat
                if ((sel.startswith("'") and sel.endswith("'")) or (sel.startswith('"') and sel.endswith('"')) or
                    (re.match(r'^[a-zA-Z0-9_-]+$', sub) and not sub.startswith('/') and len(sub) > 1)):
                    # Original select was a literal, or extracted value is a simple literal
                    inputs.add(sub)
                elif sub == '.':
                    # Dot context - traverse for-each ancestors
                    resolved_path = _extract_input_path_from_foreach(node, '')
                    if resolved_path and resolved_path != '/' and resolved_path != '.':
                        inputs.add(resolved_path)
                elif sub.startswith('$'):
                    # Variable reference
                    var_name = sub.split('/')[0][1:]  # Remove $

                    # Find variable definition
                    root = element
                    while root.getparent() is not None:
                        root = root.getparent()
                    var_nodes = root.xpath(f"//xsl:variable[@name='{var_name}']", namespaces=NSMAP)

                    if var_nodes:
                        var_node = var_nodes[0]
                        var_select = var_node.get('select', '').strip()

                        if var_select:
                            # Variable has direct select attribute
                            if var_select == '.':
                                # Variable has dot - get its ancestor context
                                var_resolved_path = _extract_input_path_from_foreach(var_node, '')

                                # Add any suffix from original variable expression
                                if '/' in sub:
                                    remaining_path = sub[sub.index('/'):]
                                    localname_pattern = r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]"
                                    matches = re.findall(localname_pattern, remaining_path)
                                    if matches:
                                        path_suffix = '/' + '/'.join(matches)
                                        final_path = var_resolved_path.rstrip('/') + path_suffix
                                        inputs.add(final_path)
                                    else:
                                        inputs.add(var_resolved_path)
                                else:
                                    inputs.add(var_resolved_path)
                            else:
                                # Variable has actual path - use it and add any suffix
                                if '/' in sub:
                                    remaining_path = sub[sub.index('/'):]
                                    localname_pattern = r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]"
                                    matches = re.findall(localname_pattern, remaining_path)
                                    if matches:
                                        path_suffix = '/' + '/'.join(matches)
                                        final_path = var_select.rstrip('/') + path_suffix
                                        inputs.add(final_path)
                                    else:
                                        inputs.add(var_select)
                                else:
                                    inputs.add(var_select)
                        else:
                            # Variable has no direct select - look inside its content for nested selects
                            nested_selects = var_node.xpath('.//*[@select]', namespaces=NSMAP)
                            for nested_node in nested_selects:
                                nested_sel = nested_node.get('select', '').strip()
                                if nested_sel:

                                    # Process the nested select using the same logic recursively
                                    for nested_sub in _extract_input_paths(nested_sel):
                                        nested_sub = nested_sub.strip()
                                        if not nested_sub:
                                            continue

                                        if nested_sub == '.':
                                            # Dot context - use the nested node's context
                                            nested_resolved_path = _extract_input_path_from_foreach(nested_node, '')
                                            if nested_resolved_path and nested_resolved_path != '/' and nested_resolved_path != '.':
                                                inputs.add(nested_resolved_path)
                                        elif re.match(r'^[0-9]+(\.[0-9]+)?$', nested_sub):
                                            # Skip numeric literals
                                            continue
                                        elif (nested_sel.startswith("'") and nested_sel.endswith("'")) or (nested_sel.startswith('"') and nested_sel.endswith('"')):
                                            # Original nested select was a literal
                                            inputs.add(nested_sub)
                                        else:
                                            # Other paths - process with ancestor context from nested node
                                            localname_pattern = r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]"
                                            matches = re.findall(localname_pattern, nested_sub)

                                            if matches:
                                                clean_path = '/' + '/'.join(matches)
                                                ancestor_path = _extract_input_path_from_foreach(nested_node, '')
                                                if ancestor_path and ancestor_path != '/' and ancestor_path != '.':
                                                    final_path = ancestor_path + clean_path
                                                    inputs.add(final_path)
                                                else:
                                                    inputs.add(clean_path)
                                            else:
                                                # Direct path
                                                ancestor_path = _extract_input_path_from_foreach(nested_node, '')
                                                if ancestor_path and ancestor_path != '/' and ancestor_path != '.':
                                                    if nested_sub.startswith('/'):
                                                        final_path = ancestor_path + nested_sub
                                                    else:
                                                        final_path = ancestor_path + '/' + nested_sub
                                                    inputs.add(final_path)
                                                else:
                                                    inputs.add(nested_sub)
                    else:
                        continue
                elif re.match(r'^[0-9]+(\.[0-9]+)?$', sub):
                    # Skip numeric literals
                    continue
                else:
                    # Other paths - check for local-name patterns and combine with ancestors

                    # Strip local-name patterns to get clean path
                    localname_pattern = r"\*\[local-name\(\)\s*=\s*['\"]([^'\"]+)['\"]"
                    matches = re.findall(localname_pattern, sub)

                    if matches:
                        # Has local-name patterns - get clean path and combine with ancestors
                        clean_path = '/' + '/'.join(matches)
                        ancestor_path = _extract_input_path_from_foreach(node, '')
                        if ancestor_path and ancestor_path != '/' and ancestor_path != '.':
                            final_path = ancestor_path + clean_path
                            inputs.add(final_path)
                        else:
                            inputs.add(clean_path)
                    else:
                        # Direct path - combine with ancestors
                        ancestor_path = _extract_input_path_from_foreach(node, '')
                        if ancestor_path and ancestor_path != '/' and ancestor_path != '.':
                            if sub.startswith('/'):
                                final_path = ancestor_path + sub
                            else:
                                final_path = ancestor_path + '/' + sub
                            inputs.add(final_path)
                        else:
                            inputs.add(sub)
        for c in element.xpath('.//xsl:call-template', namespaces=NSMAP):
            calls.add(f"call:{c.get('name')}")
        # extract outputs
        for el in element.iter():
            if not isinstance(el.tag, str):
                continue
            qn = etree.QName(el.tag)
            if qn.namespace != XSLT_NS:
                outputs.add(qn.localname)
            elif qn.localname == 'element':
                outputs.add(_avt_to_string(el.get('name', '')))
        # build remark (skip empty phrases)
        raw_phrases = _collect_phrases(element)
        phrases = [p for p in raw_phrases if p]
        spec.remarks = ', '.join(dict.fromkeys(phrases))
        # assign basic fields
        # Filter inputs to remove non-path items and function calls
        filtered_inputs = {i for i in inputs if '(' not in i and ')' not in i and is_valid_path(i)}
        spec.inputs = sorted(filtered_inputs)
        spec.outputs = sorted(outputs)
        spec.calls = sorted(calls)
        # annotate complexity
        spec.complexity = len(phrases)
        return spec

# CLI
if __name__ == '__main__':
    import json

    usage = (
        f"Usage:\n"
        f"  python {sys.argv[0]} path/to/file.xslt [path/to/file.xml]\n"
        f"Examples:\n"
        f"  python {sys.argv[0]} transform.xslt\n"
        f"  python {sys.argv[0]} transform.xslt input.xml"
    )

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    xslt_path = sys.argv[1]
    gen = XsltSpecGenerator(xslt_path)

    # Generate full XSLT specs and write to file
    # specs = gen.generate()
    # full_json = json.dumps([s.__dict__ for s in specs], indent=2)
    # full_file = Path(xslt_path).stem + "_full_specs.txt"
    # with open(full_file, "w", encoding="utf-8") as f:
    #     f.write(full_json)
    # print(f"Full specs written to {full_file}")

    # If XML path provided, generate mapping and write to file
    if len(sys.argv) >= 3:
        xml_path = sys.argv[2]
        mapping = gen.generate_specs_for_xml(xml_path)
        
        # Write merged specs to main file
        mapping_json = json.dumps(mapping, indent=2)
        mapping_file = Path(xslt_path).stem + "_mapping_specs.txt"
        with open(mapping_file, "w", encoding="utf-8") as f:
            f.write(mapping_json)
        print(f"Mapping specs (merged) written to {mapping_file}")
        
        # Write original specs to before_merge file
        if hasattr(gen, '_original_specs'):
            original_json = json.dumps(gen._original_specs, indent=2)
            before_merge_file = Path(xslt_path).stem + "_mapping_specs_before_merge.txt"
            with open(before_merge_file, "w", encoding="utf-8") as f:
                f.write(original_json)
            print(f"Original specs (before merge) written to {before_merge_file}")
