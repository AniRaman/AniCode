"""
Intelligent Chunk Processing System

This module implements per-chunk pattern separation and processing:
1. Separates simple patterns from complex patterns within chunks
2. Applies rule-based optimization to simple patterns
3. Sends only complex patterns to LLM with focused context
4. Learns from LLM outputs to expand rule coverage over time

This approach maximizes rule utilization while minimizing LLM token usage.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from lxml import etree
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
    """Main class for intelligent chunk processing with pattern separation."""
    
    def __init__(self):
        self.simple_patterns = self._initialize_simple_patterns()
        self.complex_patterns = self._initialize_complex_patterns()
        
        # Statistics tracking
        self.stats = {
            'chunks_processed': 0,
            'simple_patterns_optimized': 0,
            'complex_patterns_sent_to_llm': 0,
            'token_savings': 0,
            'patterns_learned': 0
        }
    
    def _initialize_simple_patterns(self) -> Dict[str, str]:
        """Initialize patterns that can be handled by rules."""
        return {
            'simple_attribute_for_each': r'<xsl:for-each\s+select="[^"]*@\w+"[^>]*>\s*(?:<xsl:variable[^>]*(?:/>|>[^<]*</xsl:variable>)\s*)?<xsl:attribute\s+name="[^"]*"[^>]*>\s*<xsl:value-of\s+select="\."[^>]*/?>\s*</xsl:attribute>\s*</xsl:for-each>',
            'direct_attribute_copy': r'<xsl:attribute\s+name="([^"]*)"[^>]*>\s*<xsl:value-of\s+select="@\1"[^>]*/?>\s*</xsl:attribute>',
            'variable_cur_declaration': r'<xsl:variable\s+name="var\d+_cur"\s+select="\."[^>]*(?:/>|>[^<]*</xsl:variable>)',
            'simple_element_for_each': r'<xsl:for-each\s+select="[^"]*"[^>]*>\s*(?:<xsl:variable[^>]*(?:/>|>[^<]*</xsl:variable>)\s*)?<(\w+)[^>]*(?:/>|>[^<]*</\1>)\s*</xsl:for-each>',
            'simple_copy_pattern': r'<xsl:for-each\s+select="([^"]*)"[^>]*>\s*(?:<xsl:variable[^>]*(?:/>|>[^<]*</xsl:variable>)\s*)?<(\w+)[^>]*>\s*<xsl:value-of\s+select="\."[^>]*/?>\s*</\2>\s*</xsl:for-each>'
        }
    
    def _initialize_complex_patterns(self) -> Dict[str, str]:
        """Initialize patterns that require LLM processing."""
        return {
            'xsl_choose': r'<xsl:choose>.*?</xsl:choose>',
            'xsl_if_complex': r'<xsl:if\s+test="[^"]*(?:contains|substring|translate|concat)[^"]*"[^>]*>',
            'string_functions': r'(?:substring-before|substring-after|contains|starts-with|translate|normalize-space|concat)\s*\(',
            'template_call': r'<xsl:call-template[^>]*>.*?</xsl:call-template>',
            'complex_value_of': r'<xsl:value-of\s+select="[^"]*(?:contains|substring|translate|boolean|number)\([^"]*"[^>]*/>',
            'nested_for_each': r'<xsl:for-each[^>]*>.*?<xsl:for-each[^>]*>.*?</xsl:for-each>.*?</xsl:for-each>',
            'variable_with_complex_select': r'<xsl:variable[^>]*select="[^"]*(?:contains|substring|translate|boolean|number)\([^"]*"[^>]*(?:/>|>[^<]*</xsl:variable>)'
        }
    
    
    def parse_xslt_constructs(self, chunk_text: str) -> List[XSLTConstruct]:
        """Parse chunk into individual XSLT constructs."""
        constructs = []
        
        # Find all major XSLT constructs
        patterns = [
            (r'<xsl:for-each[^>]*>.*?</xsl:for-each>', 'for_each'),
            (r'<xsl:choose>.*?</xsl:choose>', 'choose'),
            (r'<xsl:if[^>]*>.*?</xsl:if>', 'if'),
            (r'<xsl:variable[^>]*(?:/>|>.*?</xsl:variable>)', 'variable'),
            (r'<xsl:attribute[^>]*>.*?</xsl:attribute>', 'attribute'),
            (r'<xsl:call-template[^>]*>.*?</xsl:call-template>', 'call_template'),
            (r'<xsl:copy-of[^>]*(?:/>|>.*?</xsl:copy-of>)', 'copy_of'),
            (r'<xsl:value-of[^>]*(?:/>|>.*?</xsl:value-of>)', 'value_of')
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
        # Check for learned optimizations first
        from .refine_cache import check_for_learned_pattern
        learned_result = check_for_learned_pattern(content)
        if learned_result:
            # If we have a learned optimization, we know this pattern has been processed before
            # For now, continue with normal classification but this could be optimized
            pass
        
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
                return PatternType.SIMPLE_ATTRIBUTE
        
        # Conditional attribute patterns  
        if construct_type == 'attribute' or (construct_type == 'for_each' and '<xsl:attribute' in content):
            if re.search(r'select="@\w+"', content) and '<xsl:value-of select="."' in content:
                return PatternType.CONDITIONAL_ATTRIBUTE
        
        # Simple element patterns
        if construct_type == 'for_each':
            if re.search(r'<(\w+)[^>]*>\s*<xsl:value-of\s+select="\."', content):
                return PatternType.SIMPLE_ELEMENT
        
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
    
    def separate_patterns(self, constructs: List[XSLTConstruct]) -> Tuple[List[XSLTConstruct], List[XSLTConstruct], List[Tuple[str, int]]]:
        """Separate simple and complex patterns within constructs."""
        simple_patterns = []
        complex_patterns = []
        order = []
        
        for construct in constructs:
            if construct.is_simple:
                simple_patterns.append(construct)
                order.append(('simple', len(simple_patterns) - 1))
            else:
                complex_patterns.append(construct)
                order.append(('complex', len(complex_patterns) - 1))
        
        return simple_patterns, complex_patterns, order
    
    def apply_enhanced_rules(self, simple_patterns: List[XSLTConstruct]) -> List[str]:
        """Apply rule-based optimization to simple patterns."""
        from .refine_cache import rule_based_refine
        
        optimized_results = []
        
        # Group similar patterns for batch optimization
        pattern_groups = self._group_similar_patterns(simple_patterns)
        
        for group in pattern_groups:
            if len(group) == 1:
                # Single pattern - apply rules directly
                pattern_text = group[0].content
                try:
                    optimized_text, actions = rule_based_refine(pattern_text)
                    optimized_results.append(optimized_text)
                    
                    if actions:
                        self.stats['simple_patterns_optimized'] += 1
                except Exception as e:
                    print(f"Warning: Rule optimization failed for pattern: {e}")
                    optimized_results.append(pattern_text)  # Fallback to original
            else:
                # Multiple similar patterns - merge and optimize
                merged_pattern = self._merge_similar_patterns(group)
                try:
                    optimized_text, actions = rule_based_refine(merged_pattern)
                    # Split the result back into individual patterns if needed
                    split_results = self._split_merged_result(optimized_text, len(group))
                    optimized_results.extend(split_results)
                    
                    if actions:
                        self.stats['simple_patterns_optimized'] += len(group)
                except Exception as e:
                    print(f"Warning: Merged rule optimization failed: {e}")
                    # Fallback to individual processing
                    for pattern in group:
                        optimized_results.append(pattern.content)
        
        return optimized_results
    
    def _group_similar_patterns(self, patterns: List[XSLTConstruct]) -> List[List[XSLTConstruct]]:
        """Group similar patterns for batch optimization."""
        groups = []
        
        # Group by pattern type
        type_groups = {}
        for pattern in patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in type_groups:
                type_groups[pattern_type] = []
            type_groups[pattern_type].append(pattern)
        
        # Further group by similarity within each type
        for pattern_type, type_patterns in type_groups.items():
            if pattern_type == PatternType.SIMPLE_ATTRIBUTE:
                # Group attribute patterns by base selector
                attr_groups = {}
                for pattern in type_patterns:
                    base_selector = self._extract_base_selector(pattern.content)
                    if base_selector not in attr_groups:
                        attr_groups[base_selector] = []
                    attr_groups[base_selector].append(pattern)
                
                groups.extend(attr_groups.values())
            else:
                # For other types, group individually for now
                groups.extend([[pattern] for pattern in type_patterns])
        
        return groups
    
    def _extract_base_selector(self, content: str) -> str:
        """Extract base selector from attribute pattern."""
        match = re.search(r'select="([^"]*@)', content)
        if match:
            selector = match.group(1)
            # Remove the @ to get base path
            return selector.rstrip('@')
        return ""
    
    def _merge_similar_patterns(self, patterns: List[XSLTConstruct]) -> str:
        """Merge similar patterns into a single pattern for optimization."""
        if len(patterns) <= 1:
            return patterns[0].content if patterns else ""
        
        # For now, just concatenate patterns - the rule system will handle merging
        merged = "\n".join(pattern.content for pattern in patterns)
        return f"<temp>{merged}</temp>"
    
    def _split_merged_result(self, merged_result: str, expected_count: int) -> List[str]:
        """Split merged optimization result back into individual patterns."""
        # Simple approach: if the result contains merged patterns, split appropriately
        # For now, return the merged result as a single pattern
        return [merged_result]
    
    def send_complex_to_llm(self, complex_pattern: XSLTConstruct, llm_function) -> str:
        """Send complex pattern to LLM for optimization."""
        try:
            # This will be called with the actual LLM function from the main system
            llm_result = llm_function(complex_pattern.content)
            
            self.stats['complex_patterns_sent_to_llm'] += 1
            self.stats['token_savings'] += max(0, len(complex_pattern.content) - len(llm_result))
            
            # Learn from this LLM interaction
            self.learn_from_llm_output(complex_pattern.content, llm_result)
            
            return llm_result
        except Exception as e:
            print(f"Warning: LLM processing failed for complex pattern: {e}")
            return complex_pattern.content  # Fallback to original
    
    def reassemble_chunk(self, optimized_simple: List[str], optimized_complex: List[str], order: List[Tuple[str, int]]) -> str:
        """Reassemble optimized patterns back into a complete chunk."""
        result_parts = []
        
        for order_type, index in order:
            if order_type == 'simple':
                if index < len(optimized_simple):
                    result_parts.append(optimized_simple[index])
            else:  # complex
                if index < len(optimized_complex):
                    result_parts.append(optimized_complex[index])
        print("Reassembled chunk:","\n".join(result_parts))
        return "\n".join(result_parts)
    
    def process_chunk_intelligently(self, chunk_text: str, llm_function) -> str:
        """Main method to process a chunk with intelligent pattern separation."""
        self.stats['chunks_processed'] += 1
        
        # 1. Parse chunk into constructs
        constructs = self.parse_xslt_constructs(chunk_text)
        
        if not constructs:
            return chunk_text  # No recognizable patterns
        
        # 2. Separate simple vs complex patterns
        simple_patterns, complex_patterns, order = self.separate_patterns(constructs)
        
        print(f"Intelligent processing: {len(simple_patterns)} simple, {len(complex_patterns)} complex patterns")
        
        # 3. Apply rules to simple patterns
        optimized_simple = []
        if simple_patterns:
            optimized_simple = self.apply_enhanced_rules(simple_patterns)
        
        # 4. Send complex patterns to LLM individually
        optimized_complex = []
        for complex_pattern in complex_patterns:
            llm_result = self.send_complex_to_llm(complex_pattern, llm_function)
            optimized_complex.append(llm_result)
        
        # 5. Reassemble in original order
        result = self.reassemble_chunk(optimized_simple, optimized_complex, order)
        
        return result
    
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
        
        # 3. Attribute simplification
        original_attr_count = original.count('<xsl:attribute')
        optimized_attr_count = optimized.count('<xsl:attribute')
        if original_attr_count > optimized_attr_count:
            return 'attribute_simplification'
        
        # 4. Choose simplification
        if 'xsl:choose' in original and 'xsl:choose' not in optimized:
            return 'choose_simplification'
        
        # 5. String function optimization
        string_functions = ['substring-before', 'substring-after', 'contains', 'normalize-space']
        original_functions = sum(1 for func in string_functions if func in original)
        optimized_functions = sum(1 for func in string_functions if func in optimized)
        
        if original_functions > optimized_functions:
            return 'string_function_optimization'
        
        # 6. Mock LLM processing detection (for testing)
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