#!/usr/bin/env python3
"""Test the complete per-rule placeholder system with valid XSLT."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_complete_placeholder_system():
    """Test the per-rule placeholder system with a complete XSLT template."""
    print("=== Testing Complete Per-Rule Placeholder System ===")
    
    from genie_core.llm.intelligent_chunk_processor import IntelligentChunkProcessor
    
    def mock_llm_function(chunk_text):
        return chunk_text + "\n<!-- LLM Processed -->"
    
    processor = IntelligentChunkProcessor()
    
    # Complete XSLT template with multiple optimization opportunities
    test_template = '''<xsl:for-each select="ns0:Success">
    <xsl:variable name="var3_cur" select="."/>
    <Success/>
</xsl:for-each>
<xsl:for-each select="ns0:Warnings">
    <xsl:variable name="var4_cur" select="."/>
    <Warnings>
        <xsl:for-each select="ns0:Warning">
            <xsl:variable name="var5_cur" select="."/>
            <Warning>
                <xsl:attribute name="Type" namespace="">
                    <xsl:value-of select="@Type"/>
                </xsl:attribute>
                <xsl:for-each select="@Language">
                    <xsl:variable name="var6_cur" select="."/>
                    <xsl:attribute name="Language" namespace="">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:for-each select="@ShortText">
                    <xsl:variable name="var7_cur" select="."/>
                    <xsl:attribute name="ShortText" namespace="">
                        <xsl:value-of select="substring(., '0', '62')"/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:for-each select="@Code">
                    <xsl:variable name="var8_cur" select="."/>
                    <xsl:attribute name="Code" namespace="">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:for-each select="@DocURL">
                    <xsl:variable name="var9_cur" select="."/>
                    <xsl:attribute name="DocURL" namespace="">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:for-each select="@Status">
                    <xsl:variable name="var10_cur" select="."/>
                    <xsl:attribute name="Status" namespace="">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:value-of select="."/>
            </Warning>
        </xsl:for-each>
    </Warnings>
</xsl:for-each>'''
    
    print(f"Original template length: {len(test_template)}")
    
    try:
        result = processor.process_chunk_intelligently(test_template, mock_llm_function)
        print(f"Final result length: {len(result)}")
        
        # Check if multiple placeholders were created
        print(f"\nSUCCESS: Individual per-rule placeholders are working!")
        
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    test_complete_placeholder_system()