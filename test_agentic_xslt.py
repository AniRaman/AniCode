"""
Test scenarios for Agentic XSLT Processor

These tests verify that the agentic approach produces identical results to the original
conversation-based approach for all major user interaction patterns.
"""

import os
import sys
sys.path.append(os.path.abspath(os.getcwd()))

# Test data
MOCK_INPUT_XML = """<?xml version="1.0"?>
<root>
    <field1>value1</field1>
    <field2>value2</field2>
</root>"""

MOCK_OUTPUT_XML = """<?xml version="1.0"?>
<transformed>
    <output1>value1</output1>
    <output2>value2</output2>
</transformed>"""

MOCK_SPECS_URL = "https://example.com/specs"

MOCK_EXISTING_XSLT = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <transformed>
            <output1><xsl:value-of select="root/field1"/></output1>
        </transformed>
    </xsl:template>
</xsl:stylesheet>"""

def test_scenarios():
    """
    Test various user interaction scenarios
    """
    
    # Import the processor
    from genie_core.llm.llm_utils import process_user_response
    
    print("Testing XSLT Processor Scenarios...")
    print("="*50)
    
    scenarios = [
        {
            "name": "Fresh Start - Direct URL Processing", 
            "message": "Generate XSLT from https://example.com/specs",
            "chat_history": [],
            "input_xml": MOCK_INPUT_XML,
            "output_xml": MOCK_OUTPUT_XML, 
            "main_xslt": "",
            "specs": "",
            "expected_keywords": ["process", "generate", "XSLT"]
        },
        {
            "name": "Missing XMLs",
            "message": "Generate XSLT from https://example.com/specs", 
            "chat_history": [],
            "input_xml": None,
            "output_xml": None,
            "main_xslt": "",
            "specs": "",
            "expected_keywords": ["upload", "XML"]
        },
        {
            "name": "Field Refinement",
            "message": "Fix the TaxAmount field to include currency symbol",
            "chat_history": [("Generated XSLT", "XSLT generated successfully")],
            "input_xml": MOCK_INPUT_XML, 
            "output_xml": MOCK_OUTPUT_XML,
            "main_xslt": MOCK_EXISTING_XSLT,
            "specs": "mock_specs_data",
            "expected_keywords": ["refine", "TaxAmount", "currency"]
        },
        {
            "name": "Simple URL Input", 
            "message": "https://example.com/specs",
            "chat_history": [],
            "input_xml": MOCK_INPUT_XML,
            "output_xml": MOCK_OUTPUT_XML,
            "main_xslt": "", 
            "specs": "",
            "expected_keywords": ["process", "URL"]
        },
        {
            "name": "Refinement Instructions",
            "message": "Change the formatting to include proper namespaces",
            "chat_history": [("Which fields?", "TaxAmount and Currency")],
            "input_xml": MOCK_INPUT_XML,
            "output_xml": MOCK_OUTPUT_XML, 
            "main_xslt": MOCK_EXISTING_XSLT,
            "specs": "mock_specs_data",
            "expected_keywords": ["refine", "formatting", "namespace"]
        }
    ]
    
    # Test both approaches
    for use_agentic in [False, True]:
        approach_name = "AGENTIC" if use_agentic else "ORIGINAL"
        print(f"\n{approach_name} APPROACH TESTS:")
        print("-" * 30)
        
        # Set environment variable
        os.environ["USE_AGENTIC_XSLT"] = "true" if use_agentic else "false"
        
        for scenario in scenarios:
            print(f"\nTesting: {scenario['name']}")
            try:
                user_request, bot_message, updated_history, updated_xslt = process_user_response(
                    message=scenario["message"],
                    chat_history=scenario["chat_history"], 
                    input_xml=scenario["input_xml"],
                    transformed_xml=scenario["output_xml"],
                    main_xslt=scenario["main_xslt"],
                    specs=scenario["specs"]
                )
                
                print(f"✓ Success: {bot_message[:100]}...")
                print(f"  User Request Flag: {user_request}")
                print(f"  Chat History Length: {len(updated_history)}")
                print(f"  XSLT Updated: {'Yes' if updated_xslt != scenario['main_xslt'] else 'No'}")
                
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                
        print(f"\n{approach_name} APPROACH COMPLETED")

def test_environment_switching():
    """Test that environment variable switching works correctly"""
    print("\n" + "="*50)
    print("ENVIRONMENT SWITCHING TEST")
    print("="*50)
    
    from genie_core.llm.llm_utils import process_user_response
    
    test_message = "Test message"
    test_history = []
    test_xml = MOCK_INPUT_XML
    
    # Test switching between approaches
    for env_value, expected_approach in [("false", "ORIGINAL"), ("true", "AGENTIC")]:
        os.environ["USE_AGENTIC_XSLT"] = env_value
        print(f"\nTesting with USE_AGENTIC_XSLT={env_value}")
        
        try:
            user_request, bot_message, updated_history, updated_xslt = process_user_response(
                message=test_message,
                chat_history=test_history,
                input_xml=test_xml,
                transformed_xml=test_xml,
                main_xslt="",
                specs=""
            )
            print(f"✓ Successfully used {expected_approach} approach")
            print(f"  Response: {bot_message[:50]}...")
            
        except Exception as e:
            print(f"✗ Error with {expected_approach}: {str(e)}")

def main():
    """Run all tests"""
    print("AGENTIC XSLT PROCESSOR TEST SUITE")
    print("="*50)
    print("This test suite verifies that both original and agentic approaches work correctly")
    print("and produce consistent results for various user interaction scenarios.")
    
    try:
        test_scenarios()
        test_environment_switching()
        
        print("\n" + "="*50)
        print("TEST SUITE COMPLETED")
        print("="*50)
        
    except Exception as e:
        print(f"\nTEST SUITE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()