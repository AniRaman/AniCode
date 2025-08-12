#!/usr/bin/env python3
"""
Test all text-based optimization patterns together.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.refine_cache import _text_based_for_each_merge

def test_comprehensive_optimizations():
    """Test all optimization patterns working together."""
    print("=== COMPREHENSIVE TEXT-BASED OPTIMIZATION TEST ===")
    
    # Complex test with all pattern types
    comprehensive_chunk = '''<xsl:for-each select="@Status">
    <xsl:attribute name="Status">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>
<xsl:for-each select="@Priority">
    <xsl:attribute name="Priority">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>
<xsl:for-each select="ns0:ContactInfo">
    <xsl:variable name="var10_cur" select="."/>
    <ContactInfo>
        <xsl:value-of select="."/>
    </ContactInfo>
</xsl:for-each>
<xsl:attribute name="Type">
    <xsl:value-of select="@Type"/>
</xsl:attribute>
<CompanyName>
    <xsl:value-of select="ns0:CompanyName"/>
</CompanyName>
<xsl:for-each select="ns0:Address">
    <Address>
        <xsl:value-of select="."/>
    </Address>
</xsl:for-each>'''
    
    print("Original length:", len(comprehensive_chunk))
    print("\nOriginal patterns:")
    print("- 2x attribute for-each (@Status, @Priority)")  
    print("- 1x element for-each with variable (ContactInfo)")
    print("- 1x direct attribute copy (Type)")
    print("- 1x simple element copy (CompanyName)")
    print("- 1x element for-each without variable (Address)")
    
    result = _text_based_for_each_merge(comprehensive_chunk)
    
    print(f"\nOptimized length: {len(result)}")
    print(f"Size reduction: {((len(comprehensive_chunk) - len(result)) / len(comprehensive_chunk) * 100):.1f}%")
    
    print("\nResult:")
    print(result)
    
    # Count optimization results
    attr_union = '@Status | @Priority' in result or ('@Priority | @Status' in result)
    element_copies = result.count('copy-of select="ns0:')
    attr_copies = result.count('copy-of select="@')
    remaining_foreach = result.count('<xsl:for-each')
    
    print(f"\nOptimization Analysis:")
    print(f"- Attribute union created: {attr_union}")
    print(f"- Element copy-of patterns: {element_copies}")
    print(f"- Attribute copy-of patterns: {attr_copies}")
    print(f"- Remaining for-each blocks: {remaining_foreach}")
    
    # Expected: 2 element copy-of + 1 attribute copy-of + possible attribute union
    total_optimizations = element_copies + attr_copies + (1 if attr_union else 0)
    
    return total_optimizations >= 3

def test_incomplete_xml_fragment():
    """Test with realistic incomplete fragment like NDC."""
    print("\n=== INCOMPLETE XML FRAGMENT TEST ===")
    
    incomplete_fragment = '''<ContactInfo>
        <xsl:attribute name="ID">
            <xsl:value-of select="@ID"/>
        </xsl:attribute>
        <xsl:for-each select="*[name()='ns0:Phone']">
            <Phone>
                <xsl:value-of select="."/>
            </Phone>
        </xsl:for-each>
        <Email>
            <xsl:value-of select="ns0:Email"/>
        </Email>
    </ContactInfo>'''
    
    print("Fragment (incomplete XML):")
    print("Original length:", len(incomplete_fragment))
    
    result = _text_based_for_each_merge(incomplete_fragment)
    
    print("Optimized length:", len(result))
    print("Result:")
    print(result)
    
    # Should optimize: attribute copy + element copy + simple element  
    optimizations = result.count('copy-of')
    print(f"Copy-of optimizations: {optimizations}")
    
    return optimizations >= 2

if __name__ == "__main__":
    try:
        print("Testing comprehensive text-based optimizations...\n")
        
        comprehensive_success = test_comprehensive_optimizations()
        incomplete_success = test_incomplete_xml_fragment()
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Comprehensive test: {'[SUCCESS]' if comprehensive_success else '[FAILED]'}")
        print(f"Incomplete fragment test: {'[SUCCESS]' if incomplete_success else '[FAILED]'}")
        print(f"Overall: {'[SUCCESS]' if (comprehensive_success and incomplete_success) else '[FAILED]'}")
        
    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()