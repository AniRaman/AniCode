"""
Parallel XSLT processing for complex and simple field batches
Implements parallel execution of 4 complex + 8 simple mapping batches
"""

import asyncio
import streamlit as st
from typing import List, Optional, Tuple, NamedTuple
import pandas as pd
from genie_core.llm.llm_utils import llm_process, llm_process_async


async def process_batch_async(context_batch: pd.DataFrame, message: str, input_xml: str, output_xml: str, current_xslt: Optional[str] = None) -> str:
    """
    True async processing using llm_process_async for non-blocking parallel execution

    Args:
        context_batch: DataFrame batch of field mappings
        message: Processing message
        input_xml: Input XML content
        output_xml: Output XML content
        current_xslt: Current XSLT to build upon

    Returns:
        str: Generated/updated XSLT
    """
    print(f"[BATCH DEBUG] process_batch_async called with {len(context_batch)} rows")
    print(f"[BATCH DEBUG] About to call llm_process_async...")

    try:
        result_xslt = await llm_process_async(context_batch, message, input_xml, output_xml, current_xslt)
        print(f"[BATCH DEBUG] llm_process_async returned: {len(result_xslt) if result_xslt else 0} characters")
        return result_xslt
    except Exception as e:
        print(f"[BATCH DEBUG] Batch processing failed: {e}")
        import traceback
        traceback.print_exc()
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


def process_mappings_with_realtime_merging(simple_rows: pd.DataFrame, complex_rows: pd.DataFrame,
                                         input_xml: str, output_xml: str,
                                         main_xslt: Optional[str] = None) -> str:
    """
    Real-time template merging: Create base template first, then merge each batch as it completes

    Args:
        simple_rows: DataFrame of simple field mappings
        complex_rows: DataFrame of complex field mappings
        input_xml: Input XML content
        output_xml: Output XML content
        main_xslt: Starting XSLT

    Returns:
        str: Final XSLT with real-time merged batches
    """
    print("[REALTIME DEBUG] ===== STARTING REAL-TIME TEMPLATE MERGING =====")

    # Step 1: Create base template FIRST (before any parallel processing)
    print("[REALTIME DEBUG] Step 1: Creating base template from output XML")
    from genie_core.llm.hybrid_template_merger import BaseTemplateGenerator

    template_generator = BaseTemplateGenerator()
    base_template = template_generator.create_base_template_from_output_xml(output_xml)

    # Extract element list for processing order
    element_list = []
    if not simple_rows.empty and 'Field' in simple_rows.columns:
        element_list.extend(simple_rows['Field'].tolist())
    if not complex_rows.empty and 'Field' in complex_rows.columns:
        element_list.extend(complex_rows['Field'].tolist())

    print(f"[REALTIME DEBUG] Base template created, processing {len(element_list)} elements")
    print(f"[REALTIME DEBUG] Elements to process: {element_list}")

    # Show initial base template
    initial_placeholders = base_template.count('{{PLACEHOLDER_')
    print(f"[REALTIME DEBUG] Initial base template:")
    print(f"[REALTIME DEBUG] Template length: {len(base_template)} characters")
    print(f"[REALTIME DEBUG] Initial placeholders: {initial_placeholders}")
    print("-" * 50)
    print(base_template[:500] + ("..." if len(base_template) > 500 else ""))
    print("-" * 50)

    # Step 2: Start parallel processing with real-time merging
    try:
        return asyncio.run(process_with_realtime_template_updates(
            simple_rows, complex_rows, input_xml, output_xml,
            base_template, element_list, main_xslt
        ))
    except Exception as e:
        print(f"[REALTIME DEBUG] Real-time merging failed: {e}")
        print("[REALTIME DEBUG] Falling back to original parallel processing")
        return process_mappings_with_parallel_execution(simple_rows, complex_rows, input_xml, output_xml, main_xslt)


class BatchResult(NamedTuple):
    batch_type: str  # "simple" or "complex"
    batch_id: int
    result_xslt: str
    fields: List[str]


