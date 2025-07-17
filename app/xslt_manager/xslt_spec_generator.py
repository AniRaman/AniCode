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
from collections import defaultdict
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
# XML namespace for XSLT
XSLT_NS = "http://www.w3.org/1999/XSL/Transform"
NSMAP = {"xsl": XSLT_NS}

def _avt_to_string(avt: Optional[str]) -> str:
    if not avt:
        return ''
    return re.sub(r'[{}]', '', avt)

def _strip_xpath(expr: str) -> str:
    """Strip wrapping functions to extract the raw XPath expression."""
    expr = expr.strip()
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

def _extract_input_paths(expr: str) -> List[str]:
    expr = expr.strip()
    # skip literal strings
    if expr.startswith(("'", '"')) and expr.endswith(("'", '"')):
        return []
    # parse nested functions
    calls = _parse_functions(expr)
    if calls:
        paths: List[str] = []
        for _, args in calls:
            for arg in args:
                paths.extend(_extract_input_paths(arg))
        return paths
    # arithmetic at top-level: split into operands
    for op in (' div ', ' * ', ' + ', ' - '):
        if op in expr:
            parts = expr.split(op, 1)
            paths: List[str] = []
            for part in parts:
                paths.extend(_extract_input_paths(part))
            return paths
    # atomic expression
    return [expr]

def _phrase_value_of(node: etree._Element) -> str:
    sel = node.get('select', '').strip()
    raw = _strip_xpath(sel)
    # skip default value-of dot (loop context)
    if raw == '.':
        return ''
    calls = _parse_functions(sel)
    phrases: List[str] = []
    functions = ['concat', 'substring']
    for name, args in calls:
        if name == 'concat':
            non_literals = [a.strip() for a in args if not a.strip().startswith(("'", '"'))]
            non_literals = [a for a in non_literals if not any(func in a for func in functions)]
            phrases.append(f"Concatenate the following {', '.join(non_literals)}")
        elif name == 'substring' and len(args) >= 3:
            phrases.append(f"Substring of {args[0].strip()} from pos {args[1].strip()} length {args[2].strip()}")
        else:
            phrases.append(f"Call {name} on {', '.join(a.strip() for a in args)}")
    if phrases:
        return ', '.join(phrases)
    # fallback arithmetic
    if ' div ' in sel:
        left, right = [p.strip() for p in sel.split(' div ', 1)]
        return f"Divide {left} by {right}"
    if ' * ' in sel:
        left, right = [p.strip() for p in sel.split(' * ', 1)]
        return f"Multiply {left} by {right}"
    if ' + ' in sel:
        left, right = [p.strip() for p in sel.split(' + ', 1)]
        return f"Add {left} and {right}"
    if ' - ' in sel:
        parts = sel.split(' - ', 1)
        if len(parts) == 2:
            return f"Subtract {parts[1].strip()} from {parts[0].strip()}"
    return f"Outputs text of {sel}"

PHRASE_HANDLERS = {
    # skip dot selections
    'for-each': lambda n: f"Iterate over {_strip_xpath(n.get('select','').strip())}" if n.get('select') and _strip_xpath(n.get('select','').strip()) != '.' else '',
    'choose': lambda n: "Has conditional logic",
    'when': lambda n: f"Branch on {n.get('test')}",
    'if': lambda n: f"Condition when {n.get('test')}",
    'element': lambda n: f"Creates element {_avt_to_string(n.get('name'))}",
    'copy-of': lambda n: f"Copies nodes via select={_strip_xpath(n.get('select','').strip())}" if n.get('select') and _strip_xpath(n.get('select','').strip()) != '.' else '',
    'call-template': lambda n: f"Delegates to {n.get('name')}",
    'apply-templates': lambda n: f"Applies templates on {_strip_xpath(n.get('select','').strip())}" if n.get('select') and _strip_xpath(n.get('select','').strip()) != '.' else '',
    # value-of handler covers arithmetic, substring, and concatenation
    'value-of': _phrase_value_of,
}

