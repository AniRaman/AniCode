# Agentic XSLT Processor Implementation Guide

## Overview

The XSLT generation system has been successfully converted from a conversation-based state machine to an intelligent agentic approach using Azure GPT function calling. This maintains identical functionality while providing much more flexible user interaction.

## Architecture

### Key Components

1. **`agentic_xslt_processor.py`** - Main agentic implementation
   - Function definitions for GPT
   - Context management system  
   - Function execution logic
   - System prompt generation

2. **`llm_utils.py`** - Backward compatibility wrapper
   - Original function renamed to `process_user_response_original`
   - New wrapper function `process_user_response` that switches approaches
   - Environment-based configuration

3. **UI Integration** - No changes required
   - Same function signature maintained
   - Same return values and behavior
   - Transparent switching between approaches

## Usage

### Environment Configuration

Set the environment variable to control which approach to use:

```bash
# Use agentic approach (default)
export USE_AGENTIC_XSLT=true

# Use original conversation-based approach  
export USE_AGENTIC_XSLT=false
```

### User Experience Changes

**Before (Rigid Conversation Flow):**
1. User: "START"
2. Bot: "Please provide the URL of the specs"
3. User: "https://example.com/specs"
4. Bot: "XSLT generated. Do you want to refine?"
5. User: "YES"
6. Bot: "Please provide the fields to be refined?"
7. User: "TaxAmount"
8. Bot: "What needs to be refined here?"
9. User: "Add currency symbol"

**After (Flexible Agentic):**
1. User: "Generate XSLT from https://example.com/specs"
2. Bot: "XSLT generated. Do you want to refine?"
3. User: "Fix TaxAmount to include currency symbol" 
4. Bot: "XSLT refined. Any corrections?"

## Error Handling Strategy

### 1. Function Call Failures

```python
# Automatic fallback implemented in wrapper
try:
    return process_user_request_agentic(...)
except Exception as e:
    print(f"Error in agentic approach, falling back to original: {e}")
    return process_user_response_original(...)
```

### 2. GPT API Errors

- **Connection Failures**: Retry with exponential backoff
- **Rate Limiting**: Automatic retry after delay
- **Invalid Function Calls**: Graceful error messages to user
- **Malformed Responses**: Fallback to original approach

### 3. Context Management Errors

- **Session State Issues**: Automatic context reconstruction
- **Missing Prerequisites**: Clear error messages requesting missing items
- **Data Processing Errors**: Preserve original error handling logic

### 4. Processing Chain Errors

Each function in the processing chain has error handling:

```python
def process_specs_and_generate_xslt(specs_url: str) -> Tuple[bool, str, Optional[str]]:
    try:
        # Processing logic
        return True, "Success message", xslt_result
    except Exception as e:
        print(f"Error in process_specs_and_generate_xslt: {e}")
        return False, f"Error processing specifications: {str(e)}", None
```

## Rollback Strategy

### Immediate Rollback (Zero Downtime)

1. **Environment Variable Method**:
   ```bash
   export USE_AGENTIC_XSLT=false
   ```
   System immediately switches to original approach.

2. **No Code Changes Required**: 
   - UI continues working unchanged
   - All existing functionality preserved
   - Same performance characteristics

### Permanent Rollback (If Needed)

1. **Remove Agentic Files**:
   ```bash
   rm genie_core/llm/agentic_xslt_processor.py
   rm test_agentic_xslt.py
   ```

2. **Restore Original Function**:
   ```python
   # In llm_utils.py, replace wrapper with:
   process_user_response = process_user_response_original
   ```

3. **Clean Up**: Remove environment variable references

### Monitoring and Alerts

**Key Metrics to Monitor**:
- Function call success rate
- Response time comparison 
- Error frequency
- User satisfaction (same outputs)
- XSLT generation accuracy

**Alert Conditions**:
- Agentic error rate > 5%
- Response time increase > 200%
- Function calling failures > 3 consecutive

## Testing

### Automated Test Suite

Run comprehensive tests:
```bash
python test_agentic_xslt.py
```

**Test Coverage**:
- All original conversation paths
- New flexible input patterns
- Error conditions and recovery
- Environment switching
- Context management
- Function call scenarios

### Manual Testing Checklist

- [ ] Fresh XSLT generation from URL
- [ ] Field refinement workflows  
- [ ] Error handling (invalid URLs, missing XMLs)
- [ ] Complex specification processing
- [ ] Multi-step refinement conversations
- [ ] Environment variable switching
- [ ] Fallback to original approach

## Benefits Achieved

1. **User Experience**: Natural language interaction vs. rigid conversation flow
2. **Maintainability**: Clean function-based architecture vs. nested if-else chains  
3. **Extensibility**: Easy to add new capabilities as functions
4. **Reliability**: Automatic fallback ensures zero downtime
5. **Flexibility**: Can handle multiple intents in single request

## Function Definitions

The system provides these functions to GPT:

### `validate_prerequisites()`
- Checks if input XML, output XML are uploaded
- Returns missing items list for user guidance

### `process_specs_and_generate_xslt(specs_url)`
- Processes specifications URL
- Converts HTML to DataFrame  
- Generates XSLT using existing batch logic (complex-first, then simple)
- Preserves exact same processing logic

### `refine_existing_xslt(field_names, refinement_instructions)`
- Refines specific fields in existing XSLT
- Uses RAG to find field context
- Applies refinements using existing logic
- Updates specifications automatically

### `request_missing_prerequisites(missing_items)`
- Generates appropriate error messages
- Maintains exact same error text as original

## Performance Considerations

- **Token Usage**: Function calling uses slightly more tokens but provides better results
- **Response Time**: Similar to original approach (single LLM call vs. conversation turns)  
- **Reliability**: Higher due to automatic fallback mechanism
- **Scalability**: Better architecture for adding new capabilities

## Future Enhancements (Phase 2)

1. **Multi-turn Complex Operations**: Chain multiple function calls automatically
2. **Learning from Interactions**: Improve function calling over time  
3. **Proactive Suggestions**: Suggest optimizations and improvements
4. **Batch Processing**: Handle multiple URLs or refinements in single request
5. **Advanced Error Recovery**: More sophisticated error handling strategies

## Conclusion

The agentic implementation successfully modernizes the XSLT generation system while maintaining 100% backward compatibility. The intelligent function calling provides a much better user experience with the same reliable processing logic underneath.