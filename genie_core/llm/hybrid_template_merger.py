"""
Hybrid Template-Based XSLT Merging System
Combines algorithmic chunk extraction with LLM conflict resolution
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Set
from lxml import etree, html
from genie_core.llm.llm_utils import get_chat_completion


class BaseTemplateGenerator:
    """
    Generates XSLT base template from output XML structure with placeholders
    """

    def __init__(self):
        self.debug = True

    def create_base_template_from_output_xml(self, output_xml: str) -> str:
        """
        Create XSLT base template with placeholders from output XML structure

        Args:
            output_xml: Expected output XML structure

        Returns:
            str: XSLT template with placeholders
        """
        print(f"[TEMPLATE DEBUG] ===== CREATING BASE TEMPLATE =====")
        print(f"[TEMPLATE DEBUG] Output XML length: {len(output_xml)} characters")

        try:
            # Parse output XML
            root = etree.fromstring(output_xml.encode('utf-8'))
            print(f"[TEMPLATE DEBUG] Successfully parsed output XML. Root element: {root.tag}")

            # Create XSLT template structure
            template = self._create_xslt_template_structure(root)

            print(f"[TEMPLATE DEBUG] Base template created successfully")
            print(f"[TEMPLATE DEBUG] Template length: {len(template)} characters")

            return template

        except Exception as e:
            print(f"[TEMPLATE DEBUG] ERROR creating base template: {e}")
            raise e

    def _create_xslt_template_structure(self, root_element) -> str:
        """
        Convert XML structure to XSLT template with placeholders
        """
        print(f"[TEMPLATE DEBUG] Converting XML structure to XSLT template")

        # Start building XSLT template
        template_parts = []
        template_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        template_parts.append('<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">')
        template_parts.append('  <xsl:template match="/">')

        # Process root element and children
        template_content = self._process_element_for_template(root_element, "    ")
        template_parts.append(template_content)

        template_parts.append('  </xsl:template>')
        template_parts.append('</xsl:stylesheet>')

        final_template = '\n'.join(template_parts)
        print(f"[TEMPLATE DEBUG] Template structure created with {len(template_parts)} parts")

        return final_template

    def _process_element_for_template(self, element, indent: str) -> str:
        """
        Process XML element and create XSLT template equivalent with placeholders
        """
        element_name = element.tag
        print(f"[TEMPLATE DEBUG] Processing element: {element_name}")

        # Handle namespaces if present
        if '}' in element_name:
            namespace, local_name = element_name.split('}')
            namespace = namespace[1:]  # Remove leading '{'
            element_name = local_name
            print(f"[TEMPLATE DEBUG] Namespace detected: {namespace}, local name: {local_name}")

        # Create placeholder for this element
        placeholder = f"{{{{PLACEHOLDER_{element_name}}}}}"
        print(f"[TEMPLATE DEBUG] Created placeholder: {placeholder}")

        result_parts = []

        # Check if element has children
        if len(element) > 0:
            print(f"[TEMPLATE DEBUG] Element {element_name} has {len(element)} children")

            # Element with children - create container with child placeholders
            result_parts.append(f"{indent}<{element_name}>")

            # Process children
            for child in element:
                child_content = self._process_element_for_template(child, indent + "  ")
                result_parts.append(child_content)

            result_parts.append(f"{indent}</{element_name}>")
        else:
            # Leaf element - replace entirely with placeholder
            print(f"[TEMPLATE DEBUG] Element {element_name} is leaf element")
            result_parts.append(f"{indent}{placeholder}")

        return '\n'.join(result_parts)

    def extract_element_names_from_output_xml(self, output_xml: str) -> List[str]:
        """
        Extract all element names from output XML for processing list
        """
        print(f"[TEMPLATE DEBUG] Extracting element names from output XML")

        try:
            root = etree.fromstring(output_xml.encode('utf-8'))
            element_names = []

            def collect_elements(element):
                element_name = element.tag
                if '}' in element_name:
                    element_name = element_name.split('}')[1]  # Remove namespace

                element_names.append(element_name)
                for child in element:
                    collect_elements(child)

            collect_elements(root)

            # Remove duplicates while preserving order
            unique_names = []
            seen = set()
            for name in element_names:
                if name not in seen:
                    unique_names.append(name)
                    seen.add(name)

            print(f"[TEMPLATE DEBUG] Found {len(unique_names)} unique elements: {unique_names}")
            return unique_names

        except Exception as e:
            print(f"[TEMPLATE DEBUG] ERROR extracting element names: {e}")
            return []


class ChunkExtractor:
    """
    Extracts XSLT chunks using line-by-line traversal algorithm
    """

    def __init__(self):
        self.debug = True

    def extract_chunk_for_element(self, xslt_string: str, target_element: str) -> Optional[str]:
        """
        Extract XSLT chunk for target element using line-by-line traversal

        Args:
            xslt_string: Generated XSLT content
            target_element: Element name to extract chunk for

        Returns:
            str: Extracted XSLT chunk or None if not found
        """
        print(f"[EXTRACTION DEBUG] ===== EXTRACTING CHUNK FOR {target_element} =====")
        print(f"[EXTRACTION DEBUG] XSLT length: {len(xslt_string)} characters")

        if not xslt_string.strip():
            print(f"[EXTRACTION DEBUG] Empty XSLT string, skipping extraction")
            return None

        # Split into lines for processing
        lines = xslt_string.strip().split('\n')
        print(f"[EXTRACTION DEBUG] Split XSLT into {len(lines)} lines")

        # Find target element line
        target_line_index = self._find_element_line(lines, target_element)

        if target_line_index is None:
            print(f"[EXTRACTION DEBUG] Element {target_element} not found in XSLT")
            return None

        print(f"[EXTRACTION DEBUG] Found {target_element} at line {target_line_index + 1}")
        print(f"[EXTRACTION DEBUG] Target line content: '{lines[target_line_index].strip()}'")

        # Traverse up to find first closing tag
        boundary_line_index = self._traverse_up_for_closing_tag(lines, target_line_index)

        # Determine extraction boundaries
        start_line, end_line = self._determine_extraction_boundaries(
            lines, target_line_index, boundary_line_index
        )

        # Extract chunk
        chunk = self._extract_chunk_from_lines(lines, start_line, end_line, target_element)

        print(f"[EXTRACTION DEBUG] Extracted chunk length: {len(chunk)} characters")
        print(f"[EXTRACTION DEBUG] ===== EXTRACTION COMPLETE =====")

        return chunk

    def _find_element_line(self, lines: List[str], target_element: str) -> Optional[int]:
        """
        Find line index containing target element opening tag
        """
        print(f"[EXTRACTION DEBUG] Searching for element: <{target_element}>")

        for i, line in enumerate(lines):
            # Look for opening tag patterns
            if f'<{target_element}>' in line or f'<{target_element} ' in line:
                print(f"[EXTRACTION DEBUG] Found element at line {i + 1}: '{line.strip()}'")
                return i

        print(f"[EXTRACTION DEBUG] Element {target_element} not found in XSLT lines")
        return None

    def _traverse_up_for_closing_tag(self, lines: List[str], target_line_index: int) -> Optional[int]:
        """
        Traverse up from target line to find first closing tag
        """
        print(f"[EXTRACTION DEBUG] Traversing up from line {target_line_index + 1}")

        for i in range(target_line_index - 1, -1, -1):
            line = lines[i].strip()
            print(f"[EXTRACTION DEBUG] Checking line {i + 1}: '{line}'")

            # Look for any closing tag
            if '</' in line:
                print(f"[EXTRACTION DEBUG] Found closing tag at line {i + 1}: '{line}'")
                return i

        print(f"[EXTRACTION DEBUG] No closing tag found above target line")
        return None

    def _determine_extraction_boundaries(self, lines: List[str], target_line_index: int,
                                       boundary_line_index: Optional[int]) -> Tuple[int, int]:
        """
        Determine start and end lines for extraction
        """
        if boundary_line_index is None:
            # No closing tag found - extract from target element line
            start_line = target_line_index
            print(f"[EXTRACTION DEBUG] No boundary found, starting from target line {start_line + 1}")
        else:
            # Found closing tag - extract from next line down
            start_line = boundary_line_index + 1
            print(f"[EXTRACTION DEBUG] Boundary found, starting from line {start_line + 1}")

        # Find corresponding closing tag for extraction
        end_line = self._find_corresponding_closing_tag(lines, start_line)

        print(f"[EXTRACTION DEBUG] Extraction boundaries: lines {start_line + 1} to {end_line + 1}")
        return start_line, end_line

    def _find_corresponding_closing_tag(self, lines: List[str], start_line: int) -> int:
        """
        Find corresponding closing tag for the opening tag at start_line
        """
        start_line_content = lines[start_line].strip()
        print(f"[EXTRACTION DEBUG] Finding closing tag for: '{start_line_content}'")

        # Extract tag name from opening tag
        if '<' in start_line_content:
            tag_match = re.search(r'<([^>\s]+)', start_line_content)
            if tag_match:
                tag_name = tag_match.group(1)
                closing_tag = f'</{tag_name}>'
                print(f"[EXTRACTION DEBUG] Looking for closing tag: '{closing_tag}'")

                # Search for corresponding closing tag
                for i in range(start_line + 1, len(lines)):
                    if closing_tag in lines[i]:
                        print(f"[EXTRACTION DEBUG] Found closing tag at line {i + 1}")
                        return i

        # Fallback: return start line if no closing tag found
        print(f"[EXTRACTION DEBUG] No closing tag found, using start line as end")
        return start_line

    def _extract_chunk_from_lines(self, lines: List[str], start_line: int,
                                 end_line: int, target_element: str) -> str:
        """
        Extract chunk from lines and format properly
        """
        extracted_lines = lines[start_line:end_line + 1]
        chunk = '\n'.join(extracted_lines)

        print(f"[EXTRACTION DEBUG] Extracted {len(extracted_lines)} lines for {target_element}")
        if self.debug and len(chunk) < 500:  # Only show small chunks in debug
            print(f"[EXTRACTION DEBUG] Chunk content:\n{chunk}")

        return chunk

    def remove_chunk_from_xslt(self, xslt_string: str, chunk: str) -> str:
        """
        Remove extracted chunk from XSLT string to prevent conflicts
        """
        print(f"[EXTRACTION DEBUG] Removing chunk from XSLT (chunk length: {len(chunk)})")

        # Simple string replacement for now
        modified_xslt = xslt_string.replace(chunk, '', 1)

        print(f"[EXTRACTION DEBUG] XSLT length before removal: {len(xslt_string)}")
        print(f"[EXTRACTION DEBUG] XSLT length after removal: {len(modified_xslt)}")

        return modified_xslt


class TemplateReplacer:
    """
    Handles direct template replacement and conflict detection
    """

    def __init__(self):
        self.debug = True
        self.element_chunks: Dict[str, List[str]] = {}  # Track multiple chunks per element

    def replace_placeholder_with_chunk(self, base_template: str, element_name: str, chunk: str) -> str:
        """
        Replace placeholder in base template with extracted chunk

        Args:
            base_template: XSLT template with placeholders
            element_name: Target element name
            chunk: Extracted XSLT chunk

        Returns:
            str: Updated template
        """
        print(f"[REPLACEMENT DEBUG] ===== REPLACING PLACEHOLDER FOR {element_name} =====")

        placeholder = f"{{{{PLACEHOLDER_{element_name}}}}}"
        print(f"[REPLACEMENT DEBUG] Looking for placeholder: {placeholder}")
        print(f"[REPLACEMENT DEBUG] Chunk length: {len(chunk)} characters")

        if placeholder in base_template:
            updated_template = base_template.replace(placeholder, chunk, 1)
            print(f"[REPLACEMENT DEBUG] Placeholder replaced successfully")
            print(f"[REPLACEMENT DEBUG] Template length before: {len(base_template)}")
            print(f"[REPLACEMENT DEBUG] Template length after: {len(updated_template)}")
            return updated_template
        else:
            print(f"[REPLACEMENT DEBUG] WARNING: Placeholder {placeholder} not found in template")
            return base_template

    def add_chunk_for_element(self, element_name: str, chunk: str):
        """
        Add chunk for element, detecting conflicts
        """
        print(f"[REPLACEMENT DEBUG] Adding chunk for element: {element_name}")

        if element_name not in self.element_chunks:
            self.element_chunks[element_name] = []

        self.element_chunks[element_name].append(chunk)
        chunk_count = len(self.element_chunks[element_name])

        if chunk_count > 1:
            print(f"[REPLACEMENT DEBUG] CONFLICT DETECTED: Element {element_name} has {chunk_count} chunks")
        else:
            print(f"[REPLACEMENT DEBUG] First chunk added for element {element_name}")

    def get_conflicts(self) -> Dict[str, List[str]]:
        """
        Get elements with multiple chunks (conflicts)
        """
        conflicts = {
            element: chunks for element, chunks in self.element_chunks.items()
            if len(chunks) > 1
        }

        print(f"[REPLACEMENT DEBUG] Found {len(conflicts)} conflicts")
        for element, chunks in conflicts.items():
            print(f"[REPLACEMENT DEBUG] Conflict: {element} has {len(chunks)} chunks")

        return conflicts

    def get_resolved_chunks(self) -> Dict[str, str]:
        """
        Get single chunk per element (after conflict resolution)
        """
        resolved = {}
        for element, chunks in self.element_chunks.items():
            if len(chunks) == 1:
                resolved[element] = chunks[0]
            # Note: Conflicts need to be resolved separately

        print(f"[REPLACEMENT DEBUG] {len(resolved)} elements have single chunks")
        return resolved


class ConflictResolver:
    """
    Resolves conflicts using LLM when multiple chunks target same element
    """

    def __init__(self):
        self.debug = True

    def resolve_conflict_with_llm(self, element_name: str, conflicting_chunks: List[str]) -> str:
        """
        Use LLM to resolve conflict between multiple chunks for same element

        Args:
            element_name: Element that has conflicting chunks
            conflicting_chunks: List of XSLT chunks that all generate same element

        Returns:
            str: Resolved XSLT chunk chosen or merged by LLM
        """
        print(f"[CONFLICT DEBUG] ===== RESOLVING CONFLICT FOR {element_name} =====")
        print(f"[CONFLICT DEBUG] Number of conflicting chunks: {len(conflicting_chunks)}")

        # Format chunks for LLM prompt
        formatted_chunks = []
        for i, chunk in enumerate(conflicting_chunks):
            formatted_chunks.append(f"Chunk {i + 1}:\n{chunk}\n")

        chunks_text = "\n".join(formatted_chunks)

        # Create LLM prompt for conflict resolution
        prompt = f"""
