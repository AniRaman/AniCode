#!/usr/bin/env python3
"""
Test direct attribute copy optimization.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.refine_cache import _text_based_for_each_merge

def test_direct_attribute_copy():
    """Test the new direct attribute copy optimization."""
    print("=== TEST DIRECT ATTRIBUTE COPY ===")
    
    # Test case 1: Single direct attribute
    test_chunk_1 = '''<xsl:attribute name="Type">
    <xsl:value-of select="@Type"/>
</xsl:attribute>'''
    
    print("Test 1 - Single direct attribute:")
    print("Original:", test_chunk_1.strip())
    
    result_1 = _text_based_for_each_merge(test_chunk_1)
    
    print("Result:", result_1.strip())
    print(f"Optimized: {'copy-of' in result_1}")
    print()
    
    # Test case 2: Multiple direct attributes
    test_chunk_2 = '''<xsl:attribute name="Status">
    <xsl:value-of select="@Status"/>
</xsl:attribute>
<xsl:attribute name="Priority">
    <xsl:value-of select="@Priority"/>
</xsl:attribute>
<xsl:attribute name="Category">
    <xsl:value-of select="@Category"/>
</xsl:attribute>'''
    
    print("Test 2 - Multiple direct attributes:")
    print("Original length:", len(test_chunk_2))
    
    result_2 = _text_based_for_each_merge(test_chunk_2)
    
    print("Result length:", len(result_2))
    print("Result:", result_2.strip())
    copy_count = result_2.count('copy-of')
    print(f"Copy-of patterns: {copy_count}")
    print()
    
    # Test case 3: Mixed with other patterns
    test_chunk_3 = '''<xsl:for-each select="ns0:ContactInfo">
    <ContactInfo>
        <xsl:value-of select="."/>
    </ContactInfo>
</xsl:for-each>
<xsl:attribute name="Type">
    <xsl:value-of select="@Type"/>
</xsl:attribute>
<xsl:for-each select="@Status">
    <xsl:attribute name="Status">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>'''
    
    print("Test 3 - Mixed with other patterns:")
    print("Original length:", len(test_chunk_3))
    
    result_3 = _text_based_for_each_merge(test_chunk_3)
    
    print("Result length:", len(result_3))
    print("Result:", result_3.strip())
    
    element_copy = result_3.count('copy-of select="ns0:ContactInfo"')
    attr_copy = result_3.count('copy-of select="@Type"')
    for_each_kept = 'select="@Status"' in result_3
    
    print(f"Element copy-of: {element_copy}")
    print(f"Attribute copy-of: {attr_copy}")
    print(f"For-each kept (single pattern): {for_each_kept}")
    
    return copy_count >= 3

if __name__ == "__main__":
    try:
        success = test_direct_attribute_copy()
        print(f"\n=== RESULT ===")
        print(f"Direct attribute copy test: {'[SUCCESS]' if success else '[FAILED]'}")
        
    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()