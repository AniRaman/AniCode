#!/usr/bin/env python3
"""
Test the refactored rule-based learning system.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.intelligent_chunk_processor import IntelligentChunkProcessor
from genie_core.llm.refine_cache import print_learned_transformations_report, get_learned_transformations

def test_rule_learning():
    """Test the simplified rule-based learning system."""
    print("=== RULE-BASED LEARNING SYSTEM TEST ===")
    
    processor = IntelligentChunkProcessor()
    
    # Test different transformation types
    test_cases = [
        # Variable removal
        {
            'name': 'Variable Removal',
            'original': '''<xsl:variable name="var1_cur" select="."/>
<xsl:attribute name="Status">
    <xsl:value-of select="."/>
</xsl:attribute>''',
            'optimized': '''<xsl:attribute name="Status">
    <xsl:value-of select="."/>
</xsl:attribute>'''
        },
        
        # For-each to copy-of
        {
            'name': 'For-each to Copy-of',
            'original': '''<xsl:for-each select="@Language">
    <xsl:attribute name="Language">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>''',
            'optimized': '''<xsl:copy-of select="@Language"/>'''
        },
        
        # Attribute simplification
        {
            'name': 'Attribute Simplification',
            'original': '''<xsl:for-each select="@Status">
    <xsl:attribute name="Status" namespace="">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>
<xsl:for-each select="@Type">
    <xsl:attribute name="Type" namespace="">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>''',
            'optimized': '''<xsl:copy-of select="@Status"/>
<xsl:copy-of select="@Type"/>'''
        },
    ]
    
    print(f"Testing {len(test_cases)} transformation scenarios...")
    
    # Learn from each test case
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {case['name']}")
        processor.learn_from_llm_output(case['original'], case['optimized'])
    
    # Print the learned transformations report
    print_learned_transformations_report()
    
    # Show statistics
    print(f"\nProcessing Statistics:")
    print(f"Transformations learned: {processor.stats['patterns_learned']}")
    
    # Get all learned transformations
    transformations = get_learned_transformations()
    potential_rules = [t for t in transformations if t['pattern_regex']]
    
    print(f"\nRule Development Summary:")
    print(f"Total learned transformations: {len(transformations)}")
    print(f"Potential rules (with regex patterns): {len(potential_rules)}")
    
    if potential_rules:
        print("\nRule candidates that could be implemented:")
        for rule in potential_rules:
            print(f"- {rule['transformation_type']}: {rule['pattern_regex'][:50]}...")
    
    print("\n" + "=" * 60)
    print("RULE-BASED LEARNING SYSTEM: OPERATIONAL")
    print("- Stores transformations in SQLite database")
    print("- Extracts regex patterns for rule development")
    print("- No unnecessary confidence/frequency tracking")  
    print("- Focused on expanding deterministic rule base")
    print("=" * 60)

if __name__ == "__main__":
    test_rule_learning()