async def process_with_realtime_template_updates(simple_rows: pd.DataFrame, complex_rows: pd.DataFrame,
                                               input_xml: str, output_xml: str,
                                               base_template: str, element_list: List[str],
                                               main_xslt: Optional[str] = None) -> str:
    """
    TRUE real-time approach: Parallel processing + immediate template updates via asyncio queue

    Args:
        simple_rows: DataFrame of simple field mappings
        complex_rows: DataFrame of complex field mappings
        input_xml: Input XML content
        output_xml: Output XML content
        base_template: Pre-created base template with placeholders
        element_list: List of elements to process in order
        main_xslt: Starting XSLT

    Returns:
        str: Final XSLT with true real-time merged batches
    """
    print("[REALTIME DEBUG] ===== TRUE REAL-TIME PROCESSING WITH ASYNCIO QUEUE =====")

    # Import hybrid merger components
    from genie_core.llm.hybrid_template_merger import ChunkExtractor, TemplateReplacer

    chunk_extractor = ChunkExtractor()
    template_replacer = TemplateReplacer()

    # Setup asyncio queue for batch completions
    completion_queue = asyncio.Queue()
    current_template = base_template
    processed_elements = set()

    print(f"[REALTIME DEBUG] Starting parallel processing with asyncio queue")
    print(f"[REALTIME DEBUG] Simple batches: {len(simple_rows)}, Complex batches: {len(complex_rows)}")

    # Strategy 1: Sequential Groups with Real-Time Updates Within Groups

    # Phase 1: Complex batches with real-time updates
    print(f"[REALTIME DEBUG] === PHASE 1: COMPLEX BATCHES ===")
    if len(complex_rows) > 0:
        current_template = await process_group_with_realtime_updates(
            complex_rows, "complex", 4, input_xml, output_xml, main_xslt,
            completion_queue, current_template, processed_elements,
            chunk_extractor, template_replacer
        )
    else:
        print(f"[REALTIME DEBUG] No complex batches to process")

    # Phase 2: Simple batches with real-time updates
    print(f"[REALTIME DEBUG] === PHASE 2: SIMPLE BATCHES ===")
    if len(simple_rows) > 0:
        current_template = await process_group_with_realtime_updates(
            simple_rows, "simple", 8, input_xml, output_xml, main_xslt,
            completion_queue, current_template, processed_elements,
            chunk_extractor, template_replacer
        )
    else:
        print(f"[REALTIME DEBUG] No simple batches to process")

    print(f"[REALTIME DEBUG] Both phases completed with sequential groups strategy")

    print(f"[REALTIME DEBUG] TRUE real-time processing complete!")
    print(f"[REALTIME DEBUG] Processed {len(processed_elements)} elements via real-time updates")
    print(f"[REALTIME DEBUG] Final template length: {len(current_template)} characters")

    return current_template


