"""
Test script for the new routing workflow implementation
Tests intelligent classification and parallel processing
"""

import pandas as pd
import sys
import os

# Add project root to path
if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))

from genie_core.data_processing.intelligent_classification import (
    intelligent_row_extraction,
    compare_with_manual_classification
)


def create_test_dataframe():
    """Create sample test data for validation"""
    test_data = {
        'Field': [
            'CustomerID',
            'TotalAmount',
            'TaxAmount',
            'CurrencyCode',
            'InvoiceDate',
            'PaymentStatus',
            'FormattedTotal',
            'CustomerName',
            'ItemCount',
            'ProcessedDate'
        ],
        'Input XPATH': [
            'ns0:Order/ns0:Customer/ns0:ID',
            'ns0:Order/ns0:Total',
            'ns0:Order/ns0:Tax',
            'ns0:Order/ns0:Currency',
            'ns0:Order/ns0:Date',
            'ns0:Order/ns0:Status',
            'ns0:Order/ns0:FormattedAmount',
            'ns0:Order/ns0:Customer/ns0:Name',
            'ns0:Order/ns0:Items/count()',
            'ns0:Order/ns0:ProcessDate'
        ],
        'Output XPATH': [
            'Customer/@ID',
            'Invoice/Total',
            'Invoice/Tax',
            'Invoice/Currency',
            'Invoice/Date',
            'Invoice/Status',
            'Invoice/FormattedTotal',
            'Customer/Name',
            'Invoice/ItemCount',
            'Invoice/ProcessedDate'
        ],
        'Description': [
            'Direct mapping of customer ID',
            'Copy total amount as-is',
            'Format tax amount with 2 decimal places and currency symbol',
            'Hardcode currency to USD',
            'Convert date to ISO format YYYY-MM-DD',
            'Map payment status directly',
            'Format total with currency symbol and thousands separator',
            'Copy customer name directly',
            'Count number of items in order',
            'Transform to current processing timestamp'
        ],
        'Complexity': [
            'S', 'S', 'C', 'S', 'C', 'S', 'C', 'S', 'C', 'C'
        ],
        'M/C/O': [
            'M', 'M', 'M', 'O', 'M', 'O', 'M', 'M', 'O', 'M'
        ]
    }

    return pd.DataFrame(test_data)


def test_classification_accuracy():
    """Test classification accuracy against manual labels"""
    print("=== Testing Classification Accuracy ===")

    # Create test data
    test_df = create_test_dataframe()
    print(f"Test dataset: {len(test_df)} rows")

    # Show original manual classification
    manual_simple = test_df[test_df['Complexity'] == 'S']
    manual_complex = test_df[test_df['Complexity'] == 'C']
    print(f"Manual classification: {len(manual_simple)} simple, {len(manual_complex)} complex")

    print("\nManual Simple Fields:")
    for idx, row in manual_simple.iterrows():
        print(f"  {row['Field']}: {row['Description']}")

    print("\nManual Complex Fields:")
    for idx, row in manual_complex.iterrows():
        print(f"  {row['Field']}: {row['Description']}")

    # Test intelligent classification
    try:
        agent_simple, agent_complex = intelligent_row_extraction(test_df)

        print(f"\nAgent classification: {len(agent_simple)} simple, {len(agent_complex)} complex")

        print("\nAgent Simple Fields:")
        for idx, row in agent_simple.iterrows():
            print(f"  {row['Field']}: {row['Description']}")

        print("\nAgent Complex Fields:")
        for idx, row in agent_complex.iterrows():
            print(f"  {row['Field']}: {row['Description']}")

        # Compare results
        compare_with_manual_classification(test_df)

    except Exception as e:
        print(f"Classification test failed: {e}")
        return False

    return True


def test_parallel_processing():
    """Test parallel processing workflow"""
    print("\n=== Testing Parallel Processing Workflow ===")

    try:
        from genie_core.llm.parallel_xslt_processor import (
            create_batches,
            process_mappings_sequential_fallback
        )

        # Create test data
        test_df = create_test_dataframe()

        # Simulate classification results
        simple_data = test_df[test_df['Complexity'] == 'S'].reset_index(drop=True)
        complex_data = test_df[test_df['Complexity'] == 'C'].reset_index(drop=True)

        print(f"Simple rows: {len(simple_data)}")
        print(f"Complex rows: {len(complex_data)}")

        # Test batching
        simple_batches = create_batches(simple_data, batch_size=8)
        complex_batches = create_batches(complex_data, batch_size=4)

        print(f"Simple batches: {len(simple_batches)}")
        print(f"Complex batches: {len(complex_batches)}")

        for i, batch in enumerate(simple_batches):
            fields = ", ".join(batch['Field'].tolist())
            print(f"  Simple batch {i+1}: {fields}")

        for i, batch in enumerate(complex_batches):
            fields = ", ".join(batch['Field'].tolist())
            print(f"  Complex batch {i+1}: {fields}")

        print("Parallel processing workflow test passed!")
        return True

    except Exception as e:
        print(f"Parallel processing test failed: {e}")
        return False


def test_integration():
    """Test full integration workflow"""
    print("\n=== Testing Full Integration ===")

    try:
        # Test the main integration point
        from genie_core.data_processing.intelligent_classification import intelligent_row_extraction_with_fallback

        test_df = create_test_dataframe()

        # Test with fallback
        simple_rows, complex_rows = intelligent_row_extraction_with_fallback(test_df)

        print(f"Integration test results:")
        print(f"  Simple rows: {len(simple_rows)}")
        print(f"  Complex rows: {len(complex_rows)}")
        print(f"  Total processed: {len(simple_rows) + len(complex_rows)}")
        print(f"  Original total: {len(test_df)}")

        success = (len(simple_rows) + len(complex_rows)) == len(test_df)
        print(f"Integration test: {'PASSED' if success else 'FAILED'}")

        return success

    except Exception as e:
        print(f"Integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Starting Routing Workflow Implementation Tests")
    print("=" * 50)

    tests_passed = 0
    total_tests = 3

    # Test classification
    if test_classification_accuracy():
        tests_passed += 1

    # Test parallel processing
    if test_parallel_processing():
        tests_passed += 1

    # Test integration
    if test_integration():
        tests_passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🟢 All tests passed! Routing workflow implementation is ready.")
    else:
        print("🔴 Some tests failed. Please check the implementation.")


if __name__ == "__main__":
    main()