def _collect_phrases(node) -> List[str]:
    phrases: List[str] = []
    local = etree.QName(node.tag).localname
    if local in PHRASE_HANDLERS:
        phrases.append(PHRASE_HANDLERS[local](node))
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
        r'^Creates element ',
        r'^Delegates to '
    ]
    
    if any(re.search(pattern, remark) for pattern in simple_patterns):
        return False
        
    # Check for complex patterns
    complex_patterns = [
        r'\bconcat\b',
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
        r' and ',
        r' or ',
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
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Get unique remarks to format
            unique_remarks = list(self.remarks_to_format.keys())
            formatted_remarks = loop.run_until_complete(
                batch_format_remarks(unique_remarks)
            )
            
            # Update specs with formatted remarks
            for orig, formatted in formatted_remarks.items():
                for spec in self.remarks_to_format[orig]:
                    spec.formatted_remarks = formatted
                    spec.remarks = formatted
        
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
                    f"//xsl:for-each[contains(@select, '@{attr}')]|"
                    f"//xsl:value-of[contains(@select, '@{attr}')]|"
                    f"//xsl:attribute[@name='{attr}']"
                )
                snippets = self.tree.xpath(xpath_expr, namespaces=NSMAP)
                if snippets:
                    # pick best snippet: prefer for-each, then value-of, then attribute
                    best = next((sn for sn in snippets if etree.QName(sn.tag).localname == 'for-each'), None)
                    best = best or next((sn for sn in snippets if etree.QName(sn.tag).localname == 'value-of'), None)
                    best = best or next((sn for sn in snippets if etree.QName(sn.tag).localname == 'attribute'), None)
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
                        'remarks': f"Fallback copy for @{attr}"
                    })
            # child-element specs
            # literal elements in XSLT matching this XML tag
            xpath_el = f"//xsl:template//*[local-name()='{xml_tag}' and namespace-uri()!='{XSLT_NS}']"
            snippets_el = self.tree.xpath(xpath_el, namespaces=NSMAP)
            if snippets_el:
                for sn in snippets_el:
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
                    'remarks': f"Fallback copy for <{xml_tag}>"
                })
        # Remove duplicate rows with same spec_type and xml_output_node_path
        seen = set()
        unique_rows = []
        for row in rows:
            key = (row['spec_type'], row['xml_output_node_path'])
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
            # run async batch formatting
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            formatted_map = loop.run_until_complete(batch_format_remarks(unique_remarks))
            for row in rows:
                orig = row.get('remarks')
                if orig in formatted_map:
                    row['remarks'] = formatted_map[orig]
        return rows

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
                    var_name = sub[1:]
                    var_nodes = self.tree.xpath(f"//xsl:variable[@name='{var_name}']", namespaces=NSMAP)
                    if var_nodes and var_nodes[0].get('select'):
                        inputs.add(_strip_xpath(var_nodes[0].get('select')))
                    else:
                        inputs.add(sub)
                elif re.match(r'^[0-9]+(\.[0-9]+)?$', sub):
                    continue
                else:
                    inputs.add(_strip_xpath(sub))
        # capture xsl:param inside snippet
        for p in element.xpath('.//xsl:param', namespaces=NSMAP):
            inputs.add(f"${p.get('name')}" )
        # capture descendant select attributes, ignore '.' (loop context)
        for node in element.xpath('.//*[@select]', namespaces=NSMAP):
            sel = node.get('select', '').strip()
            if not sel or sel == '.':
                continue
            for sub in _extract_input_paths(sel):
                sub = sub.strip()
                if not sub or sub == '.':
                    continue
                if sub.startswith('$'):
                    var_name = sub[1:]
                    var_nodes = self.tree.xpath(f"//xsl:variable[@name='{var_name}']", namespaces=NSMAP)
                    if var_nodes and var_nodes[0].get('select'):
                        inputs.add(_strip_xpath(var_nodes[0].get('select')))
                    else:
                        inputs.add(sub)
                elif re.match(r'^[0-9]+(\.[0-9]+)?$', sub):
                    continue
                else:
                    inputs.add(_strip_xpath(sub))
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
        spec.inputs = sorted(i for i in inputs if '(' not in i and ')' not in i)
        spec.outputs = sorted(outputs)
        spec.calls = sorted(calls)
        # annotate complexity
        spec.complexity = len(phrases)
        return spec

# CLI
if __name__ == '__main__':
    import sys, json
    from pathlib import Path

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
        mapping_json = json.dumps(mapping, indent=2)
        mapping_file = Path(xslt_path).stem + "_mapping_specs.txt"
        with open(mapping_file, "w", encoding="utf-8") as f:
            f.write(mapping_json)
        print(f"Mapping specs written to {mapping_file}")
