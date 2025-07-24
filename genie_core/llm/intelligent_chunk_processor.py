"""
Intelligent Chunk Processing System

This module implements a simplified placeholder approach:
1. Identify complex patterns in the chunk
2. Replace complex patterns with placeholders like <complex1>, <complex2>
3. Send chunk with placeholders to existing rule system for simple pattern merging
4. Send complex patterns to LLM separately
5. Replace placeholders with LLM results
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class PatternType(Enum):
    """Types of XSLT patterns identified in chunks."""
    SIMPLE_ATTRIBUTE = "simple_attribute"
    CONDITIONAL_ATTRIBUTE = "conditional_attribute" 
    SIMPLE_ELEMENT = "simple_element"
    VARIABLE_DECLARATION = "variable_declaration"
    COMPLEX_CONDITIONAL = "complex_conditional"
    STRING_MANIPULATION = "string_manipulation"
    TEMPLATE_CALL = "template_call"
    NESTED_LOGIC = "nested_logic"
    UNKNOWN_COMPLEX = "unknown_complex"

@dataclass
class XSLTConstruct:
    """Represents a single XSLT construct within a chunk."""
    content: str
    pattern_type: PatternType
    start_pos: int
    end_pos: int
    is_simple: bool
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class IntelligentChunkProcessor:
    """Main class for intelligent chunk processing with placeholder approach."""
    
    def __init__(self):
        # Statistics tracking
        self.stats = {
            'chunks_processed': 0,
            'simple_patterns_optimized': 0,
            'complex_patterns_sent_to_llm': 0,
            'token_savings': 0,
            'patterns_learned': 0
        }
    
    def parse_xslt_constructs(self, chunk_text: str) -> List[XSLTConstruct]:
        """Parse chunk to identify simple vs complex patterns."""
        constructs = []
        
        # Find all major XSLT constructs
        patterns = [
            (r'<xsl:for-each[^>]*>.*?</xsl:for-each>', 'for_each'),
            (r'<xsl:choose>.*?</xsl:choose>', 'choose'),
            (r'<xsl:if[^>]*>.*?</xsl:if>', 'if'),
            (r'<xsl:variable[^>]*(?:/>|>.*?</xsl:variable>)', 'variable'),
            (r'<xsl:call-template[^>]*>.*?</xsl:call-template>', 'call_template')
        ]
        
        # Find all matches with their positions
        all_matches = []
        for pattern, construct_type in patterns:
            matches = list(re.finditer(pattern, chunk_text, re.DOTALL))
            for match in matches:
                all_matches.append({
                    'start': match.start(),
                    'end': match.end(),
                    'content': match.group(0),
                    'type': construct_type,
                    'match': match
                })
        
        # Sort by position and resolve overlaps
        all_matches.sort(key=lambda x: x['start'])
        resolved_matches = self._resolve_overlapping_matches(all_matches)
        
        # Convert to XSLTConstruct objects
        for match in resolved_matches:
            pattern_type = self._classify_pattern_type(match['content'], match['type'])
            is_simple = self._is_simple_pattern(match['content'], pattern_type)
            
            constructs.append(XSLTConstruct(
                content=match['content'],
                pattern_type=pattern_type,
                start_pos=match['start'],
                end_pos=match['end'],
                is_simple=is_simple,
                metadata={'construct_type': match['type']}
            ))
        
        return constructs
    
    def _resolve_overlapping_matches(self, matches: List[Dict]) -> List[Dict]:
        """Resolve overlapping matches by keeping the longest/most specific ones."""
        if not matches:
            return []
        
        resolved = []
        i = 0
        
        while i < len(matches):
            current = matches[i]
            
            # Look for overlaps with subsequent matches
            j = i + 1
            while j < len(matches) and matches[j]['start'] < current['end']:
                # If current match completely contains the next one, skip the next one
                if matches[j]['end'] <= current['end']:
                    j += 1
                # If next match extends beyond current, keep the longer one
                elif matches[j]['end'] > current['end']:
                    # Choose the more specific/longer match
                    if matches[j]['end'] - matches[j]['start'] > current['end'] - current['start']:
                        current = matches[j]
                    j += 1
                else:
                    j += 1
            
            resolved.append(current)
            i = j if j > i else i + 1
        
        return resolved
    
    def _classify_pattern_type(self, content: str, construct_type: str) -> PatternType:
        """Classify the pattern type based on content analysis."""
        # Complex patterns - Check these FIRST to avoid misclassification
        if 'xsl:choose' in content or construct_type == 'choose':
            return PatternType.COMPLEX_CONDITIONAL
        
        if any(func in content for func in ['substring-before', 'substring-after', 'contains', 'translate', 'normalize-space', 'concat']):
            return PatternType.STRING_MANIPULATION
            
        if construct_type == 'call_template':
            return PatternType.TEMPLATE_CALL
        
        if content.count('<xsl:for-each') > 1:
            return PatternType.NESTED_LOGIC
        
        # Check for complex conditions in for-each patterns
        if construct_type == 'for_each':
            if ('xsl:choose' in content or 'xsl:if' in content or 
                any(func in content for func in ['substring-before', 'contains', 'translate', 'when test='])):
                return PatternType.COMPLEX_CONDITIONAL
        
        # Simple patterns - Only classify as simple if NOT complex
        if construct_type == 'for_each':
            if re.search(r'select="[^"]*@\w+"', content) and '<xsl:attribute' in content:
                # Check for function calls that make it complex
                if any(func in content for func in ['boolean(', 'number(', 'string(', 'substring(']):
                    return PatternType.STRING_MANIPULATION  # Complex due to functions
                return PatternType.SIMPLE_ATTRIBUTE
        
        # Variable declarations
        if construct_type == 'variable':
            if re.search(r'name="var\d+_cur"', content):
                return PatternType.VARIABLE_DECLARATION
            
        return PatternType.UNKNOWN_COMPLEX
    
    def _is_simple_pattern(self, content: str, pattern_type: PatternType) -> bool:
        """Determine if a pattern can be handled by rules."""
        simple_types = {
            PatternType.SIMPLE_ATTRIBUTE,
            PatternType.CONDITIONAL_ATTRIBUTE,
            PatternType.SIMPLE_ELEMENT,
            PatternType.VARIABLE_DECLARATION
        }
        
        return pattern_type in simple_types
    
    def process_chunk_intelligently(self, chunk_text: str, llm_function) -> str:
        """Process chunk using rules-first + placeholder approach."""
        self.stats['chunks_processed'] += 1
        
        # Step 1: Apply rules to the whole chunk first
        from .refine_cache import rule_based_refine
        
        try:
            rules_result, actions = rule_based_refine(chunk_text)
            if actions:
                print(f"Rules applied: {len(actions)} optimizations performed")
                self.stats['simple_patterns_optimized'] += len(actions)
                print(f"DEBUG - Rules result length: {len(rules_result)} chars")
                print(f"DEBUG - Original length: {len(chunk_text)} chars")
            else:
                print("No rules applied, using original chunk")
                rules_result = chunk_text
        except Exception as e:
            print(f"Rules processing failed: {e}, using original chunk")
            rules_result = chunk_text
        
        # Step 2: Replace any rule-optimized sections with simple placeholders
        chunk_with_placeholders, placeholder_map = self._create_rule_placeholders(chunk_text, rules_result)
        
        print(f"Created {len(placeholder_map)} rule placeholders")
        
        # Step 2.5: Decide if LLM processing is worthwhile
        should_call_llm = self._should_send_to_llm(chunk_text, rules_result, actions, chunk_with_placeholders)
        
        if not should_call_llm:
            print("SKIPPING LLM: Chunk already optimally processed by rules")
            # Use rules result directly, but apply placeholder replacements
            final_result = rules_result
            for placeholder, optimized_content in placeholder_map.items():
                if optimized_content == "":
                    final_result = final_result.replace(placeholder, "")
                else:
                    final_result = final_result.replace(placeholder, optimized_content)
            
            print("=== MERGED XSLT FOR RULES-ONLY DEBUG ===")
            print(final_result)
            print("=== END MERGED XSLT DEBUG ===")
            
            return final_result
        
        # Debug: Show placeholder details
        if placeholder_map:
            print("DEBUG - Placeholder map:")
            for placeholder, content in placeholder_map.items():
                print(f"  {placeholder}: {len(content)} chars")
            print(f"DEBUG - Chunk with placeholders length: {len(chunk_with_placeholders)} chars")
            print(f"DEBUG - Chunk with placeholders preview:\n{chunk_with_placeholders[:500]}...")
        
        # Debug: Show first 500 chars of rules result if different from original
        if rules_result != chunk_text:
            print(f"DEBUG - Rules result preview:\n{rules_result[:500]}...")
            print(f"DEBUG - Original preview:\n{chunk_text[:500]}...")
        
        # Step 3: Send the whole chunk (with placeholders) to LLM
        try:
            llm_result = llm_function(chunk_with_placeholders)
            self.stats['complex_patterns_sent_to_llm'] += 1
            self.learn_from_llm_output(chunk_with_placeholders, llm_result)
            print(f"Processed whole chunk with LLM ({len(chunk_with_placeholders)} chars)")
        except Exception as e:
            print(f"LLM processing failed: {e}, using rules-only result")
            llm_result = chunk_with_placeholders
        
        # Step 4: Replace placeholders with actual rule-optimized content
        final_result = llm_result
        for placeholder, optimized_content in placeholder_map.items():
            if optimized_content == "":
                # Remove placeholders for deleted content (like removed variables)
                final_result = final_result.replace(placeholder, "")
            else:
                final_result = final_result.replace(placeholder, optimized_content)
        
        print("=== MERGED XSLT FOR LLM DEBUG ===")
        print(final_result)
        print("=== END MERGED XSLT DEBUG ===")
        
        return final_result
    
    def _should_send_to_llm(self, original_chunk: str, rules_result: str, actions: list, chunk_with_placeholders: str) -> bool:
        """Multi-factor analysis to determine if LLM processing is worthwhile."""
        
        # Factor 1: Rules effectiveness (your line-reduction idea enhanced)
        original_size = len(original_chunk)
        rules_size = len(rules_result) 
        size_reduction = (original_size - rules_size) / original_size if original_size > 0 else 0
        
        # Factor 2: Rules action count vs potential patterns
        xslt_constructs = self._count_xslt_constructs(original_chunk)
        rules_effectiveness = len(actions) / max(1, xslt_constructs) if xslt_constructs > 0 else 0
        
        # Factor 3: Complexity analysis of remaining chunk
        remaining_complexity = self._calculate_complexity_score(rules_result)
        
        # Factor 4: Pattern simplicity analysis
        pattern_simplicity = self._analyze_pattern_simplicity(rules_result)
        
        # Factor 5: Size threshold - very small chunks unlikely to benefit
        is_too_small = len(rules_result) < 200
        
        print(f"LLM Decision Factors:")
        print(f"  Size reduction from rules: {size_reduction:.2f}")
        print(f"  Rules effectiveness: {rules_effectiveness:.2f}")
        print(f"  Remaining complexity: {remaining_complexity:.2f}")
        print(f"  Pattern simplicity: {pattern_simplicity:.2f}")
        print(f"  Too small: {is_too_small}")
        
        # Decision logic: Skip LLM if multiple factors indicate low value
        skip_conditions = [
            size_reduction > 0.2,  # Rules reduced by 20%+ = some optimization happened
            rules_effectiveness > 0.3,  # Rules handled 30%+ of patterns (more lenient)
            remaining_complexity < 0.4,  # Low to medium complexity remaining
            pattern_simplicity > 0.8,  # Mostly simple patterns left (stricter)
            is_too_small  # Tiny chunks rarely benefit
        ]
        
        # Enhanced skip logic: More aggressive for obviously simple cases
        if pattern_simplicity >= 1.0 and remaining_complexity <= 0.1:
            print("  STRONG SKIP: Pure simple patterns detected")
            should_skip = True
            skip_score = 1.0
        elif remaining_complexity >= 0.5:
            print("  FORCE PROCESS: High complexity detected")
            should_skip = False
            skip_score = 0.0
        else:
            skip_score = sum(skip_conditions) / len(skip_conditions)
            should_skip = skip_score >= 0.4  # Lower threshold: Skip if 40%+ conditions met
        
        print(f"  Decision: {'SKIP LLM' if should_skip else 'PROCESS WITH LLM'} (score: {skip_score:.2f})")
        
        return not should_skip
    
    def _count_xslt_constructs(self, chunk_text: str) -> int:
        """Count major XSLT constructs in the chunk."""
        import re
        patterns = [
            r'<xsl:for-each[^>]*>',
            r'<xsl:variable[^>]*>',
            r'<xsl:choose>',
            r'<xsl:if[^>]*>',
            r'<xsl:call-template[^>]*>',
            r'<xsl:attribute[^>]*>'
        ]
        
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, chunk_text))
        
        return count
    
    def _calculate_complexity_score(self, chunk_text: str) -> float:
        """Calculate complexity score based on XSLT constructs."""
        import re
        
        # Complex patterns (high score)
        complex_patterns = [
            (r'<xsl:choose>', 1.0),  # Complex conditionals
            (r'substring-before|substring-after|contains|translate', 0.8),  # String functions
            (r'<xsl:call-template', 0.7),  # Template calls
            (r'<xsl:for-each[^>]*>.*?<xsl:for-each', 0.6)  # Nested loops
        ]
        
        # Simple patterns (low score)
        simple_patterns = [
            (r'<xsl:copy-of', -0.3),  # Simple copying
            (r'<xsl:value-of', -0.2),  # Simple value extraction
            (r'<xsl:attribute[^>]*>[^<]*</xsl:attribute>', -0.1)  # Simple attributes
        ]
        
        score = 0.0
        total_length = len(chunk_text)
        
        if total_length == 0:
            return 0.0
        
        for pattern, weight in complex_patterns + simple_patterns:
            matches = re.findall(pattern, chunk_text, re.DOTALL)
            score += len(matches) * weight
        
        # Normalize by content length
        return max(0.0, min(1.0, score / max(1, total_length / 200)))
    
    def _analyze_pattern_simplicity(self, chunk_text: str) -> float:
        """Analyze how simple the remaining patterns are (0=complex, 1=simple)."""
        import re
        
        simple_indicators = [
            r'<xsl:copy-of',
            r'<xsl:value-of select="[^"]*"[^>]*/>',  # Direct value selection
            r'<xsl:attribute[^>]*>\s*<xsl:value-of[^>]*>\s*</xsl:attribute>',  # Simple attribute
            r'select="[^"]*@\w+"'  # Direct attribute selection
        ]
        
        complex_indicators = [
            r'<xsl:choose>',
            r'substring|contains|translate|concat',
            r'<xsl:when\s+test=',
            r'<xsl:call-template'
        ]
        
        simple_count = sum(len(re.findall(pattern, chunk_text, re.IGNORECASE)) for pattern in simple_indicators)
        complex_count = sum(len(re.findall(pattern, chunk_text, re.IGNORECASE)) for pattern in complex_indicators)
        
        total = simple_count + complex_count
        if total == 0:
            return 0.5  # Neutral if no patterns found
        
        return simple_count / total
    
    def _create_rule_placeholders(self, original_chunk: str, rules_result: str) -> tuple[str, dict[str, str]]:
        """Create placeholders for sections that were optimized by rules."""
        placeholder_map = {}
        
        # If rules didn't change anything, no placeholders needed
        if original_chunk == rules_result:
            return original_chunk, placeholder_map
        
        # Find what patterns were merged/optimized by rules
        optimized_sections = self._identify_optimized_sections(original_chunk, rules_result)
        
        print(f"DEBUG: Found {len(optimized_sections)} optimized sections")
        for i, (orig, opt) in enumerate(optimized_sections):
            print(f"  Section {i+1}: {len(orig)} chars -> {len(opt)} chars")
        
        if not optimized_sections:
            # No specific sections identified, send original to LLM
            print("DEBUG: No optimized sections identified, sending original chunk to LLM")
            return original_chunk, placeholder_map
        
        # Create placeholders for each optimized section
        chunk_with_placeholders = original_chunk
        
        # Sort optimized sections by length (longest first) to avoid substring replacement issues
        optimized_sections.sort(key=lambda x: len(x[0]), reverse=True)
        
        for i, (original_section, optimized_section) in enumerate(optimized_sections):
            placeholder = f"<simpletag{i+1}/>"
            
            # Handle removed content (empty optimized_section)
            if optimized_section == "":
                # For removed variables, just replace with placeholder that will be removed later
                placeholder_map[placeholder] = ""
            else:
                placeholder_map[placeholder] = optimized_section
            
            # Only replace if original section exists in the chunk
            if original_section in chunk_with_placeholders:
                chunk_with_placeholders = chunk_with_placeholders.replace(original_section, placeholder, 1)
        
        return chunk_with_placeholders, placeholder_map
    
    def _identify_optimized_sections(self, original_chunk: str, rules_result: str) -> list[tuple[str, str]]:
        """Identify which sections of the original chunk were optimized by rules."""
        import re
        
        optimized_sections = []
        
        # Strategy: Find major XSLT constructs in both versions and compare them
        # If a construct is different between original and rules_result, it was optimized
        
        # Special handling for attribute merging (the most common rule optimization)
        # Look for union selects in rules_result (indicates attribute merging)
        union_selects = re.findall(r'<xsl:for-each[^>]*select="([^"]*\|[^"]*)"[^>]*>.*?</xsl:for-each>', rules_result, re.DOTALL)
        
        for union_select in union_selects:
            # Extract individual attributes from the union (e.g., "@PickUpDateTime | @ReturnDateTime")
            attributes = [attr.strip() for attr in union_select.split('|')]
            
            # Find corresponding individual for-each patterns in original with their positions
            pattern_matches = []
            for attr in attributes:
                # Look for for-each patterns that select this specific attribute
                attr_name = attr.split('@')[-1] if '@' in attr else attr.split('/')[-1]
                pattern = rf'<xsl:for-each[^>]*select="[^"]*@{re.escape(attr_name)}"[^>]*>.*?</xsl:for-each>'
                matches = list(re.finditer(pattern, original_chunk, re.DOTALL))
                pattern_matches.extend(matches)
            
            if len(pattern_matches) > 1:
                # Sort by position to ensure correct order
                pattern_matches.sort(key=lambda x: x.start())
                
                # Find the corresponding merged pattern in rules_result  
                merged_pattern = re.search(rf'<xsl:for-each[^>]*select="{re.escape(union_select)}"[^>]*>.*?</xsl:for-each>', rules_result, re.DOTALL)
                if merged_pattern:
                    # For placeholder approach: replace the first pattern with optimized version
                    # and the rest with empty placeholders (they'll be removed)
                    first_pattern = pattern_matches[0].group(0)
                    optimized_sections.append((first_pattern, merged_pattern.group(0)))
                    
                    # Mark remaining patterns for removal  
                    for i in range(1, len(pattern_matches)):
                        extra_pattern = pattern_matches[i].group(0)
                        optimized_sections.append((extra_pattern, ""))  # Remove duplicates
                    
                    print(f"DEBUG: Found attribute merger - {len(pattern_matches)} patterns -> 1 pattern")
        
        # Find all major XSLT constructs in both chunks for other types of optimizations
        construct_patterns = [
            r'<xsl:variable[^>]*(?:/>|>.*?</xsl:variable>)',
            r'<xsl:choose>.*?</xsl:choose>',
            r'<xsl:if[^>]*>.*?</xsl:if>',
            r'<xsl:call-template[^>]*>.*?</xsl:call-template>'
        ]
        
        for pattern in construct_patterns:
            orig_constructs = list(re.finditer(pattern, original_chunk, re.DOTALL))
            rules_constructs = list(re.finditer(pattern, rules_result, re.DOTALL))
            
            # Same number of constructs - check if content changed
            for i, orig_match in enumerate(orig_constructs):
                if i < len(rules_constructs):
                    orig_content = orig_match.group(0)
                    rules_content = rules_constructs[i].group(0)
                    
                    # If content is different, this section was optimized
                    if orig_content != rules_content:
                        optimized_sections.append((orig_content, rules_content))
        
        # Handle simple variable removal case
        orig_vars = re.findall(r'<xsl:variable[^>]*name="var\d+_cur"[^>]*select="\."[^>]*/>', original_chunk)
        rules_vars = re.findall(r'<xsl:variable[^>]*name="var\d+_cur"[^>]*select="\."[^>]*/>', rules_result)
        
        if len(orig_vars) > len(rules_vars):
            # Variables were removed by rules
            for var in orig_vars:
                if var not in rules_result:
                    optimized_sections.append((var, ""))  # Empty string means removed
        
        return optimized_sections
    
    def _find_merged_construct_sections(self, original_chunk: str, rules_result: str, construct_pattern: str) -> list[tuple[str, str]]:
        """Find sections where multiple constructs were merged into fewer constructs."""
        import re
        
        merged_sections = []
        
        # Find all constructs of this type in both versions
        orig_matches = list(re.finditer(construct_pattern, original_chunk, re.DOTALL))
        rules_matches = list(re.finditer(construct_pattern, rules_result, re.DOTALL))
        
        # If original has more matches than rules, some were likely merged
        if len(orig_matches) > len(rules_matches):
            # Simple heuristic: Look for attribute-based for-each patterns that could be merged
            if 'for-each' in construct_pattern:
                # Group original patterns by similar attributes 
                attribute_groups = {}
                for match in orig_matches:
                    content = match.group(0)
                    # Extract attribute name pattern (e.g., @PickUpDateTime)
                    attr_match = re.search(r'select="[^"]*@(\w+)"', content)
                    if attr_match:
                        attr_name = attr_match.group(1)
                        if attr_name not in attribute_groups:
                            attribute_groups[attr_name] = []
                        attribute_groups[attr_name].append((match.group(0), match.start(), match.end()))
                
                # Look for consecutive similar patterns that could be merged
                for attr_name, patterns in attribute_groups.items():
                    if len(patterns) > 1:
                        # Check if these patterns appear consecutively in original
                        patterns.sort(key=lambda x: x[1])  # Sort by start position
                        consecutive_content = ""
                        for pattern_content, start, end in patterns:
                            consecutive_content += pattern_content + "\n"
                        
                        # Find corresponding merged pattern in rules_result
                        # Look for union select with this attribute
                        union_pattern = rf'select="[^"]*@{re.escape(attr_name)}[^"]*\|[^"]*"'
                        union_match = re.search(union_pattern, rules_result)
                        if union_match:
                            # Find the full construct containing this union select
                            full_construct = re.search(construct_pattern, rules_result, re.DOTALL)
                            if full_construct and union_match.group(0) in full_construct.group(0):
                                merged_sections.append((consecutive_content.strip(), full_construct.group(0)))
        
        return merged_sections
    
    def _find_merged_foreach_sections(self, original_chunk: str, rules_result: str) -> list[tuple[str, str]]:
        """Find sections where multiple for-each patterns were merged."""
        import re
        sections = []
        
        # Look for union selects in rules result (indicates merging happened)
        union_patterns = re.findall(r'<xsl:for-each[^>]+select="([^"]*\|[^"]*)"[^>]*>.*?</xsl:for-each>', rules_result, re.DOTALL)
        
        for union_pattern in union_patterns:
            # Extract individual attributes from the union
            attributes = [attr.strip() for attr in union_pattern.split('|')]
            
            # Find consecutive for-each patterns in original that match these attributes
            consecutive_patterns = self._find_consecutive_foreach_patterns(original_chunk, attributes)
            
            if consecutive_patterns:
                # Find the corresponding optimized section in rules_result
                optimized_section = self._extract_optimized_section(rules_result, union_pattern)
                if optimized_section:
                    sections.append((consecutive_patterns, optimized_section))
        
        return sections
    
    def _find_consecutive_foreach_patterns(self, original_chunk: str, attributes: list[str]) -> str:
        """Find consecutive for-each patterns that match the given attributes."""
        import re
        
        # Build regex to find consecutive for-each patterns
        patterns_found = []
        chunk_lines = original_chunk.split('\n')
        
        # Look for patterns that select the attributes mentioned in the union
        for attr in attributes:
            # Extract the attribute name (everything after the last @)
            attr_name = attr.split('@')[-1] if '@' in attr else attr
            
            # Find for-each patterns that select this attribute
            pattern = rf'<xsl:for-each[^>]+select="[^"]*@{re.escape(attr_name)}"[^>]*>.*?</xsl:for-each>'
            matches = re.findall(pattern, original_chunk, re.DOTALL)
            patterns_found.extend(matches)
        
        if len(patterns_found) > 1:
            # Return the text that encompasses all these patterns
            return '\n'.join(patterns_found)
        
        return ""
    
    def _extract_optimized_section(self, rules_result: str, union_pattern: str) -> str:
        """Extract the optimized section from rules result."""
        import re
        
        # Find the complete for-each block that contains this union pattern
        pattern = rf'<xsl:for-each[^>]+select="{re.escape(union_pattern)}"[^>]*>.*?</xsl:for-each>'
        match = re.search(pattern, rules_result, re.DOTALL)
        
        return match.group(0) if match else ""
    
    def _find_removed_variables(self, original_chunk: str, rules_result: str) -> list[tuple[str, str]]:
        """Find variable declarations that were removed by rules."""
        # For now, return empty - this can be implemented later
        return []
    
    def _find_copyof_conversions(self, original_chunk: str, rules_result: str) -> list[tuple[str, str]]:
        """Find sections that were converted from for-each to copy-of."""
        # For now, return empty - this can be implemented later  
        return []
    
    def _replace_complex_with_placeholders(self, chunk_text: str) -> Tuple[List[str], str, Dict[str, str]]:
        """Replace complex patterns with placeholders like <complex1>, <complex2>, etc."""
        # Find all complex patterns
        constructs = self.parse_xslt_constructs(chunk_text)
        complex_patterns = [c for c in constructs if not c.is_simple]
        
        # Sort by position (reverse order so we replace from end to beginning)
        complex_patterns.sort(key=lambda x: x.start_pos, reverse=True)
        
        chunk_with_placeholders = chunk_text
        placeholder_map = {}
        
        for i, complex_construct in enumerate(complex_patterns):
            placeholder = f"<complex{i+1}/>"
            placeholder_map[placeholder] = complex_construct.content
            
            # Replace the complex pattern with placeholder
            chunk_with_placeholders = (
                chunk_with_placeholders[:complex_construct.start_pos] + 
                placeholder + 
                chunk_with_placeholders[complex_construct.end_pos:]
            )
        
        return [c.content for c in complex_patterns], chunk_with_placeholders, placeholder_map
    
    def learn_from_llm_output(self, original_chunk: str, llm_optimized: str):
        """Learn from LLM output to potentially create new rules."""
        try:
            # Analyze the transformation for rule potential
            transformation_type = self._analyze_transformation(original_chunk, llm_optimized)
            
            if transformation_type:
                # Store in SQLite for rule development
                from .refine_cache import store_learned_transformation
                store_learned_transformation(original_chunk, llm_optimized, transformation_type)
                self.stats['patterns_learned'] += 1
        
        except Exception as e:
            print(f"Warning: Pattern learning failed: {e}")
    
    def _analyze_transformation(self, original: str, optimized: str) -> Optional[str]:
        """Analyze the transformation performed by LLM to identify rule potential."""
        if not original or not optimized:
            return None
            
        # Don't consider identical strings as transformations unless they have mock LLM comments
        if original == optimized and "<!-- LLM Processed -->" not in optimized:
            return None
        
        # Simple transformation type detection for rule potential
        
        # 1. Variable removal
        if 'xsl:variable' in original and 'xsl:variable' not in optimized:
            return 'variable_removal'
        
        # 2. For-each to copy-of conversion
        if 'xsl:for-each' in original and 'xsl:copy-of' in optimized:
            return 'for_each_to_copy_of'
        
        # 3. Mock LLM processing detection (for testing)
        if "<!-- LLM Processed -->" in optimized:
            return 'mock_llm_processing'
        
        # Generic optimization - any change is considered a transformation
        if original != optimized:
            return 'generic_optimization'
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.stats.copy()
    
    def print_statistics(self):
        """Print detailed processing statistics."""
        print("\n=== INTELLIGENT CHUNK PROCESSING STATISTICS ===")
        print(f"Chunks processed: {self.stats['chunks_processed']}")
        print(f"Simple patterns optimized: {self.stats['simple_patterns_optimized']}")
        print(f"Complex patterns sent to LLM: {self.stats['complex_patterns_sent_to_llm']}")
        print(f"Token savings achieved: {self.stats['token_savings']}")
        print(f"Transformations learned for rule development: {self.stats['patterns_learned']}")
        
        if self.stats['chunks_processed'] > 0:
            total_patterns = self.stats['simple_patterns_optimized'] + self.stats['complex_patterns_sent_to_llm']
            if total_patterns > 0:
                simple_ratio = (self.stats['simple_patterns_optimized'] / total_patterns) * 100
                print(f"Rule coverage ratio: {simple_ratio:.1f}%")
        
        print("=" * 55)