"""
Simple test for real-time template merging with mocked LLM calls
"""

import pandas as pd
import sys
import os

# Add project root to path
if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))

# Mock LLM calls to avoid timeouts
class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]
        self.usage = MockUsage()

    def __str__(self):
        return f"MockResponse(content='{self.choices[0].message.content[:50]}...')"

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockUsage:
    def __init__(self):
        self.prompt_tokens = 100
        self.completion_tokens = 50
        self.total_tokens = 150

async def mock_get_chat_completion_async(prompt):
    """Mock async LLM call that returns simple XSLT"""
    # Extract field name from prompt for realistic mocking
    field_name = "CustomerID"  # Default field
    if "TaxAmount" in str(prompt):
        field_name = "TaxAmount"

    content = f"""<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <{field_name}>
        <xsl:value-of select="ns0:Order/{field_name}"/>
    </{field_name}>
</xsl:stylesheet>"""
    return MockResponse(content)

def mock_llm_process(context_batch, message, input_xml, output_xml, current_xslt=None):
    """Mock synchronous LLM processing that returns simple XSLT chunks"""

    # Get the field name from the first row
    if len(context_batch) > 0:
        field_name = context_batch.iloc[0]['Field']

        # Return simple XSLT chunk for this field
        return f"""<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <{field_name}>
        <xsl:value-of select="ns0:Order/{field_name}"/>
    </{field_name}>
</xsl:stylesheet>"""

    return ""

# Patch both sync and async LLM functions
import genie_core.llm.llm_utils
genie_core.llm.llm_utils.llm_process = mock_llm_process
genie_core.llm.llm_utils.get_chat_completion_async = mock_get_chat_completion_async

def test_base_template_only():
    """Test just base template creation"""
    print("🏗️ Testing Base Template Creation Only")
    print("-" * 40)

    try:
        from genie_core.llm.hybrid_template_merger import BaseTemplateGenerator

        output_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
    <CustomerID>123</CustomerID>
    <TaxAmount>15.00</TaxAmount>
</Invoice>"""

        generator = BaseTemplateGenerator()
        base_template = generator.create_base_template_from_output_xml(output_xml)

        print("✅ Base template created successfully")
        print("Base template:")
        print(base_template)
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_realtime_flow():
    """Test real-time flow with minimal data"""
    print("\n🚀 Testing Simple Real-Time Flow")
    print("-" * 40)

    try:
        from genie_core.llm.parallel_xslt_processor import process_mappings_with_realtime_merging

        # Very simple test data - just 2 fields total
        simple_data = pd.DataFrame({
            'Field': ['CustomerID'],
            'Input': ['ns0:Order/Customer/ID'],
            'Output': ['Customer ID']
        })

        complex_data = pd.DataFrame({
            'Field': ['TaxAmount'],
            'Input': ['ns0:Order/Tax'],
            'Output': ['Tax Amount']
        })

        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ns0:Order xmlns:ns0="http://test.com">
    <ns0:Customer><ns0:ID>123</ns0:ID></ns0:Customer>
    <ns0:Tax>15.00</ns0:Tax>
</ns0:Order>"""

        output_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
    <CustomerID>123</CustomerID>
    <TaxAmount>15.00</TaxAmount>
</Invoice>"""

        print("Starting real-time merging with mock LLM...")

        final_xslt = process_mappings_with_realtime_merging(
            simple_data, complex_data, input_xml, output_xml
        )

        print("✅ Real-time merging completed")
        print(f"Final XSLT length: {len(final_xslt) if final_xslt else 0}")

        if final_xslt:
            print("Final XSLT:")
            print(final_xslt[:500] + "..." if len(final_xslt) > 500 else final_xslt)

        return final_xslt is not None and len(final_xslt) > 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Simple Real-Time Merging Test")
    print("=" * 50)

    success1 = test_base_template_only()
    success2 = test_simple_realtime_flow()

    if success1 and success2:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed")