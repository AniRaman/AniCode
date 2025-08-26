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
    
    def process_chunk_intelligently(self, chunk_text: str, llm_function) -> str:
        """Process chunk using rules-first + placeholder approach."""
        self.stats['chunks_processed'] += 1
        
        # Step 1: Apply rules to the whole chunk first
        from .refine_cache import rule_based_refine, replace_placeholders
        
        try:
            print("Initial Chunk", chunk_text)
            chunk_with_placeholders, actions, placeholder_map = rule_based_refine(chunk_text)
            print("Placeholder Map", placeholder_map)
            print("chunk_with_placeholders", chunk_with_placeholders)
            if actions:
                print(f"Rules applied: {len(actions)} optimizations performed")
                self.stats['simple_patterns_optimized'] += len(actions)
                print(f"DEBUG - Original length: {len(chunk_text)} chars")
            else:
                print("No rules applied, using original chunk")
        except Exception as e:
            print(f"Rules processing failed: {e}, using original chunk")
            chunk_with_placeholders = chunk_text
            placeholder_map = {}
            actions = []
        
        print(f"Created {len(placeholder_map)} rule placeholders")
        
        # Step 2.5: Decide if LLM processing is worthwhile  
        should_call_llm = self._should_send_to_llm(chunk_text, actions, chunk_with_placeholders, placeholder_map)
        
        if not should_call_llm:
            print("SKIPPING LLM: Chunk already optimally processed by rules")
            # Replace placeholders to get final optimized result
            final_result = replace_placeholders(chunk_with_placeholders, placeholder_map) if placeholder_map else chunk_with_placeholders
            print(f"DEBUG: Rules-only path - replaced {len(placeholder_map)} placeholders")
            print(f"DEBUG: Final result contains optimized union selectors and merged patterns")
            
            print("=== MERGED XSLT FOR RULES-ONLY DEBUG ===")
            print(final_result)
            print("=== END MERGED XSLT DEBUG ===")
            
            return final_result
        
        #Debug: Show placeholder details
        if placeholder_map:
            print("DEBUG - Placeholder map:")
            for placeholder, content in placeholder_map.items():
                print(f"  {placeholder}: {len(content)} chars")
            print(f"DEBUG - Chunk with placeholders length: {len(chunk_with_placeholders)} chars")
            print(f"DEBUG - Chunk with placeholders preview:\n{chunk_with_placeholders[:500]}...")
        
        # Debug: Show first 500 chars of rules result if different from original
        #if rules_result != chunk_text:
            #print(f"DEBUG - Rules result preview:\n{rules_result[:500]}...")
            #print(f"DEBUG - Original preview:\n{chunk_text[:500]}...")
        
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
        final_result = replace_placeholders(llm_result, placeholder_map) if placeholder_map else llm_result
        print(f"DEBUG: Replaced {len(placeholder_map)} placeholders in LLM result")
        
        print("=== MERGED XSLT FOR LLM DEBUG ===")
        print(final_result)
        print("=== END MERGED XSLT DEBUG ===")
        
        return final_result
    
    def _should_send_to_llm(self, original_chunk: str, actions: list, chunk_with_placeholders: str, placeholder_map: dict) -> bool:
        """Multi-factor analysis to determine if LLM processing is worthwhile."""
        
        # Factor 1: Rules effectiveness (your line-reduction idea enhanced)
        print("Original chunk of Org chunk: " + str(len(original_chunk)))  # Original length
        cleaned_chunk_org = "\n".join(line.strip() for line in original_chunk.splitlines() if line.strip())
        print("Cleaned chunk of Org chunk: " + str(len(cleaned_chunk_org)))
        original_size = len(cleaned_chunk_org)

        # Calculate rules result only when needed for size comparison
        from .refine_cache import replace_placeholders
        rules_result = replace_placeholders(chunk_with_placeholders, placeholder_map) if placeholder_map else chunk_with_placeholders
        print("Original chunk of rules result: " + str(len(rules_result)))  # Original length
        cleaned_chunk_rules = "\n".join(line.strip() for line in rules_result.splitlines() if line.strip())
        print("Cleaned chunk of rules result: " + str(len(cleaned_chunk_rules)))
        rules_size = len(cleaned_chunk_rules)
        
        size_reduction = (original_size - rules_size) / original_size if original_size > 0 else 0
        
        # Factor 2: Rules action count vs potential patterns
        xslt_constructs = self._count_xslt_constructs(original_chunk)
        rules_effectiveness = len(actions) / max(1, xslt_constructs) if xslt_constructs > 0 else 0
        
        # Factor 3: Complexity analysis of remaining chunk
        remaining_complexity = self._calculate_complexity_score(rules_result)
          
        # Factor 4: Size threshold - very small chunks unlikely to benefit
        is_too_small = len(cleaned_chunk_rules) < 200
        
        print(f"LLM Decision Factors:")
        print(f"  Size reduction from rules: {size_reduction:.2f}")
        print(f"  Rules effectiveness: {rules_effectiveness:.2f}")
        print(f"  Remaining complexity: {remaining_complexity:.2f}")
        print(f"  Too small: {is_too_small}")
        
        # Decision logic: Skip LLM if multiple factors indicate low value
        skip_conditions = [
            size_reduction > 0.25,  # Rules reduced by 20%+ = some optimization happened
            rules_effectiveness > 0.3,  # Rules handled 30%+ of patterns (more lenient)
            remaining_complexity > 0.3,  # Low to medium complexity remaining
            is_too_small  # Tiny chunks rarely benefit
        ]
        
        # Enhanced skip logic: More aggressive for obviously simple cases
        if size_reduction >= 0.3:
            print("  STRONG SKIP: Size reduction detected")
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
  
    
    def learn_from_llm_output(self, original_chunk: str, llm_optimized: str):
        """Learn from LLM output to potentially create new rules."""
        try:
            # Analyze the transformation for rule potential
            transformation_type = self._analyze_transformation(original_chunk, llm_optimized)
            
            if transformation_type:
                # Count transformations for statistics
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