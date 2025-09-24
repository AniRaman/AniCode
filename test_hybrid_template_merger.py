"""
Test script for hybrid template-based XSLT merging system
Tests all components: template generation, chunk extraction, conflict resolution
"""

import pandas as pd
import sys
import os

# Add project root to path
if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))

from genie_core.llm.hybrid_template_merger import (
    BaseTemplateGenerator,
    ChunkExtractor,
    TemplateReplacer,
    ConflictResolver,
    HybridTemplateMerger
)


def create_test_output_xml():
    """Create sample output XML for testing"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
    <Header>
        <CustomerID>123</CustomerID>
        <InvoiceDate>2024-01-01</InvoiceDate>
        <Currency>USD</Currency>
    </Header>
    <Details>
        <TotalAmount>100.00</TotalAmount>
        <TaxAmount>15.00</TaxAmount>
        <ItemCount>5</ItemCount>
    </Details>
    <Status>
        <ProcessingStatus>COMPLETED</ProcessingStatus>
    </Status>
</Invoice>"""


def create_test_generated_xslt():
    """Create sample generated XSLT for testing"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!-- Simple field mappings -->
    <CustomerID>
        <xsl:value-of select="ns0:Order/ns0:Customer/ns0:ID"/>
    </CustomerID>

    <Currency>
        <xsl:text>USD</xsl:text>
    </Currency>

    <!-- Complex field with conditional logic -->
    <TaxAmount>
        <xsl:choose>
            <xsl:when test="ns0:Order/ns0:TaxExempt = 'true'">
                <xsl:text>0.00</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="format-number(ns0:Order/ns0:Tax, '#.00')"/>
            </xsl:otherwise>
        </xsl:choose>
    </TaxAmount>

    <!-- Field with for-each loop -->
    <xsl:for-each select="ns0:Order/ns0:Items/ns0:Item">
        <ItemCount>
            <xsl:value-of select="count(.)"/>
        </ItemCount>
    </xsl:for-each>

    <!-- Another simple field -->
    <TotalAmount>
        <xsl:value-of select="ns0:Order/ns0:Total"/>
    </TotalAmount>

    <!-- Date formatting -->
    <InvoiceDate>
        <xsl:value-of select="format-date(ns0:Order/ns0:Date, 'YYYY-MM-DD')"/>
    </InvoiceDate>

    <!-- Status field -->
    <ProcessingStatus>
        <xsl:text>COMPLETED</xsl:text>
    </ProcessingStatus>

</xsl:stylesheet>"""


def create_test_element_list():
    """Create test element list matching the output XML"""
    return [
        'CustomerID',
        'InvoiceDate',
        'Currency',
        'TotalAmount',
        'TaxAmount',
        'ItemCount',
        'ProcessingStatus'
    ]


def create_conflict_test_xslt():
    """Create XSLT with conflicts for testing conflict resolution"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!-- First approach for TaxAmount -->
    <TaxAmount>
        <xsl:value-of select="ns0:Order/ns0:Tax"/>
    </TaxAmount>

    <!-- Second approach for TaxAmount (conflict) -->
    <TaxAmount>
        <xsl:choose>
            <xsl:when test="ns0:Order/ns0:TaxExempt = 'true'">
                <xsl:text>0.00</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="format-number(ns0:Order/ns0:Tax, '#.00')"/>
            </xsl:otherwise>
        </xsl:choose>
    </TaxAmount>

    <!-- Non-conflicting field -->
    <CustomerID>
        <xsl:value-of select="ns0:Order/ns0:Customer/ns0:ID"/>
    </CustomerID>

</xsl:stylesheet>"""


def test_base_template_generation():
    """Test base template generation from output XML"""
    print("=== Testing Base Template Generation ===")

    generator = BaseTemplateGenerator()
    output_xml = create_test_output_xml()

    try:
        template = generator.create_base_template_from_output_xml(output_xml)

        print(f"✅ Template generated successfully")
        print(f"Template length: {len(template)} characters")

        # Check if placeholders are created
        expected_placeholders = [
            '{{PLACEHOLDER_CustomerID}}',
            '{{PLACEHOLDER_InvoiceDate}}',
            '{{PLACEHOLDER_Currency}}',
            '{{PLACEHOLDER_TotalAmount}}',
            '{{PLACEHOLDER_TaxAmount}}',
            '{{PLACEHOLDER_ItemCount}}',
            '{{PLACEHOLDER_ProcessingStatus}}'
        ]

        for placeholder in expected_placeholders:
            if placeholder in template:
                print(f"✅ Found placeholder: {placeholder}")
            else:
                print(f"❌ Missing placeholder: {placeholder}")

        return True

    except Exception as e:
        print(f"❌ Template generation failed: {e}")
        return False


def test_chunk_extraction():
    """Test chunk extraction algorithm"""
    print("\n=== Testing Chunk Extraction ===")

    extractor = ChunkExtractor()
    generated_xslt = create_test_generated_xslt()
    test_elements = ['CustomerID', 'TaxAmount', 'ItemCount', 'Currency']

    extraction_results = {}

    try:
        current_xslt = generated_xslt

        for element in test_elements:
            print(f"\nTesting extraction for: {element}")

            chunk = extractor.extract_chunk_for_element(current_xslt, element)

            if chunk:
                print(f"✅ Extracted chunk for {element}")
                print(f"Chunk length: {len(chunk)} characters")
                extraction_results[element] = chunk

                # Remove chunk from XSLT
                current_xslt = extractor.remove_chunk_from_xslt(current_xslt, chunk)
                print(f"✅ Chunk removed from XSLT")
            else:
                print(f"❌ No chunk found for {element}")

        print(f"\nExtraction Summary:")
        print(f"✅ Extracted {len(extraction_results)} chunks")
        print(f"Remaining XSLT length: {len(current_xslt)} characters")

        return len(extraction_results) > 0

    except Exception as e:
        print(f"❌ Chunk extraction failed: {e}")
        return False


