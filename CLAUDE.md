# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Always think deeply and act as a critic for any ideas. Don't assume anything and ask questions if you are not clear.

## Project Overview

**GENIe (Content Transformer)** is a Streamlit-based application for XSLT transformation and optimization using Azure OpenAI models. The core functionality involves parsing large XSLT templates, applying rule-based optimizations, and using LLMs for complex pattern transformations.

## Key Development Commands

### Running Applications
```bash
# Main XSLT Manager application
streamlit run app/xslt_manager/xslt_manager.py
### Testing
```bash
# Core system tests
python test_intelligent_chunk_processor.py
python test_main_integration.py
python test_real_xslt_processing.py

# Rule-based processing tests
python test_rule_learning.py
python test_rules_first_approach.py

# XML processing tests
python test_xml_repair.py
python test_duplicate_closing_tags.py

# Unit tests for core modules
python genie_core/tests/test_llm_generates.py
python genie_core/tests/test_xml_utils.py
python genie_core/tests/test_xslt_utils.py

# Run specific LLM integration tests
python test_llm_calls.py
python test_llm_skip_logic.py
```

### Environment Setup
```bash
# Install dependencies (Python 3.12+ required)
pip install -r requirements.txt

# Alternative: Poetry installation
poetry install

# Setup Microsoft Visual C++ Build Tools (Windows)
# Required for some dependencies - install from Microsoft Visual Studio
```

## Architecture Overview

### Core Processing Pipeline (`genie_core/llm/`)

**Main XSLT Processing Flow:**
1. **Input**: Large XSLT templates (up to 384KB) from Mapforce
2. **Template Extraction**: Parse XSLT into individual templates using lxml
3. **Intelligent Processing**: 
   - Chunks < 1000 chars: Standard rule-based + LLM processing
   - Chunks ≥ 1000 chars: **Intelligent Chunk Processor** with pattern separation
4. **Output**: Optimized XSLT with reduced size and improved efficiency

**Key Components:**

- **`llm_utils.py`**: Main processing orchestration, Azure OpenAI integration, template chunking logic
- **`refine_cache.py`**: SQLite-based caching system, rule-based XSLT optimizations (6 rule types), fingerprint-based template matching
- **`intelligent_chunk_processor.py`**: Advanced pattern separation system that classifies XSLT constructs as simple (rule-optimized) vs complex (LLM-processed)

### Intelligent Pattern Processing System

The **IntelligentChunkProcessor** implements sophisticated XSLT pattern analysis:

**Pattern Types:**
- Simple: `SIMPLE_ATTRIBUTE`, `CONDITIONAL_ATTRIBUTE`, `SIMPLE_ELEMENT`, `VARIABLE_DECLARATION`
- Complex: `COMPLEX_CONDITIONAL`, `STRING_MANIPULATION`, `TEMPLATE_CALL`, `NESTED_LOGIC`

**Processing Flow:**
1. Parse XSLT into individual constructs
2. Classify each construct (simple vs complex)
3. Apply rule-based optimization to simple patterns
4. Send only complex patterns to LLM
5. Learn from LLM outputs to expand rule coverage

### Application Structure (`app/`)

**Multi-page Streamlit Applications:**
- **XSLT Manager**: Primary tool for XSLT generation and optimization
- **Gap Analyser**: XML comparison and analysis
- **Code Generator**: Pattern extraction and code generation
- **Agentic Gap Analyser**: AI-powered analysis workflows

### Data Layer

**Vector Database**: ChromaDB for document embeddings and retrieval
**SQL Cache**: SQLite database (`xslt_generator/database/refine_cache.db`) for optimization results
**Learning Database**: JSON storage for LLM-learned patterns

## Key Technical Details

### XSLT Processing Limits
- **Character Budget**: 5000 characters per LLM prompt
- **Intelligent Processing Threshold**: 1000 characters per chunk
- **Template Size Handling**: Large templates split using `_process_large_template()`

### Rule-Based Optimizations
1. **Variable Removal**: Eliminate `<xsl:variable name="var*_cur" select="." />` boilerplate
2. **Attribute Merging**: Convert simple for-each attribute loops to `xsl:copy-of`
3. **For-each Simplification**: Collapse trivial nested loops
4. **Direct Attribute Copy**: Convert direct attribute copying to `xsl:copy-of`
5. **Conditional Attribute Copy**: Optimize conditional attribute patterns
6. **Copy-of Merging**: Consolidate multiple copy-of statements
7. **Element Copying**: Simplify element duplication patterns
8. **Boolean Conversions**: Optimize type conversion patterns
9. **Template Call Optimization**: Inline simple utility template calls
10. **Complex Boolean Patterns**: Simplify nested boolean test patterns


### Testing Approach
- **Unit Tests**: Individual modules tested with direct Python execution (no pytest framework)
- **Integration Tests**: End-to-end validation with realistic XSLT content
- **Mock Functions**: LLM interactions stubbed for deterministic testing
- **Test Data**: Real-world XSLT samples in `genie_core/config/test_data/`

## Performance Metrics

The intelligent processing system achieves:
- **71.4% rule coverage ratio** (simple patterns handled by rules)
- **77% LLM call reduction** compared to pure LLM processing
- **15-25% size optimization** for processed templates

## Important File Locations

**Configuration**: `genie_core/config/` - prompts, test data, cookbooks
**Results**: `genie_core/config/results/` - generated outputs
**Reports**: Root directory - comprehensive implementation reports (*.md files)
**Learning Cache**: `genie_core/llm/learned_patterns.json`