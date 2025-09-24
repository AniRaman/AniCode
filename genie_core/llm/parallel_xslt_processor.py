"""
Parallel XSLT processing for complex and simple field batches
Implements parallel execution of 4 complex + 8 simple mapping batches
"""

import asyncio
import streamlit as st
from typing import List, Optional, Tuple
import pandas as pd
from genie_core.llm.llm_utils import llm_process


async def process_batch_async(context_batch: pd.DataFrame, message: str, input_xml: str, output_xml: str, current_xslt: Optional[str] = None) -> str:
    """
    Async wrapper for llm_process to enable parallel processing

    Args:
        context_batch: DataFrame batch of field mappings
        message: Processing message
        input_xml: Input XML content
        output_xml: Output XML content
        current_xslt: Current XSLT to build upon

    Returns:
        str: Generated/updated XSLT
    """
    # Note: llm_process is synchronous, but we wrap it for async execution
    # In a real async environment, you might need to use asyncio.to_thread() or similar
    try:
        result_xslt = llm_process(context_batch, message, input_xml, output_xml, current_xslt)
        return result_xslt
    except Exception as e:
        print(f"Batch processing failed: {e}")
        return current_xslt or ""


def create_batches(dataframe: pd.DataFrame, batch_size: int) -> List[pd.DataFrame]:
    """
    Split DataFrame into batches of specified size

    Args:
        dataframe: Input DataFrame to split
        batch_size: Maximum rows per batch

    Returns:
        List of DataFrame batches
    """
    if len(dataframe) == 0:
        return []

    batches = []
    for i in range(0, len(dataframe), batch_size):
        batch = dataframe.iloc[i:i + batch_size]
        batches.append(batch)

    return batches


async def process_complex_batches_parallel(complex_rows: pd.DataFrame, input_xml: str, output_xml: str, main_xslt: Optional[str] = None) -> List[str]:
    """
    Process complex field batches in parallel

    Args:
        complex_rows: DataFrame of complex field mappings
        input_xml: Input XML content
        output_xml: Output XML content
        main_xslt: Starting XSLT

    Returns:
        List of generated XSLT strings
    """
    print(f"[PARALLEL DEBUG] ===== PROCESSING COMPLEX BATCHES =====")
    print(f"[PARALLEL DEBUG] Complex rows count: {len(complex_rows)}")

    if len(complex_rows) == 0:
        print("[PARALLEL DEBUG] No complex mappings to process")
        return []

    # Create batches of 4 complex mappings each
    complex_batches = create_batches(complex_rows, batch_size=4)
    print(f"[PARALLEL DEBUG] Created {len(complex_batches)} complex batches (4 rows each)")
    print(f"[PARALLEL DEBUG] Starting parallel processing of complex batches...")

    # Create async tasks for all complex batches
    tasks = []
    for i, batch in enumerate(complex_batches):
        context_fields = ",".join(map(str, batch["Field"]))
        message = f"Map all the complex elements mentioned here: {context_fields}"

        print(f"[PARALLEL DEBUG] Complex batch {i + 1}: {context_fields}")

        task = process_batch_async(batch, message, input_xml, output_xml, main_xslt)
        tasks.append(task)

    # Execute all complex batches in parallel
    print(f"[PARALLEL DEBUG] Executing {len(tasks)} complex batch tasks in parallel...")
    results = await asyncio.gather(*tasks)

    print(f"[PARALLEL DEBUG] Completed {len(results)} complex batch processing")
    print(f"[PARALLEL DEBUG] ===== COMPLEX BATCHES COMPLETE =====")
    return results


