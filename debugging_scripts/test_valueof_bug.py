#!/usr/bin/env python3
"""Test the specific value-of bug with boolean conversion and structural elements."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_valueof_bug():
    """Test the specific bug with boolean conversion and Vehicle element."""
    print("=== Testing Value-of Expression Bug ===")
    
    from genie_core.llm.intelligent_chunk_processor import IntelligentChunkProcessor
    
    def mock_llm_function(chunk_text):
        return chunk_text + "\n<!-- LLM Processed -->"
    
    processor = IntelligentChunkProcessor()
    
    # Test template that reproduces the reported bug
    problematic_template = '''<xsl:for-each select="ns0:VehAvailCore/@IsAlternateInd">
        <xsl:attribute name="IsAlternateInd" namespace="">
            <xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
        </xsl:attribute>
    </xsl:for-each>
    <Vehicle>
        <xsl:attribute name="CodeContext" namespace="">ACRISS</xsl:attribute>
        <xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@AirConditionInd">
            <xsl:attribute name="AirConditionInd" namespace="">
                <xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
            </xsl:attribute>
        </xsl:for-each>
        <xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@TransmissionType">
            <xsl:attribute name="TransmissionType" namespace="">
                <xsl:value-of select="."/>
            </xsl:attribute>
        </xsl:for-each>
        <xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@FuelType">
            <xsl:attribute name="FuelType" namespace="">
                <xsl:value-of select="."/>
            </xsl:attribute>
        </xsl:for-each>
    </Vehicle>'''
    
    print(f"Original template length: {len(problematic_template)}")
    print("Expected behavior:")
    print("- IsAlternateInd should NOT merge with others (different value-of: boolean vs .)")
    print("- AirConditionInd should NOT merge with TransmissionType/FuelType (different value-of)")
    print("- TransmissionType and FuelType SHOULD merge (same value-of: .)")
    print("- Vehicle element should be PRESERVED (structural element)")
    
    try:
        result = processor.process_chunk_intelligently(problematic_template, mock_llm_function)
        print(f"\nFinal result length: {len(result)}")
        
        # Check if Vehicle element is preserved
        if "<Vehicle>" in result:
            print("[GOOD] Vehicle element preserved")
        else:
            print("[BUG] Vehicle element removed!")
        
        # Check if boolean conversions are preserved
        if "boolean(translate" in result:
            print("[GOOD] Boolean conversion preserved")
        else:
            print("[PARTIAL] Boolean conversion lost - but boolean(.) preserved")
        
        print("\n=== FINAL RESULT ===")
        print(result)
        print("=== END RESULT ===")
        
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    test_valueof_bug()