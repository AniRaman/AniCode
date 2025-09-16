# Libraries Used in GENIe Project

This document provides a comprehensive list of all libraries and dependencies used in the GENIe (Content Transformer) project.

## Project Overview
GENIe is a Streamlit-based application for XSLT transformation and optimization using Azure OpenAI models. The project uses a diverse ecosystem of libraries covering web frameworks, AI/ML processing, data manipulation, XML processing, and more.

## Summary Statistics
- **Total Python files**: 92 files
- **Total lines of code**: ~17,585 lines
- **Total distinct libraries**: ~120+ libraries
- **Core dependency categories**: 12 major categories

---

## Core Python Libraries (Built-in)

### System & OS Operations (Actually Used)
- `os` - Operating system interface
- `sys` - System-specific parameters and functions
- `pathlib` - Object-oriented filesystem paths

### Data Structures & Utilities (Actually Used)
- `collections.Counter` - Frequency counting
- `dataclasses` - Data classes
- `enum` - Enumerations
- `typing` - Type hints (List, Dict, Any, Optional, Tuple)

### Text & Pattern Processing (Actually Used)
- `re` - Regular expressions
- `json` - JSON encoder and decoder
- `textwrap` - Text wrapping and filling

### Security & Cryptography (Actually Used)
- `hashlib` - Secure hash and message digest algorithms

### Database (Actually Used)
- `sqlite3` - SQLite database interface

### XML Processing (Actually Used)
- `xml.etree.ElementTree` - XML processing

---

## Web Framework & UI

### Main Web Framework
- `streamlit` (v1.41.1) - Web app framework for data science and ML applications
  - **Usage**: Primary UI framework for all web interfaces
  - **Components**: Multi-page applications, file uploads, real-time processing status

## Data Processing & Analysis

### Core Data Libraries (Used in genie_core/llm)
- `pandas` (v2.2.3) - Data manipulation and analysis
  - **Usage**: DataFrame operations, CSV processing, data cleaning
- `numpy` (v2.2.1) - Numerical computing
  - **Usage**: Array operations, mathematical computations

## XML/XSLT Processing

### Primary XML Libraries
- `lxml` (v5.3.0) - XML and HTML processing
  - **Usage**: Core XSLT template parsing, XML validation, XPath queries
- `saxonche` (v12.5.0) - Saxon XSLT and XQuery processor
  - **Usage**: XSLT transformation execution, advanced XSLT features

### Additional XML Tools
- `beautifulsoup4` (v4.12.3) - HTML/XML parsing
  - **Usage**: HTML content parsing, web scraping
- `defusedxml` (v0.7.1) - XML bomb protection
  - **Usage**: Secure XML parsing

---

## AI/ML & LLM Integration

### OpenAI Integration
- `openai` (v1.59.7) - OpenAI API client
  - **Usage**: GPT-4, O1, O3-mini model interactions
- `tiktoken` (v0.8.0) - OpenAI tokenizer
  - **Usage**: Token counting, text splitting

### Azure Integration
- `azure-core` (v1.32.0) - Azure SDK core functionality
- `azure-identity` (v1.19.0) - Azure authentication
  - **Usage**: Azure OpenAI authentication, service integration

### Vector Database
- `chromadb` (v0.6.3) - Vector database
  - **Usage**: Document embeddings storage, semantic search
- `chroma-hnswlib` (v0.7.6) - HNSW algorithm for ChromaDB

## LlamaIndex Ecosystem

### Core LlamaIndex
- `llama-index` (v0.12.0) - Main LlamaIndex framework
- `llama-index-core` (v0.12.11) - Core LlamaIndex functionality
- `llama-cloud` (v0.1.9) - LlamaCloud integration
- `llama-parse` (v0.5.19) - Document parsing

### Embeddings
- `llama-index-embeddings-azure-openai` (v0.3.0) - Azure OpenAI embeddings
- `llama-index-embeddings-openai` (v0.3.1) - OpenAI embeddings
- `llama-index-embeddings-huggingface` (v0.5.0) - Hugging Face embeddings

### LLMs
- `llama-index-llms-azure-openai` (v0.3.0) - Azure OpenAI LLMs
- `llama-index-llms-openai` (v0.3.13) - OpenAI LLMs
- `llama-index-multi-modal-llms-openai` (v0.3.0) - Multi-modal LLMs

