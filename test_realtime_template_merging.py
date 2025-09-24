"""
Test script for real-time template merging implementation
Tests the new flow: base template first, then real-time batch merging
"""

import pandas as pd
import sys
import os

# Add project root to path
if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))

from genie_core.llm.parallel_xslt_processor import process_mappings_with_realtime_merging


def create_test_data():
    """Create test data for real-time merging"""

    # Simple rows (8 per batch)
    simple_data = {
        'Field': ['CustomerID', 'Currency', 'Status', 'Region', 'Country', 'Type', 'Category', 'Priority'],
        'Input': ['ns0:Order/Customer/ID', 'USD', 'ACTIVE', 'ns0:Order/Region', 'ns0:Order/Country', 'STANDARD', 'A', 'HIGH'],
        'Output': ['Customer ID', 'Currency', 'Status', 'Region', 'Country', 'Type', 'Category', 'Priority'],
        'C/S': ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S']
    }

    # Complex rows (4 per batch)
    complex_data = {
        'Field': ['TaxAmount', 'InvoiceDate', 'ItemCount', 'TotalAmount'],
        'Input': ['ns0:Order/Tax', 'ns0:Order/Date', 'ns0:Order/Items/Item', 'ns0:Order/Total'],
        'Output': ['Tax Amount with format', 'Invoice Date formatted', 'Item Count', 'Total Amount'],
        'C/S': ['C', 'C', 'C', 'C']
    }

    simple_df = pd.DataFrame(simple_data)
    complex_df = pd.DataFrame(complex_data)

    return simple_df, complex_df


def create_test_xml():
    """Create test XML inputs"""

    input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ns0:Order xmlns:ns0="http://test.com/order">
    <ns0:Customer>
        <ns0:ID>CUST001</ns0:ID>
    </ns0:Customer>
    <ns0:Date>2024-01-15</ns0:Date>
    <ns0:Tax>150.00</ns0:Tax>
    <ns0:Total>1150.00</ns0:Total>
    <ns0:Region>North America</ns0:Region>
    <ns0:Country>USA</ns0:Country>
    <ns0:Items>
        <ns0:Item>Item1</ns0:Item>
        <ns0:Item>Item2</ns0:Item>
        <ns0:Item>Item3</ns0:Item>
    </ns0:Items>
</ns0:Order>"""

    output_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
    <Header>
        <CustomerID>123</CustomerID>
        <InvoiceDate>2024-01-01</InvoiceDate>
        <Currency>USD</Currency>
        <Region>North America</Region>
        <Country>USA</Country>
    </Header>
    <Details>
        <TotalAmount>100.00</TotalAmount>
        <TaxAmount>15.00</TaxAmount>
        <ItemCount>5</ItemCount>
        <Status>ACTIVE</Status>
        <Type>STANDARD</Type>
        <Category>A</Category>
        <Priority>HIGH</Priority>
    </Details>
</Invoice>"""

    return input_xml, output_xml


def test_realtime_template_merging():
    """Test the complete real-time template merging flow"""
    print("🧪 Testing Real-Time Template Merging")
    print("=" * 60)

    try:
        # Create test data
        simple_df, complex_df = create_test_data()
        input_xml, output_xml = create_test_xml()

        print(f"📊 Test Data Created:")
        print(f"   Simple rows: {len(simple_df)}")
        print(f"   Complex rows: {len(complex_df)}")
        print(f"   Input XML length: {len(input_xml)} characters")
        print(f"   Output XML length: {len(output_xml)} characters")

        # Test the real-time merging flow
        print(f"\n🚀 Starting Real-Time Template Merging Test...")
        print("-" * 40)

        final_xslt = process_mappings_with_realtime_merging(
            simple_df, complex_df, input_xml, output_xml
        )

        # Analyze results
        if final_xslt and len(final_xslt) > 0:
            print(f"\n✅ Real-Time Template Merging SUCCESSFUL!")
            print(f"   Final XSLT length: {len(final_xslt)} characters")

            # Check for key indicators
            has_template_structure = '<xsl:template match="/">' in final_xslt
            has_xslt_header = '<?xml version="1.0" encoding="UTF-8"?>' in final_xslt
            remaining_placeholders = final_xslt.count('{{PLACEHOLDER_')

            print(f"\n🔍 Quality Analysis:")
            print(f"   ✓ XSLT header present: {has_xslt_header}")
            print(f"   ✓ Template structure present: {has_template_structure}")
            print(f"   ⚠️ Remaining placeholders: {remaining_placeholders}")

            # Show sample output (first 1000 chars)
            print(f"\n📝 Final XSLT Sample (first 1000 chars):")
            print("-" * 40)
            print(final_xslt[:1000])
            if len(final_xslt) > 1000:
                print("... [truncated]")

            return True

        else:
            print(f"\n❌ Real-Time Template Merging FAILED!")
            print(f"   Returned empty or None result")
            return False

    except Exception as e:
        print(f"\n❌ Real-Time Template Merging ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_template_creation():
    """Test base template creation separately"""
    print("\n🏗️ Testing Base Template Creation")
    print("-" * 40)

    try:
        from genie_core.llm.hybrid_template_merger import BaseTemplateGenerator

        _, output_xml = create_test_xml()
        generator = BaseTemplateGenerator()

        base_template = generator.create_base_template_from_output_xml(output_xml)

        if base_template and len(base_template) > 0:
            print(f"✅ Base template created successfully")
            print(f"   Length: {len(base_template)} characters")

            # Count placeholders
            placeholder_count = base_template.count('{{PLACEHOLDER_')
            print(f"   Placeholders found: {placeholder_count}")

            # Show placeholders
            import re
            placeholders = re.findall(r'\{\{PLACEHOLDER_(\w+)\}\}', base_template)
            print(f"   Placeholder elements: {placeholders}")

            return True
        else:
            print(f"❌ Base template creation failed")
            return False

    except Exception as e:
        print(f"❌ Base template creation error: {e}")
        return False


def run_all_tests():
    """Run all real-time merging tests"""
    print("🧪 Real-Time Template Merging Test Suite")
    print("=" * 60)

    tests = [
        ("Base Template Creation", test_base_template_creation),
        ("Real-Time Template Merging", test_realtime_template_merging)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_function in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_function():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 60)
    print(f"🧪 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Real-time template merging is working.")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check implementation.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)