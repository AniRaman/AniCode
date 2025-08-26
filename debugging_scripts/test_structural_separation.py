#!/usr/bin/env python3
"""
Test structural element separation as per user's requirements.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.intelligent_chunk_processor import IntelligentChunkProcessor

def mock_llm_function(pattern_text):
    """Mock LLM function for testing."""
    print(f"[MOCK LLM CALLED] Processing {len(pattern_text)} characters")
    return f"<!-- LLM Processed -->\n{pattern_text.strip()}"

def test_structural_separation():
    """Test structural element preservation and XSLT instruction processing."""
    print("=== STRUCTURAL SEPARATION TEST ===")
    
    processor = IntelligentChunkProcessor()
    
    # Test with the user's example structure
    test_chunk = '''<OTA_VehAvailRateRS xmlns="http://www.opentravel.org/OTA/2003/05">
        <xsl:for-each select="ns0:OTA_VehAvailRateRS">
            <xsl:variable name="var2_cur" select="."/>
            <xsl:for-each select="ns0:Success">
                <xsl:variable name="var3_cur" select="."/>
                <Success/>
            </xsl:for-each>                
            <xsl:for-each select="ns0:VehAvailRSCore">
                <xsl:variable name="var14_cur" select="."/>
                <VehAvailRSCore>
                    <VehRentalCore>
                        <xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime">
                            <xsl:variable name="var15_cur" select="."/>
                            <xsl:attribute name="PickUpDateTime" namespace="">
                                <xsl:value-of select="."/>
                            </xsl:attribute>
                        </xsl:for-each>
                        <xsl:for-each select="ns0:VehRentalCore/@ReturnDateTime">
                            <xsl:variable name="var16_cur" select="."/>
                            <xsl:attribute name="ReturnDateTime" namespace="">
                                <xsl:value-of select="."/>
                            </xsl:attribute>
                        </xsl:for-each>
                    </VehRentalCore>
                </VehAvailRSCore>
            </xsl:for-each>
        </xsl:for-each>
    </OTA_VehAvailRateRS>'''
    
    print(f"Input chunk size: {len(test_chunk)} characters")
    
    result = processor.process_chunk_intelligently(test_chunk, mock_llm_function)
    
    print(f"Result size: {len(result)} characters")
    
    # Analyze the result
    issues = []
    
    # Check 1: Structural tags should be preserved
    structural_tags = ['<OTA_VehAvailRateRS', '<VehAvailRSCore>', '<VehRentalCore>']
    for tag in structural_tags:
        if tag in result:
            print(f"[OK] Structural tag preserved: {tag}")
        else:
            issues.append(f"[ISSUE] Structural tag missing: {tag}")
    
    # Check 2: XSLT instructions should be processed
    xslt_instructions = result.count('<xsl:')
    print(f"[INFO] XSLT instructions found: {xslt_instructions}")
    
    # Check 3: LLM processing should happen
    llm_calls = result.count('<!-- LLM Processed -->')
    print(f"[INFO] LLM calls detected: {llm_calls}")
    
    # Check 4: Simple patterns should potentially be merged
    attribute_patterns = result.count('PickUpDateTime') + result.count('ReturnDateTime')
    print(f"[INFO] Attribute patterns: {attribute_patterns}")
    
    print(f"\n=== ANALYSIS RESULTS ===")
    print(f"Issues found: {len(issues)}")
    for issue in issues:
        print(issue)
    
    success = len(issues) == 0
    if success:
        print("\n[SUCCESS] Structural separation working correctly!")
    else:
        print(f"\n[PARTIAL] {len(issues)} issues found")
        
    return success

if __name__ == "__main__":
    success = test_structural_separation()
    print(f"\nStructural separation test: {'PASSED' if success else 'NEEDS WORK'}")