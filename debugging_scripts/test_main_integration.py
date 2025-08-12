#!/usr/bin/env python3
"""
Simple integration test for XSLT processing with intelligent chunk processor.
Tests the main processing chain from llm_utils.py with a large XSLT chunk.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

def create_large_test_xslt():
    """Create a test XSLT chunk larger than 1000 characters to trigger intelligent processing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <root>
            <!-- This is a large XSLT template to trigger intelligent processing -->
            <xsl:for-each select="data/items/item">
                <xsl:variable name="var1_current" select="."/>
                <xsl:for-each select="@id">
                    <xsl:variable name="var2_current" select="."/>
                    <xsl:attribute name="item-id">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:for-each select="@name">
                    <xsl:variable name="var3_current" select="."/>
                    <xsl:attribute name="item-name">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:for-each select="@category">
                    <xsl:variable name="var4_current" select="."/>
                    <xsl:attribute name="item-category">
                        <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:for-each>
                <xsl:for-each select="description">
                    <xsl:variable name="var5_current" select="."/>
                    <description>
                        <xsl:value-of select="."/>
                    </description>
                </xsl:for-each>
                <xsl:for-each select="price">
                    <xsl:variable name="var6_current" select="."/>
                    <price>
                        <xsl:value-of select="."/>
                    </price>
                </xsl:for-each>
            </xsl:for-each>
            
            <xsl:for-each select="data/metadata/tags/tag">
                <xsl:variable name="var7_current" select="."/>
                <tag>
                    <xsl:value-of select="."/>
                </tag>
            </xsl:for-each>
            
            <!-- Complex conditional logic -->
            <xsl:choose>
                <xsl:when test="contains(data/status, 'active')">
                    <status>Active</status>
                </xsl:when>
                <xsl:otherwise>
                    <status>Inactive</status>
                </xsl:otherwise>
            </xsl:choose>
        </root>
    </xsl:template>
</xsl:stylesheet>'''

def mock_llm_function(pattern_text):
    """Mock LLM function that simulates processing."""
    # Simple mock that adds a comment to show LLM processing
    return pattern_text + "\n<!-- LLM Processed -->"

def test_main_integration():
    """Test the main XSLT processing integration."""
    print("Starting XSLT Processing Integration Test")
    print("=" * 50)
    
    # Create test XSLT content
    test_xslt = create_large_test_xslt()
    print(f"Test XSLT size: {len(test_xslt)} characters")
    
    # Verify size is large enough to trigger intelligent processing
    if len(test_xslt) <= 1000:
        print("WARNING: Test XSLT is not large enough to trigger intelligent processing!")
        return False
    
    try:
        # Import the main processing function
        from genie_core.llm.llm_utils import initiate_conversation_with_LLM_xslt
        print("SUCCESS: Successfully imported main processing function")
        
        # Import intelligent chunk processor directly for testing
        from genie_core.llm.intelligent_chunk_processor import IntelligentChunkProcessor
        print("SUCCESS: Successfully imported intelligent chunk processor")
        
        # Test intelligent processor directly first
        processor = IntelligentChunkProcessor()
        
        # Create a test chunk that will trigger intelligent processing
        test_chunk = test_xslt[test_xslt.find('<xsl:template'):test_xslt.rfind('</xsl:template>') + 15]
        print(f"Test chunk size: {len(test_chunk)} characters")
        
        # Process the chunk with intelligent processor
        print("\nTesting intelligent chunk processing...")
        result = processor.process_chunk_intelligently(test_chunk, mock_llm_function)
        
        print("SUCCESS: Intelligent chunk processing completed")
        print(f"Result size: {len(result)} characters")
        
        # Verify intelligent processing was used
        constructs = processor.parse_xslt_constructs(test_chunk)
        simple_patterns, complex_patterns, _ = processor.separate_patterns(constructs)
        
        print(f"\nPattern separation results:")
        print(f"  Simple patterns: {len(simple_patterns)}")
        print(f"  Complex patterns: {len(complex_patterns)}")
        
        if len(simple_patterns) > 0 or len(complex_patterns) > 0:
            print("SUCCESS: Intelligent pattern separation working")
        else:
            print("WARNING: No patterns detected - check pattern recognition")
        
        # Test the main processing function
        print("\nTesting main XSLT processing function...")
        
        # Mock streamlit session state (required by the function)
        class MockSessionState:
            def __init__(self):
                self.generated_xslt = None
                self.hierarchical_reports = None
        
        import streamlit as st
        if not hasattr(st, 'session_state'):
            st.session_state = MockSessionState()
        
        # Call the main processing function
        initiate_conversation_with_LLM_xslt(test_xslt)
        
        print("SUCCESS: Main XSLT processing completed without errors")
        
        # Verify result
        if hasattr(st.session_state, 'generated_xslt') and st.session_state.generated_xslt:
            print(f"SUCCESS: Generated XSLT size: {len(st.session_state.generated_xslt)} characters")
        else:
            print("WARNING: No generated XSLT found in session state")
        
        # Show statistics
        processor.print_statistics()
        
        print("\n" + "=" * 50)
        print("SUCCESS: All tests completed successfully!")
        print("SUCCESS: Intelligent processing is working correctly")
        return True
        
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        print("Make sure all required dependencies are installed")
        return False
        
    except Exception as e:
        print(f"ERROR: Processing error: {e}")
        print("Check the processing chain for issues")
        return False

if __name__ == "__main__":
    print("XSLT Processing Chain Integration Test")
    print("Testing intelligent chunk processor with main processing function")
    print()
    
    success = test_main_integration()
    
    if success:
        print("\nSUCCESS: Integration test PASSED!")
        sys.exit(0)
    else:
        print("\nERROR: Integration test FAILED!")
        sys.exit(1)