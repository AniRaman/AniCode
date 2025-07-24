#!/usr/bin/env python3
"""
Test that LLM calls are working properly.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.intelligent_chunk_processor import IntelligentChunkProcessor

def mock_llm_function(pattern_text):
    """Mock LLM function for testing."""
    print(f"[MOCK LLM CALLED] Processing {len(pattern_text)} characters")
    return f"<!-- LLM Processed -->\n{pattern_text.strip()}"

def test_llm_calls():
    """Test that LLM calls are happening."""
    print("=== LLM CALLS TEST ===")
    
    processor = IntelligentChunkProcessor()
    
    # Create a chunk with both simple and complex patterns
    test_chunk = '''<xsl:for-each select="ns0:VehAvailRSCore">
        <VehAvailRSCore>
            <VehRentalCore>
                <xsl:for-each select="ns0:VehRentalCore/@ReturnDateTime">
                    <xsl:attribute name="ReturnDateTime" namespace="">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:for-each select="ns0:VehRentalCore/@StartChargesDateTime">
                    <xsl:attribute name="StartChargesDateTime" namespace="">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:choose>
                    <xsl:when test="@Status = 'active'">
                        <xsl:attribute name="Status">Active</xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:attribute name="Status">Inactive</xsl:attribute>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:if test="string-length(@Description) > 0">
                    <xsl:attribute name="Description">
                        <xsl:value-of select="substring(@Description, 1, 100)"/>
                    </xsl:attribute>
                </xsl:if>
            </VehRentalCore>
        </VehAvailRSCore>
    </xsl:for-each>'''
    
    print(f"Input chunk size: {len(test_chunk)} characters")
    
    result = processor.process_chunk_intelligently(test_chunk, mock_llm_function)
    
    print(f"Result size: {len(result)} characters")
    
    # Check if LLM was called
    llm_calls = result.count('<!-- LLM Processed -->')
    print(f"LLM calls detected: {llm_calls}")
    
    # Check statistics
    stats = processor.get_statistics()
    print(f"Stats - Complex patterns sent to LLM: {stats['complex_patterns_sent_to_llm']}")
    print(f"Stats - Simple patterns optimized: {stats['simple_patterns_optimized']}")
    
    success = llm_calls > 0 and stats['complex_patterns_sent_to_llm'] > 0
    
    if success:
        print("\n[SUCCESS] LLM calls are working correctly!")
    else:
        print("\n[FAILURE] LLM calls not working")
        
    return success

if __name__ == "__main__":
    success = test_llm_calls()
    print(f"\nLLM calls test: {'PASSED' if success else 'FAILED'}")