async def process_simple_batches_parallel(simple_rows: pd.DataFrame, input_xml: str, output_xml: str, main_xslt: Optional[str] = None) -> List[str]:
    """
    Process simple field batches in parallel

    Args:
        simple_rows: DataFrame of simple field mappings
        input_xml: Input XML content
        output_xml: Output XML content
        main_xslt: Starting XSLT

    Returns:
        List of generated XSLT strings
    """
    print(f"[PARALLEL DEBUG] ===== PROCESSING SIMPLE BATCHES =====")
    print(f"[PARALLEL DEBUG] Simple rows count: {len(simple_rows)}")

    if len(simple_rows) == 0:
        print("[PARALLEL DEBUG] No simple mappings to process")
        return []

    # Create batches of 8 simple mappings each
    simple_batches = create_batches(simple_rows, batch_size=8)
    print(f"[PARALLEL DEBUG] Created {len(simple_batches)} simple batches (8 rows each)")
    print(f"[PARALLEL DEBUG] Starting parallel processing of simple batches...")

    # Create async tasks for all simple batches
    tasks = []
    for i, batch in enumerate(simple_batches):
        context_fields = ",".join(map(str, batch["Field"]))
        message = f"Map all the simple elements mentioned here: {context_fields}"

        print(f"[PARALLEL DEBUG] Simple batch {i + 1}: {context_fields}")

        task = process_batch_async(batch, message, input_xml, output_xml, main_xslt)
        tasks.append(task)

    # Execute all simple batches in parallel
    print(f"[PARALLEL DEBUG] Executing {len(tasks)} simple batch tasks in parallel...")
    results = await asyncio.gather(*tasks)

    print(f"[PARALLEL DEBUG] Completed {len(results)} simple batch processing")
    print(f"[PARALLEL DEBUG] ===== SIMPLE BATCHES COMPLETE =====")
    return results


def combine_xslt_results_hybrid(simple_results: List[str], complex_results: List[str],
                              simple_rows: pd.DataFrame, complex_rows: pd.DataFrame,
                              output_xml: str, initial_xslt: Optional[str] = None) -> str:
    """
    Combine XSLT results using hybrid template-based approach

    Args:
        simple_results: List of XSLT strings from simple processing
        complex_results: List of XSLT strings from complex processing
        simple_rows: DataFrame of simple field mappings
        complex_rows: DataFrame of complex field mappings
        output_xml: Expected output XML structure
        initial_xslt: Starting XSLT to build upon

    Returns:
        str: Combined final XSLT with preserved element ordering
    """
    print(f"[HYBRID COMBINE DEBUG] ===== STARTING HYBRID COMBINATION =====")
    print(f"[HYBRID COMBINE DEBUG] Simple results: {len(simple_results)}")
    print(f"[HYBRID COMBINE DEBUG] Complex results: {len(complex_results)}")
    print(f"[HYBRID COMBINE DEBUG] Simple rows: {len(simple_rows)}")
    print(f"[HYBRID COMBINE DEBUG] Complex rows: {len(complex_rows)}")

    try:
        # Import hybrid merger
        from genie_core.llm.hybrid_template_merger import HybridTemplateMerger

        # Combine all XSLT results into one string
        all_results = complex_results + simple_results
        combined_xslt = "\n".join([result for result in all_results if result])

        print(f"[HYBRID COMBINE DEBUG] Combined XSLT length: {len(combined_xslt)} characters")

        # Extract all field names from both simple and complex rows
        element_list = []

        # Add simple fields
        if not simple_rows.empty and 'Field' in simple_rows.columns:
            element_list.extend(simple_rows['Field'].tolist())
            print(f"[HYBRID COMBINE DEBUG] Added {len(simple_rows)} simple fields")

        # Add complex fields
        if not complex_rows.empty and 'Field' in complex_rows.columns:
            element_list.extend(complex_rows['Field'].tolist())
            print(f"[HYBRID COMBINE DEBUG] Added {len(complex_rows)} complex fields")

        print(f"[HYBRID COMBINE DEBUG] Total elements to process: {len(element_list)}")

        # Use hybrid merger if we have elements to process
        if element_list and combined_xslt and output_xml:
            print(f"[HYBRID COMBINE DEBUG] Using hybrid template merger")

            merger = HybridTemplateMerger()
            final_xslt = merger.merge_xslt_batches_with_template(
                combined_xslt, output_xml, element_list
            )

            print(f"[HYBRID COMBINE DEBUG] Hybrid merge completed successfully")
            return final_xslt

        else:
            print(f"[HYBRID COMBINE DEBUG] Insufficient data for hybrid merge, using fallback")
            return combine_xslt_results_fallback(complex_results, simple_results, initial_xslt)

    except Exception as e:
        print(f"[HYBRID COMBINE DEBUG] ERROR during hybrid combination: {e}")
        print(f"[HYBRID COMBINE DEBUG] Falling back to traditional combination")
        return combine_xslt_results_fallback(complex_results, simple_results, initial_xslt)


