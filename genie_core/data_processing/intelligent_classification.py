"""
Intelligent field classification for XSLT generation using agent-based approach
Replaces manual 'C/S' column with LLM-based classification
"""

import json
import pandas as pd
import asyncio
from typing import List, Dict, Tuple
from genie_core.llm.llm_utils import get_chat_completion


def classify_batch_with_agent(remarks_list: List[str], batch_index: int) -> Dict[str, str]:
    """
    Classify a batch of remarks using LLM agent

    Args:
        remarks_list: List of description/remarks strings (max 20 items)
        batch_index: Batch number for tracking

    Returns:
        Dict: {0: 'SIMPLE', 1: 'COMPLEX', ...} (indices within batch)
    """
    print(f"[ROUTING DEBUG] Starting classification for batch {batch_index + 1}")
    print(f"[ROUTING DEBUG] Batch size: {len(remarks_list)} rows")

    # Format remarks for prompt
    formatted_remarks = ""
    for i, remark in enumerate(remarks_list):
        clean_remark = str(remark).strip() if remark else "No description"
        formatted_remarks += f"{i}: {clean_remark}\n"
        print(f"[ROUTING DEBUG] Row {i}: '{clean_remark[:50]}{'...' if len(clean_remark) > 50 else ''}'")

    # Create focused classification prompt
    prompt = f"""
Classify each field description as SIMPLE or COMPLEX for XSLT generation:

SIMPLE: Direct mapping, hardcoded values, basic assignment, copy operations, static values
COMPLEX: Formatting, transformations, calculations, conditionals, string manipulation, date formatting, currency formatting, concatenation

Field descriptions to classify:
{formatted_remarks}

Return ONLY valid JSON in this exact format:
{{"0": "SIMPLE", "1": "COMPLEX", "2": "SIMPLE", "3": "COMPLEX"}}
"""

    try:
        print(f"[ROUTING DEBUG] Sending classification request for batch {batch_index + 1}")
        response = get_chat_completion([
            {"role": "system", "content": "You are an XSLT complexity classifier. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ])

        # Parse response
        response_text = response.choices[0].message.content.strip()
        print(f"[ROUTING DEBUG] LLM response for batch {batch_index + 1}: {response_text[:100]}...")

        classifications = parse_classification_response(response_text, len(remarks_list))

        # Log classification results
        simple_count = sum(1 for v in classifications.values() if v == 'SIMPLE')
        complex_count = sum(1 for v in classifications.values() if v == 'COMPLEX')
        print(f"[ROUTING DEBUG] Batch {batch_index + 1} results: {simple_count} SIMPLE, {complex_count} COMPLEX")

        return classifications

    except Exception as e:
        print(f"[ROUTING DEBUG] Classification batch {batch_index + 1} failed: {e}")
        # Fallback: mark all as COMPLEX for safety
        fallback_result = {str(i): 'COMPLEX' for i in range(len(remarks_list))}
        print(f"[ROUTING DEBUG] Using fallback classification for batch {batch_index + 1}: all COMPLEX")
        return fallback_result


def parse_classification_response(response_text: str, expected_count: int) -> Dict[str, str]:
    """
    Parse LLM JSON response into classification dict with validation

    Args:
        response_text: Raw LLM response
        expected_count: Expected number of classifications

    Returns:
        Dict: Classification results with fallback for errors
    """
    try:
        # Clean response text
        cleaned = response_text.strip()

        # Remove markdown code blocks if present
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:-3].strip()
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:-3].strip()

        # Parse JSON
        classifications = json.loads(cleaned)

        # Validate all expected indices are present
        for i in range(expected_count):
            if str(i) not in classifications:
                classifications[str(i)] = 'COMPLEX'  # Default missing to COMPLEX

        # Validate classification values
        valid_values = {'SIMPLE', 'COMPLEX'}
        for key, value in classifications.items():
            if value not in valid_values:
                classifications[key] = 'COMPLEX'  # Invalid values default to COMPLEX

        return classifications

    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON parsing failed: {e}")
        print(f"Response was: {response_text[:200]}...")

        # Complete fallback: all COMPLEX
        return {str(i): 'COMPLEX' for i in range(expected_count)}


async def classify_batch_async(remarks_list: List[str], batch_index: int) -> Dict[str, str]:
    """
    Async wrapper for batch classification to enable parallel processing
    """
    return classify_batch_with_agent(remarks_list, batch_index)


async def classify_all_batches_parallel(dataframe: pd.DataFrame, batch_size: int = 20) -> Dict[int, str]:
    """
    Classify all rows in parallel batches

    Args:
        dataframe: Input DataFrame with Description column
        batch_size: Size of each classification batch

    Returns:
        Dict: {row_index: classification} for all rows
    """
    remarks_list = dataframe['Description'].fillna('').tolist()
    total_rows = len(dataframe)

    # Create batch tasks
    tasks = []
    batch_info = []

    for batch_start in range(0, total_rows, batch_size):
        batch_end = min(batch_start + batch_size, total_rows)
        batch_remarks = remarks_list[batch_start:batch_end]
        batch_index = batch_start // batch_size

        # Create async task for this batch
        task = classify_batch_async(batch_remarks, batch_index)
        tasks.append(task)
        batch_info.append((batch_start, batch_end))

        print(f"Queued batch {batch_index + 1}: rows {batch_start+1}-{batch_end}")

    # Execute all batches in parallel
    print(f"Executing {len(tasks)} classification batches in parallel...")
    batch_results = await asyncio.gather(*tasks)

    # Combine results from all batches
    all_classifications = {}
    for i, (batch_start, batch_end) in enumerate(batch_info):
        batch_classifications = batch_results[i]

        # Map batch indices to global row indices
        for local_idx, classification in batch_classifications.items():
            global_idx = batch_start + int(local_idx)
            all_classifications[global_idx] = classification

    return all_classifications


def intelligent_row_extraction(dataframe: pd.DataFrame, batch_size: int = 20) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Replace manual C/S column classification with agent-based classification

    Args:
        dataframe: Input DataFrame with specs
        batch_size: Number of rows per classification batch

    Returns:
        Tuple: (simple_rows DataFrame, complex_rows DataFrame)
    """

    print(f"[ROUTING DEBUG] ===== STARTING INTELLIGENT CLASSIFICATION =====")
    print(f"[ROUTING DEBUG] Total rows to classify: {len(dataframe)}")
    print(f"[ROUTING DEBUG] Batch size: {batch_size}")
    print(f"[ROUTING DEBUG] Expected batches: {(len(dataframe) + batch_size - 1) // batch_size}")

    # Run parallel classification
    all_classifications = asyncio.run(classify_all_batches_parallel(dataframe, batch_size))

    # Split DataFrame based on classifications
    simple_indices = [i for i, cls in all_classifications.items() if cls == 'SIMPLE']
    complex_indices = [i for i, cls in all_classifications.items() if cls == 'COMPLEX']

    print(f"[ROUTING DEBUG] Classification results:")
    print(f"[ROUTING DEBUG]   Simple indices: {simple_indices}")
    print(f"[ROUTING DEBUG]   Complex indices: {complex_indices}")

    simple_rows = dataframe.iloc[simple_indices].reset_index(drop=True) if simple_indices else pd.DataFrame(columns=dataframe.columns)
    complex_rows = dataframe.iloc[complex_indices].reset_index(drop=True) if complex_indices else pd.DataFrame(columns=dataframe.columns)

    print(f"[ROUTING DEBUG] Final classification: {len(simple_rows)} SIMPLE, {len(complex_rows)} COMPLEX")
    print(f"[ROUTING DEBUG] ===== CLASSIFICATION COMPLETE =====")

    return simple_rows, complex_rows


def intelligent_row_extraction_with_fallback(dataframe: pd.DataFrame, batch_size: int = 20) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Intelligent classification with error handling

    Args:
        dataframe: Input DataFrame
        batch_size: Classification batch size

    Returns:
        Tuple: (simple_rows, complex_rows) DataFrames
    """
    try:
        return intelligent_row_extraction(dataframe, batch_size)
    except Exception as e:
        print(f"Intelligent classification failed: {e}")
        print("Falling back to all-COMPLEX classification for safety...")

        # Safe fallback: treat all as complex
        empty_df = pd.DataFrame(columns=dataframe.columns)
        return empty_df, dataframe


# Validation and testing functions
def compare_with_manual_classification(dataframe: pd.DataFrame) -> None:
    """
    Compare agent classification with manual C/S column if available
    """
    if 'Complexity' not in dataframe.columns:
        print("No manual classification column found for comparison")
        return

    # Get agent classification
    agent_simple, agent_complex = intelligent_row_extraction(dataframe)

    # Get manual classification
    manual_simple = dataframe[dataframe['Complexity'] == 'S']
    manual_complex = dataframe[dataframe['Complexity'] == 'C']

    # Compare results
    print(f"\nClassification Comparison:")
    print(f"Agent:  {len(agent_simple)} simple, {len(agent_complex)} complex")
    print(f"Manual: {len(manual_simple)} simple, {len(manual_complex)} complex")

    # Calculate agreement rate
    total_rows = len(dataframe)
    agent_classifications = ['SIMPLE'] * len(agent_simple) + ['COMPLEX'] * len(agent_complex)
    manual_classifications = dataframe['Complexity'].map({'S': 'SIMPLE', 'C': 'COMPLEX'}).tolist()

    agreements = sum(1 for a, m in zip(agent_classifications, manual_classifications) if a == m)
    agreement_rate = agreements / total_rows * 100

    print(f"Agreement rate: {agreement_rate:.1f}%")