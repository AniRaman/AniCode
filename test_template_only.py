"""
Test only the template creation and merging logic without parallel processing
"""

import pandas as pd
import sys
import os

# Add project root to path
if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))

def test_base_template_creation():
    """Test base template creation from output XML"""
    print("Testing Base Template Creation")
    print("-" * 40)

    try:
        from genie_core.llm.hybrid_template_merger import BaseTemplateGenerator

        output_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
    <Header>
        <CustomerID>123</CustomerID>
        <Currency>USD</Currency>
    </Header>
    <Details>
        <TaxAmount>15.00</TaxAmount>
        <ItemCount>5</ItemCount>
    </Details>
</Invoice>"""

        generator = BaseTemplateGenerator()
        print("Creating base template from output XML...")

        base_template = generator.create_base_template_from_output_xml(output_xml)

        print(f"Base template created successfully")
        print(f"   Length: {len(base_template)} characters")

        # Check for expected placeholders
        expected_placeholders = ['CustomerID', 'Currency', 'TaxAmount', 'ItemCount']
        found_placeholders = []

        for placeholder in expected_placeholders:
            placeholder_text = f"{{{{PLACEHOLDER_{placeholder}}}}}"
            if placeholder_text in base_template:
                found_placeholders.append(placeholder)

        print(f"   Expected placeholders: {expected_placeholders}")
        print(f"   Found placeholders: {found_placeholders}")

        # Show the template
        print(f"\n Base Template:")
        print(base_template)

        return len(found_placeholders) >= 3  # At least 3 placeholders should be found

    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chunk_extraction():
    """Test chunk extraction from sample XSLT"""
    print("\nTesting Chunk Extraction")
    print("-" * 40)

    try:
        from genie_core.llm.hybrid_template_merger import ChunkExtractor

        # Sample XSLT with multiple elements
        sample_xslt = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <CustomerID>
        <xsl:value-of select="ns0:Order/Customer/ID"/>
    </CustomerID>

    <TaxAmount>
        <xsl:choose>
            <xsl:when test="ns0:Order/TaxExempt = 'true'">
                <xsl:text>0.00</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="ns0:Order/Tax"/>
            </xsl:otherwise>
        </xsl:choose>
    </TaxAmount>

    <Currency>
        <xsl:text>USD</xsl:text>
    </Currency>

</xsl:stylesheet>"""

        extractor = ChunkExtractor()

        # Test extracting different elements
        test_elements = ['CustomerID', 'TaxAmount', 'Currency']
        extracted_chunks = {}

        for element in test_elements:
            print(f"\n   Extracting chunk for: {element}")
            chunk = extractor.extract_chunk_for_element(sample_xslt, element)

            if chunk:
                extracted_chunks[element] = chunk
                print(f"    Extracted {len(chunk)} characters")
                print(f"   Sample: {chunk[:100]}...")
            else:
                print(f"    No chunk found")

        print(f"\n   Successfully extracted {len(extracted_chunks)}/{len(test_elements)} chunks")
        return len(extracted_chunks) >= 2

    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_replacement():
    """Test replacing placeholders in base template with chunks"""
    print("\n Testing Template Replacement")
    print("-" * 40)

    try:
        from genie_core.llm.hybrid_template_merger import BaseTemplateGenerator, TemplateReplacer

        # Create a simple base template
        output_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
    <CustomerID>123</CustomerID>
    <Currency>USD</Currency>
</Invoice>"""

        generator = BaseTemplateGenerator()
        base_template = generator.create_base_template_from_output_xml(output_xml)

        print("Base template created")

        # Create sample chunks
        customer_chunk = """<xsl:value-of select="ns0:Order/Customer/ID"/>"""
        currency_chunk = """<xsl:text>USD</xsl:text>"""

        replacer = TemplateReplacer()

        # Replace CustomerID placeholder
        print("Replacing CustomerID placeholder...")
        updated_template = replacer.replace_placeholder_with_chunk(
            base_template, 'CustomerID', customer_chunk
        )

        # Replace Currency placeholder
        print("Replacing Currency placeholder...")
        final_template = replacer.replace_placeholder_with_chunk(
            updated_template, 'Currency', currency_chunk
        )

        # Check results
        remaining_placeholders = final_template.count('{{PLACEHOLDER_')
        print(f"\n    Template replacement completed")
        print(f"   Remaining placeholders: {remaining_placeholders}")

        print(f"\n Final Template:")
        print(final_template)

        return remaining_placeholders == 0

    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_element_extraction():
    """Test extracting element names from output XML"""
    print("\n Testing Element Name Extraction")
    print("-" * 40)

    try:
        from genie_core.llm.hybrid_template_merger import BaseTemplateGenerator

        output_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
    <Header>
        <CustomerID>123</CustomerID>
        <Date>2024-01-01</Date>
    </Header>
    <Details>
        <Amount>100.00</Amount>
        <Tax>15.00</Tax>
    </Details>
</Invoice>"""

        generator = BaseTemplateGenerator()
        element_names = generator.extract_element_names_from_output_xml(output_xml)

        print(f"   Extracted elements: {element_names}")

        expected_elements = ['Invoice', 'Header', 'CustomerID', 'Date', 'Details', 'Amount', 'Tax']
        found_count = len([e for e in expected_elements if e in element_names])

        print(f"   Expected to find {len(expected_elements)} elements")
        print(f"   Actually found {found_count} elements")

        return found_count >= 5  # Should find at least 5 elements

    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Template-Only Test Suite")
    print("=" * 50)

    tests = [
        ("Element Name Extraction", test_element_extraction),
        ("Base Template Creation", test_base_template_creation),
        ("Chunk Extraction", test_chunk_extraction),
        ("Template Replacement", test_template_replacement)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_function in tests:
        print(f"\nRunning: {test_name}")
        try:
            if test_function():
                passed += 1
                print(f"PASSED: {test_name}")
            else:
                print(f"FAILED: {test_name}")
        except Exception as e:
            print(f"ERROR: {test_name} - {e}")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All template tests passed!")
    else:
        print(f"{total - passed} tests failed.")

    print(f"\nNext Step: Once these core template tests pass,")
    print(f"   the real-time merging implementation should work correctly.")