You are an XSLT expert resolving conflicts between multiple XSLT approaches for the same output element.

Element: {element_name}

Multiple XSLT chunks have been generated for this element:

{chunks_text}

Your task:
1. Analyze each chunk's approach and logic
2. Choose the BEST chunk that should be used, OR
3. Merge the chunks if they complement each other

Return ONLY the final XSLT chunk that should be used for this element.
Do not include explanations or comments, just the XSLT code.
"""

        try:
            print(f"[CONFLICT DEBUG] Sending conflict resolution request to LLM")

            response = get_chat_completion([
                {"role": "system", "content": "You are an expert XSLT processor that resolves conflicts between multiple XSLT approaches."},
                {"role": "user", "content": prompt}
            ])

            resolved_chunk = response.choices[0].message.content.strip()

            print(f"[CONFLICT DEBUG] LLM resolved conflict successfully")
            print(f"[CONFLICT DEBUG] Resolved chunk length: {len(resolved_chunk)} characters")

            return resolved_chunk

        except Exception as e:
            print(f"[CONFLICT DEBUG] ERROR during LLM conflict resolution: {e}")
            print(f"[CONFLICT DEBUG] Falling back to first chunk")
            return conflicting_chunks[0]  # Fallback to first chunk

    def resolve_all_conflicts(self, conflicts: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Resolve all detected conflicts using LLM

        Args:
            conflicts: Dictionary of element_name -> list of conflicting chunks

        Returns:
            Dict[str, str]: Dictionary of element_name -> resolved chunk
        """
        print(f"[CONFLICT DEBUG] Resolving {len(conflicts)} conflicts")

        resolved = {}
        for element_name, chunks in conflicts.items():
            print(f"[CONFLICT DEBUG] Resolving conflict for {element_name}")
            resolved_chunk = self.resolve_conflict_with_llm(element_name, chunks)
            resolved[element_name] = resolved_chunk

        print(f"[CONFLICT DEBUG] All conflicts resolved")
        return resolved


