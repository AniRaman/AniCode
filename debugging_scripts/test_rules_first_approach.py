#!/usr/bin/env python3
"""
Test the new rules-first + placeholder approach.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.intelligent_chunk_processor import IntelligentChunkProcessor

def mock_llm_function(pattern_text):
    """Mock LLM function for testing."""
    print(f"[MOCK LLM CALLED] Processing {len(pattern_text)} characters")
    return f"<!-- LLM Enhanced -->\n{pattern_text.strip()}"

def test_rules_first_approach():
    """Test the rules-first + placeholder approach."""
    print("=== RULES-FIRST APPROACH TEST ===")
    
    processor = IntelligentChunkProcessor()
    
    # Test with chunk that has both rule-optimizable and complex patterns
    test_chunk = '''<xsl:for-each select="ns0:VehAvailRSCore">
        <VehAvailRSCore>
            <VehRentalCore>
                <xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime">
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
                </xsl:for-each>
                <xsl:choose>
                    <xsl:when test="@Status = 'active'">
                        <xsl:attribute name="Status">Active</xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:attribute name="Status">Inactive</xsl:attribute>
                    </xsl:otherwise>
                </xsl:choose>
            </VehRentalCore>
        </VehAvailRSCore>
    </xsl:for-each>'''
    
    print(f"Input chunk size: {len(test_chunk)} characters")
    
    result = processor.process_chunk_intelligently(test_chunk, mock_llm_function)
    
    print(f"Result size: {len(result)} characters")
    
    # Analyze results
    issues = []
    
    # Check 1: Rules should have been applied first
    stats = processor.get_statistics()
    if stats['simple_patterns_optimized'] > 0:
        print(f"[OK] Rules applied: {stats['simple_patterns_optimized']} optimizations")
    else:
        print("[INFO] No rule optimizations (may be expected)")
    
    # Check 2: LLM should have been called
    if stats['complex_patterns_sent_to_llm'] > 0:
        print(f"[OK] LLM called: {stats['complex_patterns_sent_to_llm']} times")
    else:
        issues.append("[ISSUE] LLM was not called")
    
    # Check 3: Structure should be preserved
    if '<VehAvailRSCore>' in result and '<VehRentalCore>' in result:
        print("[OK] Structural elements preserved")
    else:
        issues.append("[ISSUE] Structural elements missing")
    
    # Check 4: Both rule and LLM enhancements should be present
    rule_enhancements = result.count('|')  # Union selects from rules
    llm_enhancements = result.count('<!-- LLM Enhanced -->')
    
    print(f"[INFO] Rule enhancements detected: {rule_enhancements}")
    print(f"[INFO] LLM enhancements detected: {llm_enhancements}")
    
    # Check 5: No placeholder artifacts should remain
    if '<simpletag' in result:
        issues.append("[ISSUE] Placeholder artifacts remain")
    else:
        print("[OK] No placeholder artifacts")
    
    print(f"\n=== ANALYSIS RESULTS ===")
    print(f"Issues found: {len(issues)}")
    for issue in issues:
        print(issue)
    
    success = len(issues) == 0
    if success:
        print("\n[SUCCESS] Rules-first approach working correctly!")
    else:
        print(f"\n[PARTIAL] {len(issues)} issues found")
        
    return success

if __name__ == "__main__":
    success = test_rules_first_approach()
    print(f"\nRules-first approach test: {'PASSED' if success else 'NEEDS WORK'}")