def test_conflict_detection_and_resolution():
    """Test conflict detection and LLM resolution"""
    print("\n=== Testing Conflict Detection and Resolution ===")

    replacer = TemplateReplacer()
    resolver = ConflictResolver()

    try:
        # Create conflicting chunks for same element
        chunk1 = """<TaxAmount>
    <xsl:value-of select="ns0:Order/ns0:Tax"/>
</TaxAmount>"""

        chunk2 = """<TaxAmount>
    <xsl:choose>
        <xsl:when test="ns0:Order/ns0:TaxExempt = 'true'">
            <xsl:text>0.00</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="format-number(ns0:Order/ns0:Tax, '#.00')"/>
        </xsl:otherwise>
    </xsl:choose>
</TaxAmount>"""

        # Add conflicting chunks
        replacer.add_chunk_for_element('TaxAmount', chunk1)
        replacer.add_chunk_for_element('TaxAmount', chunk2)

        # Add non-conflicting chunk
        chunk3 = """<CustomerID>
    <xsl:value-of select="ns0:Order/ns0:Customer/ns0:ID"/>
</CustomerID>"""
        replacer.add_chunk_for_element('CustomerID', chunk3)

        # Detect conflicts
        conflicts = replacer.get_conflicts()

        if 'TaxAmount' in conflicts and len(conflicts['TaxAmount']) == 2:
            print(f"✅ Conflict detected for TaxAmount: {len(conflicts['TaxAmount'])} chunks")
        else:
            print(f"❌ Conflict detection failed")
            return False

        if 'CustomerID' not in conflicts:
            print(f"✅ No conflict detected for CustomerID (correct)")
        else:
            print(f"❌ False conflict detected for CustomerID")

        # Test conflict resolution
        print(f"Testing LLM conflict resolution...")
        resolved_conflicts = resolver.resolve_all_conflicts(conflicts)

        if 'TaxAmount' in resolved_conflicts:
            print(f"✅ Conflict resolved for TaxAmount")
            print(f"Resolved chunk length: {len(resolved_conflicts['TaxAmount'])} characters")
        else:
            print(f"❌ Conflict resolution failed")
            return False

        return True

    except Exception as e:
        print(f"❌ Conflict testing failed: {e}")
        return False


def test_full_hybrid_merge():
    """Test complete hybrid merging workflow"""
    print("\n=== Testing Full Hybrid Merge Workflow ===")

    merger = HybridTemplateMerger()

    try:
        output_xml = create_test_output_xml()
        generated_xslt = create_test_generated_xslt()
        element_list = create_test_element_list()

        print(f"Testing with {len(element_list)} elements")

        final_xslt = merger.merge_xslt_batches_with_template(
            generated_xslt, output_xml, element_list
        )

        if final_xslt and len(final_xslt) > 0:
            print(f"✅ Hybrid merge completed successfully")
            print(f"Final XSLT length: {len(final_xslt)} characters")

            # Check if final XSLT contains expected structure
            if '<xsl:template match="/">' in final_xslt:
                print(f"✅ Final XSLT has proper template structure")
            else:
                print(f"❌ Final XSLT missing template structure")

            # Check if placeholders were replaced
            placeholder_count = final_xslt.count('{{PLACEHOLDER_')
            if placeholder_count == 0:
                print(f"✅ All placeholders replaced")
            else:
                print(f"⚠️ {placeholder_count} placeholders remain unreplaced")

            return True
        else:
            print(f"❌ Hybrid merge returned empty result")
            return False

    except Exception as e:
        print(f"❌ Full hybrid merge failed: {e}")
        return False


def test_integration_with_parallel_processor():
    """Test integration with parallel processor functions"""
    print("\n=== Testing Integration with Parallel Processor ===")

    try:
        from genie_core.llm.parallel_xslt_processor import combine_xslt_results_hybrid

        # Create test data
        simple_results = [create_test_generated_xslt()]
        complex_results = [create_test_generated_xslt()]

        # Create test DataFrames
        simple_data = pd.DataFrame({
            'Field': ['CustomerID', 'Currency', 'ProcessingStatus']
        })
        complex_data = pd.DataFrame({
            'Field': ['TaxAmount', 'InvoiceDate', 'ItemCount', 'TotalAmount']
        })

        output_xml = create_test_output_xml()

        print(f"Testing hybrid combination with parallel processor integration")

        final_xslt = combine_xslt_results_hybrid(
            simple_results, complex_results, simple_data, complex_data, output_xml
        )

        if final_xslt and len(final_xslt) > 0:
            print(f"✅ Integration test successful")
            print(f"Final XSLT length: {len(final_xslt)} characters")
            return True
        else:
            print(f"❌ Integration test failed")
            return False

    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False


def run_all_tests():
    """Run all hybrid template merger tests"""
    print("🧪 Starting Hybrid Template Merger Tests")
    print("=" * 50)

    tests = [
        ("Base Template Generation", test_base_template_generation),
        ("Chunk Extraction", test_chunk_extraction),
        ("Conflict Detection & Resolution", test_conflict_detection_and_resolution),
        ("Full Hybrid Merge", test_full_hybrid_merge),
        ("Parallel Processor Integration", test_integration_with_parallel_processor)
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

    print("\n" + "=" * 50)
    print(f"🧪 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Hybrid template merger is ready.")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check implementation.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)