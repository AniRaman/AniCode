# Java Alternatives for GENIe Python Libraries

This document provides Java alternatives for all libraries actually used in the `genie_core/llm/` processing pipeline.

## Analysis Based On
- **Source**: Only libraries used in `genie_core/llm/` folder
- **Scope**: Core LLM processing functionality  
- **Total Libraries**: ~25 essential libraries (down from 120+ in requirements)

---

## Core Python Libraries (Built-in) → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `os` | `System.getProperty()`, `System.getenv()` | **Complete** - Full equivalent for environment variables and system properties |
| `sys` | `System.getProperty("java.version")`, `Runtime` | **Complete** - System information and runtime access |
| `pathlib` | `java.nio.file.Path`, `java.nio.file.Paths` | **Complete** - Modern Java file API with same functionality |
| `collections.Counter` | `Map<T, Integer>` + custom counting logic | **Partial** - Need manual implementation for frequency counting |
| `dataclasses` | `record` (Java 14+) or regular classes | **Complete** - Records provide immutable data classes |
| `enum` | `enum` | **Complete** - Direct equivalent |
| `typing` | Generics, `@Nullable` annotations | **Complete** - Static typing with generics |
| `re` | `java.util.regex.Pattern` | **Complete** - Full regex support |
| `json` | `Jackson`, `Gson` | **Complete** - Multiple excellent JSON libraries |
| `textwrap` | Custom implementation needed | **No Alternative** - Must implement text wrapping manually |
| `hashlib` | `java.security.MessageDigest` | **Complete** - SHA, MD5, etc. supported |
| `sqlite3` | `SQLite JDBC driver` | **Complete** - Maven: `sqlite-jdbc` |
| `xml.etree.ElementTree` | `javax.xml.parsers.DocumentBuilder` | **Complete** - DOM parsing equivalent |

---

## Web Framework & UI → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `streamlit` | **Spring Boot + Angular frontend** | **Architectural Change** - Complete rewrite required, different paradigm |

---

## Data Processing → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `pandas` | **Apache Spark DataFrame/Dataset API** | **Partial** - Limited usage in your code, Spark handles large-scale data |
| `numpy` | **Apache Commons Math** | **Partial** - Basic array operations, limited compared to NumPy |

---

## XML/XSLT Processing → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `lxml.etree` | **JAXP (javax.xml) + Saxon-HE** | **Complete** - Saxon-HE provides advanced XML/XSLT processing |
| `saxonche` | **Saxon-HE Java version** | **Complete** - Same processor, native Java implementation |

---

## AI/ML & LLM Integration → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `openai.AzureOpenAI` | **OpenAI Java SDK** (community) | **Partial** - Community SDK, not official but functional |
| `azure-core` | **Azure SDK for Java** | **Complete** - Official Microsoft Azure Java SDK |
| `azure-identity` | **Azure Identity for Java** | **Complete** - Official Azure authentication for Java |
| `chromadb` | **Azure AI Search** or **Elasticsearch** | **Complete** - Better enterprise alternatives available |

---

## LlamaIndex Ecosystem → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `llama-index-core` | **LangChain4j** | **Partial** - Similar functionality, different API |
| `llama-index-llms-azure-openai` | **LangChain4j + Azure OpenAI** | **Partial** - Requires integration work |
| `llama-index-embeddings-azure-openai` | **Azure AI Search embeddings** | **Complete** - Direct Azure integration |
| `llama-index-vector-stores-chroma` | **Azure AI Search** or **Elasticsearch** | **Complete** - Better enterprise solutions |

---

## Database & Storage → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `sqlite3` | **H2 Database + JDBC** | **Complete** - H2 or SQLite JDBC driver |

---

## HTTP & Networking → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `httpx` | **OkHttp** or **Apache HttpClient** | **Complete** - Multiple excellent HTTP clients |

---

## Configuration & Environment → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `python-dotenv` | **dotenv-java/Spring @ConfigurationProperties** | **Complete** - Spring handles environment configuration |

---

## Text Processing (Via Dependencies) → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `html2text` | **Jsoup + custom logic** | **Partial** - Jsoup handles HTML parsing, need custom text conversion |
| `beautifulsoup4` | **Jsoup** | **Complete** - Excellent HTML/XML parsing library |

---

## Third-party APIs → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `atlassian-python-api` | **Confluence REST API directly** | **Complete** - Use HTTP client to call REST endpoints |

---

## Utility Libraries → Java Alternatives

| Python Library | Java Alternative | Notes |
|---|---|---|
| `zss` (Zhang-Shasha tree diff) | **Custom implementation required** | **No Alternative** - Must implement tree edit distance algorithm |

---

## Conversion Summary

### **✅ Complete Alternatives (19/25 libraries)**
- Core Python libraries (10/13)
- XML/XSLT processing (2/2)  
- Azure services (3/3)
- HTTP/Database/Config (3/3)
- HTML processing (1/1)

### **⚠️ Partial Alternatives (4/25 libraries)**
- `pandas` → Apache Spark (limited usage)
- `numpy` → Apache Commons Math (basic operations only)
- `html2text` → Jsoup + custom logic
- LlamaIndex ecosystem → LangChain4j (different API)

### **❌ No Direct Alternatives (2/25 libraries)**
- `textwrap` → Custom implementation needed
- `zss` tree diff → Custom Zhang-Shasha algorithm implementation

### **🔄 Architectural Changes Required**
- `streamlit` → Complete UI rewrite with Spring Boot + Angular frontend
- `chromadb` + `llama-index` → Azure AI Search (recommended upgrade)

---

## Conversion Feasibility: **92% (23/25) Convertible**

**Estimated Conversion Effort**: 12-15 weeks
- **Core engine conversion**: 8-10 weeks
- **UI architectural redesign**: 4-5 weeks  
- **Custom implementations** (textwrap, zss): 1-2 weeks

**Recommendation**: **Highly feasible** - Most functionality has excellent Java alternatives, with significant improvements possible through Azure AI Search and modern Spring Boot architecture.

---

*Generated on: January 2025*  
*Project: GENIe (Content Transformer)*  
*Analysis: genie_core/llm processing only*  
*Conversion Feasibility: 92%*