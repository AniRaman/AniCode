"""
Simple debug test to isolate the hanging issue
"""

import pandas as pd
import sys
import os

# Add project root to path
if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))

print("Starting simple debug test...")

# Mock LLM calls first
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
    """Mock async LLM call"""
    content = """<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <CustomerID>
        <xsl:value-of select="ns0:Order/CustomerID"/>
    </CustomerID>
</xsl:stylesheet>"""
    return MockResponse(content)

try:
    print("Importing parallel processor...")
    from genie_core.llm.parallel_xslt_processor import process_batch_async
    print("Import successful")

    # Patch the async function
    import genie_core.llm.llm_utils
    genie_core.llm.llm_utils.get_chat_completion_async = mock_get_chat_completion_async
    print("Mock function patched")

    print("Creating test data...")
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

    print("About to test process_batch_async...")

    import asyncio

    async def run_test():
        try:
            result = await process_batch_async(test_data, message, input_xml, output_xml)
            print(f"Result: {len(result) if result else 0} characters")
            return result
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    print("Running async test...")
    result = asyncio.run(run_test())

    if result:
        print("Test completed successfully!")
    else:
        print("Test failed")

except Exception as e:
    print(f"Import/setup error: {e}")
    import traceback
    traceback.print_exc()