async def process_group_with_realtime_updates(rows: pd.DataFrame, group_type: str, batch_size: int,
                                            input_xml: str, output_xml: str, main_xslt: str,
                                            completion_queue: asyncio.Queue, current_template: str,
                                            processed_elements: set, chunk_extractor, template_replacer) -> str:
    """
    Process a group of batches (complex or simple) in parallel with real-time template updates

    Args:
        rows: DataFrame of field mappings for this group
        group_type: "complex" or "simple"
        batch_size: Size of each batch (4 for complex, 8 for simple)
        input_xml, output_xml, main_xslt: Standard processing inputs
        completion_queue: Queue for batch completions
        current_template: Current template state to update
        processed_elements: Set of already processed elements
        chunk_extractor, template_replacer: Processing components

    Returns:
        str: Updated template after processing this group
    """
    print(f"[GROUP DEBUG] Processing {group_type} group with {len(rows)} rows")

    # Create batches for this group
    batches = create_batches(rows, batch_size=batch_size)
    group_tasks = []

    print(f"[GROUP DEBUG] Created {len(batches)} {group_type} batches ({batch_size} fields each)")

    # Start all batches in this group in parallel
    for i, batch in enumerate(batches):
        context_fields = ",".join(map(str, batch["Field"]))
        message = f"Map all the {group_type} elements mentioned here: {context_fields}"
        fields_list = batch["Field"].tolist()

        task = process_batch_with_queue_async(
            batch, message, input_xml, output_xml, main_xslt,
            group_type, i, fields_list, completion_queue
        )
        group_tasks.append(task)

    print(f"[GROUP DEBUG] Started {len(group_tasks)} {group_type} batch tasks in parallel")

    # Start all group tasks in background (group_tasks contains coroutines, not tasks)
    group_results_task = asyncio.gather(*group_tasks)

    # Process completions in real-time as batches in this group complete
    total_group_batches = len(batches)
    completed_group_batches = 0

    print(f"[GROUP DEBUG] Processing {group_type} batch completions in real-time...")

    while completed_group_batches < total_group_batches:
        try:
            import time
            queue_wait_start = time.time()
            print(f"[TIMING DEBUG] [{group_type}] Waiting for next batch completion at {queue_wait_start:.2f}...")

            # Wait for next batch completion within this group
            batch_result = await completion_queue.get()

            queue_wait_end = time.time()
            wait_duration = queue_wait_end - queue_wait_start
            completed_group_batches += 1

            print(f"[TIMING DEBUG] [{group_type}] Got batch from queue after {wait_duration:.2f}s wait at {queue_wait_end:.2f}")
            print(f"[GROUP DEBUG] [{group_type}] Batch {completed_group_batches}/{total_group_batches} completed: {batch_result.batch_type}-{batch_result.batch_id}")
            print(f"[GROUP DEBUG] [{group_type}] Fields in batch: {batch_result.fields}")

            # Process each field in this completed batch
            for field_name in batch_result.fields:
                if field_name in processed_elements:
                    print(f"[GROUP DEBUG] [{group_type}] Field {field_name} already processed, skipping")
                    continue

                # Extract chunk from this batch's XSLT result
                chunk = chunk_extractor.extract_chunk_for_element(batch_result.result_xslt, field_name)

                if chunk:
                    print(f"[GROUP DEBUG] [{group_type}] Extracted chunk for {field_name}, updating template immediately")
                    print(f"[GROUP DEBUG] [{group_type}] Chunk content: {chunk[:200]}...")

                    # Update template immediately
                    previous_template_length = len(current_template)
                    current_template = template_replacer.replace_placeholder_with_chunk(
                        current_template, field_name, chunk
                    )

                    processed_elements.add(field_name)

                    # Show template evolution
                    remaining_placeholders = current_template.count('{{PLACEHOLDER_')
                    print(f"[GROUP DEBUG] [{group_type}] Template updated for {field_name} in real-time")
                    print(f"[GROUP DEBUG] [{group_type}] Template size: {previous_template_length} -> {len(current_template)} characters")
                    print(f"[GROUP DEBUG] [{group_type}] Remaining placeholders: {remaining_placeholders}")
                    print(f"[GROUP DEBUG] [{group_type}] Processed elements so far: {list(processed_elements)}")

                    # Show current template state (first 500 chars)
                    print(f"[GROUP DEBUG] [{group_type}] Current template state:")
                    print("-" * 50)
                    print(current_template[:500] + ("..." if len(current_template) > 500 else ""))
                    print("-" * 50)

                else:
                    print(f"[GROUP DEBUG] [{group_type}] No chunk found for {field_name}, ignoring")

            # Mark this queue item as processed
            completion_queue.task_done()

        except Exception as e:
            print(f"[GROUP DEBUG] [{group_type}] Error processing batch completion: {e}")
            completed_group_batches += 1  # Continue with other batches

    # Wait for all batches in this group to complete
    print(f"[GROUP DEBUG] [{group_type}] All batch completions processed, waiting for background tasks...")
    await group_results_task

    print(f"[GROUP DEBUG] [{group_type}] Group processing complete! Template updated with {len(processed_elements)} total elements")

    return current_template


async def process_batch_with_queue_async(batch: pd.DataFrame, message: str, input_xml: str, output_xml: str,
                                       main_xslt: Optional[str], batch_type: str, batch_id: int,
                                       fields_list: List[str], completion_queue: asyncio.Queue) -> str:
    """
    Process single batch and put completion result in asyncio queue for real-time processing
    """
    import time

    start_time = time.time()
    print(f"[TIMING DEBUG] {batch_type} batch {batch_id} STARTED at {start_time:.2f}: {fields_list}")

    # Use existing batch processing logic
    result = await process_batch_async(batch, message, input_xml, output_xml, main_xslt)

    end_time = time.time()
    duration = end_time - start_time
    print(f"[TIMING DEBUG] {batch_type} batch {batch_id} COMPLETED at {end_time:.2f}, took {duration:.2f}s")

    # Put completion result in queue for real-time processing
    batch_result = BatchResult(batch_type, batch_id, result, fields_list)
    await completion_queue.put(batch_result)

    print(f"[REALTIME DEBUG] {batch_type} batch {batch_id} queued for real-time processing")

    return result


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