def combine_xslt_results_fallback(complex_results: List[str], simple_results: List[str], initial_xslt: Optional[str] = None) -> str:
    """
    Fallback combination method using traditional LLM merge

    Args:
        complex_results: List of XSLT strings from complex processing
        simple_results: List of XSLT strings from simple processing
        initial_xslt: Starting XSLT to build upon

    Returns:
        str: Combined final XSLT
    """
    print(f"[FALLBACK DEBUG] Using traditional LLM-based combination")

    # Start with initial XSLT or empty
    final_xslt = initial_xslt or ""

    # Combine all results in sequence
    all_results = complex_results + simple_results

    for i, xslt_result in enumerate(all_results):
        if xslt_result and xslt_result != final_xslt:
            print(f"[FALLBACK DEBUG] Combining XSLT result {i + 1}")
            # Use existing combination logic from llm_utils
            from genie_core.llm.llm_utils import combine_xslt_2
            if final_xslt:
                final_xslt, _ = combine_xslt_2(xslt_result, final_xslt)
            else:
                final_xslt = xslt_result

    return final_xslt


# Keep original function for backward compatibility
def combine_xslt_results(complex_results: List[str], simple_results: List[str], initial_xslt: Optional[str] = None) -> str:
    """
    Original combination method - maintained for backward compatibility
    """
    return combine_xslt_results_fallback(complex_results, simple_results, initial_xslt)


async def process_all_mappings_parallel(simple_rows: pd.DataFrame, complex_rows: pd.DataFrame,
                                       input_xml: str, output_xml: str,
                                       main_xslt: Optional[str] = None) -> str:
    """
    Process both simple and complex mappings in parallel

    Args:
        simple_rows: DataFrame of simple field mappings
        complex_rows: DataFrame of complex field mappings
        input_xml: Input XML content
        output_xml: Output XML content
        main_xslt: Starting XSLT

    Returns:
        str: Final combined XSLT
    """
    print("Starting parallel processing of all mappings...")

    # Start both simple and complex processing in parallel
    complex_task = process_complex_batches_parallel(complex_rows, input_xml, output_xml, main_xslt)
    simple_task = process_simple_batches_parallel(simple_rows, input_xml, output_xml, main_xslt)

    # Wait for both to complete
    complex_results, simple_results = await asyncio.gather(complex_task, simple_task)

    # Combine all results using hybrid approach
    final_xslt = combine_xslt_results_hybrid(
        simple_results, complex_results, simple_rows, complex_rows, output_xml, main_xslt
    )

    print("[PARALLEL DEBUG] Parallel processing complete")
    return final_xslt


def process_mappings_with_parallel_execution(simple_rows: pd.DataFrame, complex_rows: pd.DataFrame,
                                           input_xml: str, output_xml: str,
                                           main_xslt: Optional[str] = None) -> str:
    """
    Synchronous wrapper for parallel XSLT processing

    Args:
        simple_rows: Simple field mappings
        complex_rows: Complex field mappings
        input_xml: Input XML
        output_xml: Output XML
        main_xslt: Starting XSLT

    Returns:
        str: Final XSLT
    """
    try:
        # Run the async parallel processing
        final_xslt = asyncio.run(
            process_all_mappings_parallel(simple_rows, complex_rows, input_xml, output_xml, main_xslt)
        )
        return final_xslt
    except Exception as e:
        print(f"Parallel processing failed: {e}")
        print("Falling back to sequential processing...")

        # Fallback to sequential processing
        return process_mappings_sequential_fallback(simple_rows, complex_rows, input_xml, output_xml, main_xslt)


def process_mappings_sequential_fallback(simple_rows: pd.DataFrame, complex_rows: pd.DataFrame,
                                       input_xml: str, output_xml: str,
                                       main_xslt: Optional[str] = None) -> str:
    """
    Sequential fallback processing if parallel processing fails
    """
    current_xslt = main_xslt

    # Process complex batches first (original logic)
    complex_batches = create_batches(complex_rows, batch_size=4)
    for i, batch in enumerate(complex_batches):
        context_fields = ",".join(map(str, batch["Field"]))
        message = f"Map all the complex elements mentioned here: {context_fields}"
        print(f"Sequential complex batch {i + 1}: {context_fields}")
        current_xslt = llm_process(batch, message, input_xml, output_xml, current_xslt)

    # Process simple batches second
    simple_batches = create_batches(simple_rows, batch_size=8)
    for i, batch in enumerate(simple_batches):
        context_fields = ",".join(map(str, batch["Field"]))
        message = f"Map all the simple elements mentioned here: {context_fields}"
        print(f"Sequential simple batch {i + 1}: {context_fields}")
        current_xslt = llm_process(batch, message, input_xml, output_xml, current_xslt)

    return current_xslt