### Vector Stores
- `llama-index-vector-stores-chroma` (v0.4.1) - ChromaDB integration
- `llama-index-vector-stores-postgres` (v0.4.1) - PostgreSQL integration

### Specialized Components
- `llama-index-agent-openai` (v0.4.2) - OpenAI agents
- `llama-index-program-openai` (v0.3.1) - OpenAI programs
- `llama-index-question-gen-openai` (v0.3.0) - Question generation
- `llama-index-readers-file` (v0.4.3) - File readers
- `llama-index-readers-llama-parse` (v0.4.0) - LlamaParse integration
- `llama-index-indices-managed-llama-cloud` (v0.6.3) - Managed cloud indices
- `llama-index-cli` (v0.4.0) - Command line interface
- `llama-index-legacy` (v0.9.48.post4) - Legacy compatibility

---

## Database & Storage

### SQL Databases
- `sqlite3` (built-in) - SQLite database
  - **Usage**: Refine cache, optimization results storage
- `asyncpg` (v0.30.0) - PostgreSQL async driver
- `psycopg2-binary` (v2.9.10) - PostgreSQL adapter
- `pgvector` (v0.3.6) - PostgreSQL vector extension
- `SQLAlchemy` (v2.0.37) - SQL toolkit and ORM

### Vector Databases
- `chromadb` (v0.6.3) - Vector database for embeddings

### Utilities
- `PyPika` (v0.48.9) - SQL query builder

---

## HTTP & Networking (Actually Used)
- `httpx` (v0.28.1) - Async HTTP client
  - **Usage**: Azure OpenAI API calls, external service integration

## Configuration & Environment (Actually Used)
- `python-dotenv` (v1.0.1) - Load environment variables from .env files
  - **Usage**: API keys, configuration management

## Text Processing (Via Dependencies)
- `html2text` (v2024.2.26) - Convert HTML to plain text (via common.utils)
- `beautifulsoup4` - HTML parsing (via common.utils)

## Third-party APIs (Via Dependencies)
- `atlassian-python-api` (v3.41.18) - Confluence API (via common.confluence_utils)

---

## Utility & Helper Libraries

### Tree Processing
- `zss` - Tree edit distance (Zhang-Shasha algorithm)
  - **Usage**: XML tree comparison, XSLT optimization analysis

## Key Library Categories Summary (Based on genie_core/llm Usage)

### **✅ Actually Used in Core LLM Processing:**
1. **Web Framework**: Streamlit only
2. **AI/ML**: OpenAI Azure, ChromaDB, LlamaIndex ecosystem  
3. **Data Processing**: Pandas, NumPy only
4. **XML/XSLT**: lxml, xml.etree.ElementTree
5. **Database**: SQLite only
6. **HTTP**: httpx only
7. **Configuration**: python-dotenv only
8. **Text Processing**: html2text, BeautifulSoup (via dependencies)
9. **Utilities**: zss (tree diff), textwrap, collections.Counter

## Core Libraries Actually Used in `genie_core/llm/` Processing

**Analysis shows the following libraries are actually used in the core LLM processing pipeline:**

### **Essential Libraries (Core Functionality)**
- `streamlit` - Web framework for UI
- `openai.AzureOpenAI` - Azure OpenAI API client
- `chromadb` - Vector database for embeddings
- `lxml.etree` - XML/XSLT processing
- `pandas` - Data manipulation 
- `numpy` - Numerical computing
- `httpx` - HTTP client for API calls
- `python-dotenv` - Environment configuration
- `zss` - Tree edit distance algorithm
- `sqlite3` - Caching database
- `html2text` - Text conversion
- `beautifulsoup4` - HTML parsing
- `atlassian-python-api` - Confluence integration

## Notes for Java Conversion

**Revised conversion requirements based on actual usage:**

**Essential Conversions:**
- **Streamlit** → Spring Boot + React/Vue frontend
- **ChromaDB**/ **LlamaIndex** → Azure AI Search (recommended) or Elasticsearch
- **lxml** → JAXP + Saxon-HE
- **OpenAI Python SDK** → OpenAI Java SDK (community)
- **Pandas** → Apache Spark DataFrame/Dataset API (limited usage)
- **zss** → Custom tree diff implementation