class HybridTemplateMerger:
    """
    Main orchestrator for hybrid template-based XSLT merging
    """

    def __init__(self):
        self.template_generator = BaseTemplateGenerator()
        self.chunk_extractor = ChunkExtractor()
        self.template_replacer = TemplateReplacer()
        self.conflict_resolver = ConflictResolver()
        self.debug = True

    def merge_xslt_batches_with_template(self, generated_xslt: str, output_xml: str,
                                       element_list: List[str]) -> str:
        """
        Main entry point for hybrid template-based merging

        Args:
            generated_xslt: XSLT generated from parallel processing
            output_xml: Expected output XML structure
            element_list: List of elements to process

        Returns:
            str: Final merged XSLT with correct element ordering
        """
        print(f"[HYBRID DEBUG] ===== STARTING HYBRID TEMPLATE MERGE =====")
        print(f"[HYBRID DEBUG] Generated XSLT length: {len(generated_xslt)} characters")
        print(f"[HYBRID DEBUG] Processing {len(element_list)} elements")
        print(f"[HYBRID DEBUG] Elements to process: {element_list}")

        try:
            # Step 1: Create base template from output XML
            print(f"[HYBRID DEBUG] Step 1: Creating base template")
            base_template = self.template_generator.create_base_template_from_output_xml(output_xml)

            # Step 2: Process each element - extract chunks
            print(f"[HYBRID DEBUG] Step 2: Processing elements and extracting chunks")
            current_xslt = generated_xslt
            processed_count = 0

            for element_name in element_list:
                print(f"[HYBRID DEBUG] Processing element {processed_count + 1}/{len(element_list)}: {element_name}")

                # Extract chunk for this element
                chunk = self.chunk_extractor.extract_chunk_for_element(current_xslt, element_name)

                if chunk:
                    # Add chunk (this handles conflict detection)
                    self.template_replacer.add_chunk_for_element(element_name, chunk)

                    # Remove chunk from XSLT to prevent future conflicts
                    current_xslt = self.chunk_extractor.remove_chunk_from_xslt(current_xslt, chunk)
                    processed_count += 1
                else:
                    print(f"[HYBRID DEBUG] Element {element_name} not found (likely already processed)")

            print(f"[HYBRID DEBUG] Processed {processed_count} elements successfully")

            # Step 3: Resolve conflicts
            print(f"[HYBRID DEBUG] Step 3: Resolving conflicts")
            conflicts = self.template_replacer.get_conflicts()

            if conflicts:
                print(f"[HYBRID DEBUG] Resolving {len(conflicts)} conflicts with LLM")
                resolved_conflicts = self.conflict_resolver.resolve_all_conflicts(conflicts)
            else:
                print(f"[HYBRID DEBUG] No conflicts detected")
                resolved_conflicts = {}

            # Step 4: Replace all placeholders
            print(f"[HYBRID DEBUG] Step 4: Replacing placeholders in template")
            final_template = base_template

            # Replace resolved conflicts first
            for element_name, resolved_chunk in resolved_conflicts.items():
                final_template = self.template_replacer.replace_placeholder_with_chunk(
                    final_template, element_name, resolved_chunk
                )

            # Replace non-conflicting elements
            resolved_chunks = self.template_replacer.get_resolved_chunks()
            for element_name, chunk in resolved_chunks.items():
                final_template = self.template_replacer.replace_placeholder_with_chunk(
                    final_template, element_name, chunk
                )

            print(f"[HYBRID DEBUG] Final template length: {len(final_template)} characters")
            print(f"[HYBRID DEBUG] ===== HYBRID TEMPLATE MERGE COMPLETE =====")

            return final_template

        except Exception as e:
            print(f"[HYBRID DEBUG] ERROR during hybrid merge: {e}")
            print(f"[HYBRID DEBUG] Falling back to original XSLT")
            return generated_xslt