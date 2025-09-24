"""
Test just the async LLM functions to isolate any async issues
"""

import pandas as pd
import sys
import os
import asyncio

# Add project root to path
if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))

# Mock LLM calls to avoid Azure issues
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
    content = """<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <CustomerID>
        <xsl:value-of select="test/CustomerID"/>
    </CustomerID>
</xsl:stylesheet>"""
    return MockResponse(content)

# Patch the async function
import genie_core.llm.llm_utils
genie_core.llm.llm_utils.get_chat_completion_async = mock_get_chat_completion_async

async def test_async_llm_function():
    """Test the async LLM function in isolation"""
    print("🔧 Testing Async LLM Function")
    print("-" * 40)

    try:
        from genie_core.llm.llm_utils import llm_process_async

        # Simple test data
        test_data = pd.DataFrame({
            'Field': ['CustomerID'],
            'Input': ['ns0:Order/Customer/ID'],
            'Output': ['Customer ID']
        })

        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ns0:Order xmlns:ns0="http://test.com">
    <ns0:Customer><ns0:ID>123</ns0:ID></ns0:Customer>
</ns0:Order>"""

        output_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
    <CustomerID>123</CustomerID>
</Invoice>"""

        message = "Map CustomerID field"

        print("Calling llm_process_async...")
        result = await llm_process_async(test_data, message, input_xml, output_xml, None)

        print("✅ Async LLM call succeeded")
        print(f"Result length: {len(result) if result else 0}")
        print(f"Result: {result[:200]}..." if result else "No result")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main async test runner"""
    print("🧪 Async LLM Test")
    print("=" * 50)

    success = await test_async_llm_function()

    if success:
        print("\n🎉 Async LLM test passed!")
    else:
        print("\n❌ Async LLM test failed")

if __name__ == "__main__":
    asyncio.run(main())