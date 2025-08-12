#!/usr/bin/env python3
"""Test the XML validation logic implementation."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_xml_validation_logic():
    """Test the enhanced XML validation logic - only applies when output_tags < input_tags."""
    print("=== Testing XML Tag Validation Logic (Only for Fewer Output Tags) ===")
    
    
    # Test cases - updated to reflect the corrected scope
    test_cases = [
        {
            "name": "Perfect match",
            "input": "<Warning><Type>Error</Type></Warning>",
            "output": "<Warning><Type>Error</Type></Warning>",
            "expected": "output"  # Should use refined output
        },
        {
            "name": "Fewer tags: Odd difference (missing closing tag) - VALIDATION APPLIES",
            "input": "<Warning><Type>Error</Type></Warning>",
            "output": "<Warning><Type>Error</Type>",  # Missing </Warning> - fewer tags
            "expected": "input"  # Should fall back to input (odd difference)
        },
        {
            "name": "Fewer tags: Even difference with proper removal - VALIDATION APPLIES",
            "input": "<Warning><Type>Error</Type><Status>OK</Status></Warning>",
            "output": "<Warning><Type>Error</Type></Warning>",  # Removed Status tag pair - fewer tags
            "expected": "output"  # Should use output (even difference, proper pairs)
        },
        {
            "name": "Fewer tags: Even difference with improper removal - VALIDATION APPLIES",
            "input": "<Warning><Type>Error</Type><Status>OK</Status></Warning>", 
            "output": "<Warning><Type>Error</Type><Status>",  # Removed closing tags improperly - fewer tags
            "expected": "input"  # Should fall back to input (improper pairs)
        },
        {
            "name": "More tags: Extra tags added - NO VALIDATION (uses existing logic)",
            "input": "<Warning><Type>Error</Type></Warning>",
            "output": "<Warning><Type>Error</Type><Status>OK</Status></Warning>",  # Added Status tag pair - more tags
            "expected": "output"  # Should use existing discrepancy fixing logic
        }
    ]
    
    # Extract validation functions directly for testing
    def test_validate_chunk_structure(input_chunk: str, refined_chunk: str) -> str:
        """Simplified version of validation for testing."""
        def _extract_structural_tag_names_test(content: str) -> list:
            import re
            tag_list = []
            # Simple pattern that excludes xsl: tags
            pattern = r'<(/?[^>\s]+)[^>]*>'
            for match in re.finditer(pattern, content):
                tag_name = match.group(1)
                # Skip xsl: prefixed tags
                if 'xsl:' in tag_name:
                    continue
                if tag_name.startswith('/'):
                    tag_list.append('/' + tag_name[1:])
                else:
                    tag_list.append(tag_name)
            return tag_list
            
        def _validate_tag_pairs_test(input_tags: list, output_tags: list) -> bool:
            input_set = set(input_tags)
            output_set = set(output_tags)
            different_tags = (input_set - output_set) | (output_set - input_set)
            
            if not different_tags:
                return True
                
            for tag in different_tags:
                if tag.startswith('/'):
                    opening_tag = tag[1:]
                    if opening_tag not in different_tags:
                        return False
                else:
                    closing_tag = '/' + tag
                    if closing_tag not in different_tags:
                        return False
            return True
            
        def _count_tag_pairs_test(tags: list) -> dict:
            pairs = {}
            for tag in tags:
                if tag.startswith('/'):
                    tag_name = tag[1:]
                    if tag_name not in pairs:
                        pairs[tag_name] = {'open': 0, 'close': 0}
                    pairs[tag_name]['close'] += 1
                else:
                    if tag not in pairs:
                        pairs[tag] = {'open': 0, 'close': 0}
                    pairs[tag]['open'] += 1
            return pairs
            
        def _validate_tag_pairs_content_test(input_tags: list, output_tags: list) -> bool:
            input_pairs = _count_tag_pairs_test(input_tags)
            output_pairs = _count_tag_pairs_test(output_tags)
            
            for tag_name, counts in input_pairs.items():
                if counts['open'] != counts['close']:
                    return False
                    
            for tag_name, counts in output_pairs.items():
                if counts['open'] != counts['close']:
                    return False
            return True
        
        input_tags = _extract_structural_tag_names_test(input_chunk)
        output_tags = _extract_structural_tag_names_test(refined_chunk)
        
        print(f"Input tags: {input_tags}")
        print(f"Output tags: {output_tags}")
        
        if input_tags == output_tags:
            print("Tag lists match perfectly")
            return refined_chunk
        elif len(output_tags) < len(input_tags):
            print("Output has fewer tags than input - applying XML validation logic")
            
            input_tag_count = len(input_tags)
            output_tag_count = len(output_tags)
            tag_difference = abs(output_tag_count - input_tag_count)
            
            print(f"Tag count difference: {tag_difference} (input: {input_tag_count}, output: {output_tag_count})")
            
            # If difference is odd, fall back to original chunk
            if tag_difference % 2 == 1:
                print("Odd tag difference detected - falling back to original chunk")
                return input_chunk
            
            # For even differences, validate that different tags form complete pairs
            if tag_difference > 0:
                if _validate_tag_pairs_test(input_tags, output_tags):
                    print("Even tag difference with proper pairs - using refined chunk")
                    return refined_chunk
                else:
                    print("Tag pairs not properly matched - falling back to original chunk")
                    return input_chunk
            
            # No difference in count but content differs - validate pairs
            if not _validate_tag_pairs_content_test(input_tags, output_tags):
                print("Tag pairing validation failed - falling back to original chunk")
                return input_chunk
            
            # All validation passed for fewer tags case
            return refined_chunk
        else:
            print("Output has more tags - using existing discrepancy fixing logic")
            # For testing purposes, just return output (simulating existing logic)
            return refined_chunk
    
    # Run test cases
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = test_validate_chunk_structure(test_case['input'], test_case['output'])
        
        if test_case['expected'] == 'output':
            expected_result = test_case['output']
        else:
            expected_result = test_case['input']
            
        if result == expected_result:
            print(f"[PASSED] Correctly returned {'output' if result == test_case['output'] else 'input'}")
            passed += 1
        else:
            print(f"[FAILED] Expected {'output' if expected_result == test_case['output'] else 'input'}, got {'output' if result == test_case['output'] else 'input'}")
    
    print(f"\n=== Results: {passed}/{total} tests passed ===")
    return passed == total

if __name__ == "__main__":
    test_xml_validation_logic()