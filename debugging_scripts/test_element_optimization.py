#!/usr/bin/env python3
"""
Test element creation pattern optimization.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.refine_cache import _text_based_for_each_merge

def test_element_optimization():
    """Test the new element creation pattern optimization."""
    print("=== TEST ELEMENT PATTERN OPTIMIZATION ===")
    
    # Test case 1: Simple element copying (should optimize to copy-of)
    test_chunk_1 = '''<xsl:for-each select="ns0:StreetText">
    <xsl:variable name="var33_cur" select="."/>
    <StreetText>
        <xsl:value-of select="."/>
    </StreetText>
</xsl:for-each>'''
    
    print("Test 1 - Simple element copying:")
    print("Original:")
    print(test_chunk_1)
    
    result_1 = _text_based_for_each_merge(test_chunk_1)
    
    print("\nOptimized:")
    print(result_1)
    print(f"Optimized: {'YES' if 'copy-of' in result_1 else 'NO'}")
    print()
    
    # Test case 2: Element with different name (should only remove variable)
    test_chunk_2 = '''<xsl:for-each select="ns0:SourceElement">
    <xsl:variable name="var44_cur" select="."/>
    <TargetElement>
        <xsl:value-of select="."/>
    </TargetElement>
</xsl:for-each>'''
    
    print("Test 2 - Different element names:")
    print("Original:")
    print(test_chunk_2)
    
    result_2 = _text_based_for_each_merge(test_chunk_2)
    
    print("\nOptimized:")
    print(result_2)
    variable_removed = 'var44_cur' not in result_2
    print(f"Variable removed: {'YES' if variable_removed else 'NO'}")
    print()
    
    # Test case 3: Multiple elements in same chunk
    test_chunk_3 = '''<xsl:for-each select="ns0:StreetText">
    <xsl:variable name="var33_cur" select="."/>
    <StreetText>
        <xsl:value-of select="."/>
    </StreetText>
</xsl:for-each>
<xsl:for-each select="ns0:CityName">
    <xsl:variable name="var34_cur" select="."/>
    <CityName>
        <xsl:value-of select="."/>
    </CityName>
</xsl:for-each>'''
    
    print("Test 3 - Multiple element patterns:")
    print("Original:")
    print(test_chunk_3)
    
    result_3 = _text_based_for_each_merge(test_chunk_3)
    
    print("\nOptimized:")
    print(result_3)
    copy_count = result_3.count('copy-of')
    print(f"Copy-of patterns created: {copy_count}")
    
    return copy_count >= 2

if __name__ == "__main__":
    try:
        success = test_element_optimization()
        print(f"\n=== RESULT ===")
        print(f"Element optimization test: {'[SUCCESS]' if success else '[FAILED]'}")
        
    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()