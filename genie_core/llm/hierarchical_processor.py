"""
Hierarchical XSLT Processing System

This module implements a hierarchical approach to processing large XSLT templates:
1. Template-level analysis: Identify overall structure and patterns
2. Block-level processing: Group logical units (for-each blocks, attribute groups)
3. Semantic chunking: Create chunks based on logical boundaries
4. Pattern recognition: Identify and optimize recurring patterns across blocks

This approach reduces LLM dependency by handling more patterns deterministically.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from lxml import etree
from enum import Enum

class BlockType(Enum):
    """Types of logical blocks identified in XSLT templates."""
    TEMPLATE_HEADER = "template_header"
    TEMPLATE_FOOTER = "template_footer"
    ATTRIBUTE_MAPPING = "attribute_mapping"
    ELEMENT_COPYING = "element_copying"
    CONDITIONAL_LOGIC = "conditional_logic"
    LOOP_BLOCK = "loop_block"
    COMPLEX_TRANSFORMATION = "complex_transformation"
    VARIABLE_DECLARATIONS = "variable_declarations"
    NAMESPACE_DECLARATIONS = "namespace_declarations"

class ProcessingStrategy(Enum):
    """Processing strategies for different block types."""
    RULE_BASED = "rule_based"
    LLM_REQUIRED = "llm_required"
    HYBRID = "hybrid"

@dataclass
class TemplateBlock:
    """Represents a logical block within an XSLT template."""
    block_type: BlockType
    content: str
    start_pos: int
    end_pos: int
    processing_strategy: ProcessingStrategy
    patterns: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    optimization_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TemplateStructure:
    """Represents the hierarchical structure of an XSLT template."""
    template_type: str
    total_size: int
    blocks: List[TemplateBlock] = field(default_factory=list)
    global_patterns: Dict[str, int] = field(default_factory=dict)
    namespaces: Dict[str, str] = field(default_factory=dict)
    variables: List[str] = field(default_factory=list)
    complexity_score: float = 0.0

class HierarchicalProcessor:
    """Main class for hierarchical XSLT processing."""
    
    def __init__(self):
        self.mapforce_patterns = self._initialize_mapforce_patterns()
        self.optimization_rules = self._initialize_optimization_rules()
        self.block_processors = self._initialize_block_processors()
    
    def _initialize_mapforce_patterns(self) -> Dict[str, str]:
        """Initialize known Mapforce XSLT patterns."""
        return {
            'variable_cur': r'<xsl:variable\s+name="var\d+_cur"\s+select="\."/?>',
            'variable_initial': r'<xsl:variable\s+name="var\d+_initial"\s+select="\."/?>',
            'attribute_mapping': r'<xsl:for-each\s+select="@(\w+)">\s*<xsl:attribute\s+name="\1"[^>]*>\s*<xsl:value-of\s+select="\."/>\s*</xsl:attribute>\s*</xsl:for-each>',
            'simple_element_copy': r'<xsl:for-each\s+select="([^"]+)">\s*<(\w+)>\s*<xsl:value-of\s+select="\."/>\s*</\2>\s*</xsl:for-each>',
            'namespace_attribute': r'<xsl:for-each\s+select="([^"]+)/@(\w+)">\s*<xsl:attribute\s+name="\2"[^>]*>\s*<xsl:value-of\s+select="\."/>\s*</xsl:attribute>\s*</xsl:for-each>',
            'boolean_conversion': r'<xsl:value-of\s+select="boolean\(translate\(normalize-space\(string\(\.\)\),\s*\'[^\']*\',\s*\'[^\']*\'\)\)"/>',
            'number_conversion': r'<xsl:value-of\s+select="number\(\.\)"/>',
            'empty_element': r'<xsl:for-each\s+select="([^"]+)">\s*<(\w+)/>\s*</xsl:for-each>',
        }
    
    def _initialize_optimization_rules(self) -> Dict[str, callable]:
        """Initialize optimization rules for different patterns."""
        return {
            'variable_cur': self._optimize_variable_cur,
            'attribute_mapping': self._optimize_attribute_mapping,
            'simple_element_copy': self._optimize_simple_element_copy,
            'namespace_attribute': self._optimize_namespace_attribute,
            'boolean_conversion': self._optimize_boolean_conversion,
            'number_conversion': self._optimize_number_conversion,
            'empty_element': self._optimize_empty_element,
        }
    
    def _initialize_block_processors(self) -> Dict[BlockType, callable]:
        """Initialize processors for different block types."""
        return {
            BlockType.TEMPLATE_HEADER: self._process_template_header,
            BlockType.TEMPLATE_FOOTER: self._process_template_footer,
            BlockType.ATTRIBUTE_MAPPING: self._process_attribute_mapping,
            BlockType.ELEMENT_COPYING: self._process_element_copying,
            BlockType.CONDITIONAL_LOGIC: self._process_conditional_logic,
            BlockType.LOOP_BLOCK: self._process_loop_block,
            BlockType.COMPLEX_TRANSFORMATION: self._process_complex_transformation,
            BlockType.VARIABLE_DECLARATIONS: self._process_variable_declarations,
        }
    
    def analyze_template(self, template_text: str) -> TemplateStructure:
        """
        Analyze template structure and identify logical blocks.
        
        Args:
            template_text: The XSLT template text to analyze
            
        Returns:
            TemplateStructure with identified blocks and patterns
        """
        print(f"Analyzing template of size: {len(template_text)} characters")
        
        # 1. Identify template type (Mapforce patterns)
        template_type = self._identify_template_type(template_text)
        
        # 2. Extract namespaces and variables
        namespaces = self._extract_namespaces(template_text)
        variables = self._extract_variables(template_text)
        
        # 3. Identify logical blocks
        blocks = self._identify_logical_blocks(template_text)
        
        # 4. Analyze global patterns
        global_patterns = self._analyze_global_patterns(template_text)
        
        # 5. Calculate complexity score
        complexity_score = self._calculate_complexity_score(template_text, blocks)
        
        structure = TemplateStructure(
            template_type=template_type,
            total_size=len(template_text),
            blocks=blocks,
            global_patterns=global_patterns,
            namespaces=namespaces,
            variables=variables,
            complexity_score=complexity_score
        )
        
        print(f"Template analysis complete: {len(blocks)} blocks identified")
        print(f"Template type: {template_type}, Complexity: {complexity_score:.2f}")
        
        return structure
    
    def _identify_template_type(self, template_text: str) -> str:
        """Identify the type of XSLT template (Mapforce, manual, etc.)."""
        # Check for Mapforce indicators
        mapforce_indicators = [
            r'var\d+_cur',
            r'var\d+_initial',
            r'xsl:variable.*select="\."',
            r'xmlns:ns0=',
            r'translate\(normalize-space\(string\(\.\)\)',
        ]
        
        mapforce_score = 0
        for indicator in mapforce_indicators:
            if re.search(indicator, template_text):
                mapforce_score += 1
        
        if mapforce_score >= 3:
            return "mapforce"
        elif mapforce_score >= 1:
            return "mapforce_like"
        else:
            return "manual"
    
    def _extract_namespaces(self, template_text: str) -> Dict[str, str]:
        """Extract namespace declarations from template."""
        namespaces = {}
        
        # Find xmlns declarations
        xmlns_pattern = r'xmlns:([^=]+)="([^"]*)"'
        matches = re.findall(xmlns_pattern, template_text)
        
        for prefix, uri in matches:
            namespaces[prefix] = uri
        
        return namespaces
    
    def _extract_variables(self, template_text: str) -> List[str]:
        """Extract variable declarations from template."""
        variables = []
        
        # Find variable declarations
        var_pattern = r'<xsl:variable\s+name="([^"]+)"[^>]*>'
        matches = re.findall(var_pattern, template_text)
        
        variables.extend(matches)
        return variables
    
    def _identify_logical_blocks(self, template_text: str) -> List[TemplateBlock]:
        """Identify logical blocks within the template."""
        blocks = []
        
        # 1. Template header (everything before first significant for-each)
        header_end = self._find_template_header_end(template_text)
        if header_end > 0:
            blocks.append(TemplateBlock(
                block_type=BlockType.TEMPLATE_HEADER,
                content=template_text[:header_end],
                start_pos=0,
                end_pos=header_end,
                processing_strategy=ProcessingStrategy.RULE_BASED
            ))
        
        # 2. Main processing blocks
        main_blocks = self._identify_main_blocks(template_text, header_end)
        blocks.extend(main_blocks)
        
        # 3. Template footer
        footer_start = self._find_template_footer_start(template_text)
        if footer_start < len(template_text):
            blocks.append(TemplateBlock(
                block_type=BlockType.TEMPLATE_FOOTER,
                content=template_text[footer_start:],
                start_pos=footer_start,
                end_pos=len(template_text),
                processing_strategy=ProcessingStrategy.RULE_BASED
            ))
        
        return blocks
    
    def _find_template_header_end(self, template_text: str) -> int:
        """Find the end of template header section."""
        # Look for first significant for-each or choose
        patterns = [
            r'<xsl:for-each\s+select="[^"]*[^@][^"]*"[^>]*>',
            r'<xsl:choose>',
            r'<xsl:if\s+test="[^"]*[^@][^"]*"[^>]*>',
        ]
        
        earliest_pos = len(template_text)
        for pattern in patterns:
            match = re.search(pattern, template_text)
            if match:
                earliest_pos = min(earliest_pos, match.start())
        
        return earliest_pos if earliest_pos < len(template_text) else 0
    
    def _find_template_footer_start(self, template_text: str) -> int:
        """Find the start of template footer section."""
        # Look for final closing tags
        patterns = [
            r'</xsl:for-each>\s*</[^>]+>\s*</xsl:template>',
            r'</xsl:choose>\s*</[^>]+>\s*</xsl:template>',
        ]
        
        latest_pos = 0
        for pattern in patterns:
            matches = list(re.finditer(pattern, template_text))
            if matches:
                latest_pos = max(latest_pos, matches[-1].start())
        
        return latest_pos if latest_pos > 0 else len(template_text)
    
    def _identify_main_blocks(self, template_text: str, start_pos: int) -> List[TemplateBlock]:
        """Identify main processing blocks in the template."""
        blocks = []
        
        # Find major for-each blocks
        for_each_pattern = r'<xsl:for-each\s+select="([^"]+)"[^>]*>'
        matches = list(re.finditer(for_each_pattern, template_text[start_pos:]))
        
        for match in matches:
            abs_start = start_pos + match.start()
            block_end = self._find_block_end(template_text, abs_start)
            
            if block_end > abs_start:
                block_content = template_text[abs_start:block_end]
                block_type = self._classify_block_type(block_content)
                processing_strategy = self._determine_processing_strategy(block_type, block_content)
                
                blocks.append(TemplateBlock(
                    block_type=block_type,
                    content=block_content,
                    start_pos=abs_start,
                    end_pos=block_end,
                    processing_strategy=processing_strategy,
                    patterns=self._identify_block_patterns(block_content)
                ))
        
        return blocks
    
    def _find_block_end(self, template_text: str, start_pos: int) -> int:
        """Find the end of a logical block starting at start_pos."""
        # Simple approach: find matching </xsl:for-each>
        depth = 0
        pos = start_pos
        
        while pos < len(template_text):
            if template_text[pos:pos+13] == '<xsl:for-each':
                depth += 1
            elif template_text[pos:pos+14] == '</xsl:for-each>':
                depth -= 1
                if depth == 0:
                    return pos + 14
            pos += 1
        
        return len(template_text)
    
    def _classify_block_type(self, block_content: str) -> BlockType:
        """Classify the type of a logical block."""
        # Check for attribute mapping patterns
        if re.search(r'<xsl:attribute\s+name="[^"]*"[^>]*>\s*<xsl:value-of\s+select="[\.@]', block_content):
            return BlockType.ATTRIBUTE_MAPPING
        
        # Check for element copying patterns
        if re.search(r'<\w+>\s*<xsl:value-of\s+select="\."/>\s*</\w+>', block_content):
            return BlockType.ELEMENT_COPYING
        
        # Check for conditional logic
        if re.search(r'<xsl:choose>|<xsl:if\s+test=', block_content):
            return BlockType.CONDITIONAL_LOGIC
        
        # Check for nested loops
        if block_content.count('<xsl:for-each') > 1:
            return BlockType.LOOP_BLOCK
        
        # Default to complex transformation
        return BlockType.COMPLEX_TRANSFORMATION
    
    def _determine_processing_strategy(self, block_type: BlockType, block_content: str) -> ProcessingStrategy:
        """Determine the best processing strategy for a block."""
        if block_type in [BlockType.TEMPLATE_HEADER, BlockType.TEMPLATE_FOOTER, BlockType.VARIABLE_DECLARATIONS]:
            return ProcessingStrategy.RULE_BASED
        
        if block_type == BlockType.ATTRIBUTE_MAPPING:
            # Check if it's a simple attribute mapping pattern
            if self._is_simple_attribute_mapping(block_content):
                return ProcessingStrategy.RULE_BASED
            else:
                return ProcessingStrategy.HYBRID
        
        if block_type == BlockType.ELEMENT_COPYING:
            return ProcessingStrategy.RULE_BASED
        
        if block_type in [BlockType.CONDITIONAL_LOGIC, BlockType.COMPLEX_TRANSFORMATION]:
            return ProcessingStrategy.LLM_REQUIRED
        
        return ProcessingStrategy.HYBRID
    
    def _is_simple_attribute_mapping(self, block_content: str) -> bool:
        """Check if block contains only simple attribute mapping patterns."""
        # Count complex patterns that would require LLM
        complex_patterns = [
            r'<xsl:choose>',
            r'<xsl:if\s+test=',
            r'<xsl:call-template>',
            r'substring\(',
            r'concat\(',
            r'translate\(',
        ]
        
        for pattern in complex_patterns:
            if re.search(pattern, block_content):
                return False
        
        return True
    
    def _identify_block_patterns(self, block_content: str) -> List[str]:
        """Identify patterns within a block."""
        patterns = []
        
        for pattern_name, pattern_regex in self.mapforce_patterns.items():
            if re.search(pattern_regex, block_content):
                patterns.append(pattern_name)
        
        return patterns
    
    def _analyze_global_patterns(self, template_text: str) -> Dict[str, int]:
        """Analyze patterns that occur across the entire template."""
        global_patterns = {}
        
        for pattern_name, pattern_regex in self.mapforce_patterns.items():
            matches = re.findall(pattern_regex, template_text)
            if matches:
                global_patterns[pattern_name] = len(matches)
        
        return global_patterns
    
    def _calculate_complexity_score(self, template_text: str, blocks: List[TemplateBlock]) -> float:
        """Calculate a complexity score for the template."""
        base_score = len(template_text) / 1000  # Base score from size
        
        # Add complexity for different block types
        for block in blocks:
            if block.processing_strategy == ProcessingStrategy.LLM_REQUIRED:
                base_score += 10
            elif block.processing_strategy == ProcessingStrategy.HYBRID:
                base_score += 5
            elif block.processing_strategy == ProcessingStrategy.RULE_BASED:
                base_score += 1
        
        return base_score
    
    # Optimization methods (placeholder implementations)
    def _optimize_variable_cur(self, content: str) -> str:
        """Remove var*_cur variable declarations."""
        return re.sub(r'<xsl:variable\s+name="var\d+_cur"\s+select="\."/?>(\s*\n)?', '', content)
    
    def _optimize_attribute_mapping(self, content: str) -> str:
        """Optimize simple attribute mapping patterns."""
        # Convert for-each attribute patterns to copy-of
        pattern = r'<xsl:for-each\s+select="@(\w+)">\s*<xsl:attribute\s+name="\1"[^>]*>\s*<xsl:value-of\s+select="\."/>\s*</xsl:attribute>\s*</xsl:for-each>'
        replacement = r'<xsl:copy-of select="@\1"/>'
        return re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    def _optimize_simple_element_copy(self, content: str) -> str:
        """Optimize simple element copying patterns."""
        # Placeholder - would implement element copying optimization
        return content
    
    def _optimize_namespace_attribute(self, content: str) -> str:
        """Optimize namespace attribute patterns."""
        # Placeholder - would implement namespace attribute optimization
        return content
    
    def _optimize_boolean_conversion(self, content: str) -> str:
        """Optimize boolean conversion patterns."""
        # Placeholder - would implement boolean conversion optimization
        return content
    
    def _optimize_number_conversion(self, content: str) -> str:
        """Optimize number conversion patterns."""
        # Placeholder - would implement number conversion optimization
        return content
    
    def _optimize_empty_element(self, content: str) -> str:
        """Optimize empty element patterns."""
        # Placeholder - would implement empty element optimization
        return content
    
    # Block processors (placeholder implementations)
    def _process_template_header(self, block: TemplateBlock) -> str:
        """Process template header block."""
        return self._optimize_variable_cur(block.content)
    
    def _process_template_footer(self, block: TemplateBlock) -> str:
        """Process template footer block."""
        return block.content  # Usually no optimization needed
    
    def _process_attribute_mapping(self, block: TemplateBlock) -> str:
        """Process attribute mapping block."""
        content = block.content
        content = self._optimize_variable_cur(content)
        content = self._optimize_attribute_mapping(content)
        return content
    
    def _process_element_copying(self, block: TemplateBlock) -> str:
        """Process element copying block."""
        return self._optimize_simple_element_copy(block.content)
    
    def _process_conditional_logic(self, block: TemplateBlock) -> str:
        """Process conditional logic block - typically requires LLM."""
        return block.content  # Pass through to LLM
    
    def _process_loop_block(self, block: TemplateBlock) -> str:
        """Process loop block."""
        return self._optimize_variable_cur(block.content)
    
    def _process_complex_transformation(self, block: TemplateBlock) -> str:
        """Process complex transformation block - typically requires LLM."""
        return block.content  # Pass through to LLM
    
    def _process_variable_declarations(self, block: TemplateBlock) -> str:
        """Process variable declarations block."""
        return self._optimize_variable_cur(block.content)
    
    def process_template_hierarchically(self, template_text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process template using hierarchical approach.
        
        Args:
            template_text: XSLT template to process
            
        Returns:
            Tuple of (processed_template, processing_report)
        """
        # 1. Analyze template structure
        structure = self.analyze_template(template_text)
        
        # 2. Process each block according to its strategy
        processed_blocks = []
        llm_blocks = []
        rule_based_blocks = []
        
        for block in structure.blocks:
            if block.processing_strategy == ProcessingStrategy.RULE_BASED:
                processor = self.block_processors.get(block.block_type, lambda b: b.content)
                processed_content = processor(block)
                processed_blocks.append(processed_content)
                rule_based_blocks.append(block)
            else:
                # For LLM-required blocks, add to list for batch processing
                llm_blocks.append(block)
                processed_blocks.append(block.content)  # Placeholder
        
        # 3. Reconstruct template
        processed_template = ''.join(processed_blocks)
        
        # 4. Create processing report
        report = {
            'template_type': structure.template_type,
            'total_blocks': len(structure.blocks),
            'rule_based_blocks': len(rule_based_blocks),
            'llm_required_blocks': len(llm_blocks),
            'complexity_score': structure.complexity_score,
            'rule_coverage_percent': (len(rule_based_blocks) / len(structure.blocks) * 100) if structure.blocks else 0,
            'original_size': len(template_text),
            'processed_size': len(processed_template),
            'global_patterns': structure.global_patterns,
            'processing_strategies': {
                'rule_based': [b.block_type.value for b in rule_based_blocks],
                'llm_required': [b.block_type.value for b in llm_blocks]
            }
        }
        
        return processed_template, report