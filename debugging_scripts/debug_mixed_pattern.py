#!/usr/bin/env python3
"""
Debug the mixed pattern issue.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.refine_cache import _text_based_for_each_merge
import re

def debug_mixed_pattern():
    """Debug why element pattern disappears in mixed chunk."""
    
    mixed_chunk = '''<xsl:for-each select="@Status">
    <xsl:attribute name="Status">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>
<xsl:for-each select="ns0:ContactInfo">
    <xsl:variable name="var10_cur" select="."/>
    <ContactInfo>
        <xsl:value-of select="."/>
    </ContactInfo>
</xsl:for-each>
<xsl:for-each select="@Priority">
    <xsl:attribute name="Priority">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>'''
    
    print("=== DEBUGGING MIXED PATTERN ===")
    print("Original chunk:")
    print(mixed_chunk)
    print()
    
    # Test element pattern regex specifically
    element_pattern = r'<xsl:for-each\s+select="([^"]+)"[^>]*>\s*(?:\s*<xsl:variable[^>]*name="var\d+_cur"[^>]*select="\."[^>]*(?:/>|></xsl:variable>)\s*)?<(\w+)[^>]*>\s*<xsl:value-of\s+select="\."[^>]*/?>\s*</\2>\s*</xsl:for-each>'
    
    element_matches = list(re.finditer(element_pattern, mixed_chunk, re.DOTALL))
    print(f"Element pattern matches found: {len(element_matches)}")
    
    if element_matches:
        for i, match in enumerate(element_matches):
            print(f"Match {i+1}:")
            print(f"  Select: '{match.group(1)}'")
            print(f"  Element: '{match.group(2)}'")
            print(f"  Full match: '{match.group(0)}'")
    
    print()
    
    # Now test the full function
    result = _text_based_for_each_merge(mixed_chunk)
    
    print("Result:")
    print(result)
    print()
    
    print("Analysis:")
    print(f"Original contains 'ns0:ContactInfo': {'ns0:ContactInfo' in mixed_chunk}")
    print(f"Result contains 'ns0:ContactInfo': {'ns0:ContactInfo' in result}")
    print(f"Result contains 'ContactInfo': {'ContactInfo' in result}")
    print(f"Result contains 'copy-of': {'copy-of' in result}")

if __name__ == "__main__":
    debug_mixed_pattern()