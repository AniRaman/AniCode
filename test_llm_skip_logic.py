#!/usr/bin/env python3
"""
Test the new LLM skip logic with different complexity levels.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.intelligent_chunk_processor import IntelligentChunkProcessor

def mock_llm_function(pattern_text):
    """Mock LLM function for testing."""
    print(f"[MOCK LLM CALLED] Processing {len(pattern_text)} characters")
    return f"<!-- LLM Enhanced -->\n{pattern_text.strip()}"

def test_simple_chunk_should_skip():
    """Test that very simple chunks are skipped."""
    print("=== SIMPLE CHUNK (SHOULD SKIP) ===")
    
    processor = IntelligentChunkProcessor()
    
    # Very simple chunk - just attribute copying
    simple_chunk = '''<xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime">
        <xsl:attribute name="PickUpDateTime" namespace="">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:for-each>'''
    
    result = processor.process_chunk_intelligently(simple_chunk, mock_llm_function)
    
    # Check if LLM was skipped
    stats = processor.get_statistics()
    llm_calls = result.count('<!-- LLM Enhanced -->')
    
    print(f"LLM calls made: {llm_calls}")
    print(f"Stats LLM calls: {stats['complex_patterns_sent_to_llm']}")
    
    return llm_calls == 0

def test_complex_chunk_should_process():
    """Test that complex chunks are still processed."""
    print("\n=== COMPLEX CHUNK (SHOULD PROCESS) ===")
    
    processor = IntelligentChunkProcessor()
    
    # Complex chunk with conditionals and string functions
    complex_chunk = '''<xsl:for-each select="ns0:VehRentalCore">
        <xsl:choose>
            <xsl:when test="contains(@Description, 'premium')">
                <xsl:attribute name="Type">Premium</xsl:attribute>
                <xsl:attribute name="Description">
                    <xsl:value-of select="substring(@Description, 1, 100)"/>
                </xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
                <xsl:attribute name="Type">Standard</xsl:attribute>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:call-template name="format-date">
            <xsl:with-param name="date" select="@PickUpDateTime"/>
        </xsl:call-template>
    </xsl:for-each>'''
    
    result = processor.process_chunk_intelligently(complex_chunk, mock_llm_function)
    
    # Check if LLM was called
    stats = processor.get_statistics()
    llm_calls = result.count('<!-- LLM Enhanced -->')
    
    print(f"LLM calls made: {llm_calls}")
    print(f"Stats LLM calls: {stats['complex_patterns_sent_to_llm']}")
    
    return llm_calls > 0

def test_medium_chunk_after_rules():
    """Test medium complexity chunk that gets simplified by rules."""
    print("\n=== MEDIUM CHUNK (RULES OPTIMIZED) ===")
    
    processor = IntelligentChunkProcessor()
    
    # Medium chunk - multiple similar patterns that rules can merge
    medium_chunk = '''<xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime">
        <xsl:attribute name="PickUpDateTime" namespace="">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:for-each>
    <xsl:for-each select="ns0:VehRentalCore/@ReturnDateTime">
        <xsl:attribute name="ReturnDateTime" namespace="">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:for-each>
    <xsl:for-each select="ns0:VehRentalCore/@StartChargesDateTime">
        <xsl:attribute name="StartChargesDateTime" namespace="">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:for-each>'''
    
    result = processor.process_chunk_intelligently(medium_chunk, mock_llm_function)
    
    # Check if LLM was called
    stats = processor.get_statistics()
    llm_calls = result.count('<!-- LLM Enhanced -->')
    
    print(f"LLM calls made: {llm_calls}")
    print(f"Stats LLM calls: {stats['complex_patterns_sent_to_llm']}")
    
    return result, llm_calls

if __name__ == "__main__":
    print("Testing LLM Skip Logic...\n")
    
    simple_skipped = test_simple_chunk_should_skip()
    complex_processed = test_complex_chunk_should_process()
    medium_result, medium_calls = test_medium_chunk_after_rules()
    
    print(f"\n=== RESULTS ===")
    print(f"Simple chunk skipped: {'PASS' if simple_skipped else 'FAIL'}")
    print(f"Complex chunk processed: {'PASS' if complex_processed else 'FAIL'}")
    print(f"Medium chunk LLM calls: {medium_calls}")
    
    if simple_skipped and complex_processed and medium_calls == 0:
        print("\n[SUCCESS] LLM skip logic working correctly!")
    else:
        print("\n[NEEDS WORK] LLM skip logic needs tuning")