import re
try:
    from llama_index.llms.azure_openai import AzureOpenAI as LlamaAzureOpenAI
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    #  pip install llama_index-embeddings-azure_openai
    from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
    from llama_index.core import Document, VectorStoreIndex, ServiceContext, StorageContext
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from dotenv import load_dotenv, find_dotenv
    import os
    import os.path
    import sys
    import streamlit as st
    import httpx
    from llama_index.core import Settings
    import chromadb
    from llama_index.core import StorageContext
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
    import xml.etree.ElementTree as ET
except ModuleNotFoundError as e:
    pattern = r"\'(.*)\'"
    module_name = re.search(pattern, str(e)).group(1)
    st.error(f"ModuleNotFoundError: please install the required module by running `pip install {module_name}`\n ({e})")

def init_llm():
        _ = load_dotenv(find_dotenv())
        return LlamaAzureOpenAI(
            engine="gpt-4o",
            model="gpt-4o",
            api_key=os.getenv("GPT4O_AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("GPT4O_AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("GPT4O_AZURE_API_VERSION"),
            http_client=httpx.Client(verify=False)
        )
def init_embedding():
        _ = load_dotenv(find_dotenv())
        api_key = os.getenv(f"ADA_EMBEDDING_AZURE_OPENAI_KEY")
        azure_endpoint = os.getenv(f"ADA_EMBEDDING_AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv(f"ADA_EMBEDDING_AZURE_API_VERSION")
        deployment_model_name = os.getenv(f"ADA_EMBEDDING_MODEL_DEPLOYMENT_NAME")
        embeddings = AzureOpenAIEmbedding(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            deployment_model_name=deployment_model_name,
            http_client=httpx.Client(verify=False)
            )
        return embeddings

def init_llama_dex_with_chroma():
    chroma_client = chromadb.EphemeralClient()
    chroma_collection = chroma_client.get_or_create_collection("xml_mappings")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embedding_model = init_embedding()
    Settings.embed_model=embedding_model
    Settings.llm = init_llm()
    # service_context = ServiceContext.from_defaults(embed_model=embedding_model)
    return storage_context

def parse_xml(file_path, xml_type):
    """
    Parses an XML file and extracts meaningful chunks.
    Adds metadata to identify input, output, and specification XMLs.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    documents = []
    
    # Iterate through elements to extract relevant data
    for elem in root.iter():
        text = elem.text.strip() if elem.text else ""
        tag = elem.tag
        if text:
            doc = Document(
                text=f"{tag}: {text}",
                metadata={"type": xml_type, "tag": tag}
            )
            documents.append(doc)
    
    return documents

def load_and_store_documents(input_xml_path, output_xml_path, spec_path):
    # Parse XML files
    input_docs = parse_xml(input_xml_path, "input_xml")
    output_docs = parse_xml(output_xml_path, "output_xml")

    # Load Specification (Assuming it's a text file or JSON)
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_text = f.read()
    
    spec_doc = Document(
        text=spec_text,
        metadata={"type": "specifications"}
    )

    # Combine all docs
    all_docs = input_docs + output_docs + [spec_doc]

    storage_context = init_llama_dex_with_chroma()
    # Create Index and Store
    index = VectorStoreIndex.from_documents(
        all_docs, 
        storage_context=storage_context, 
        service_context=Settings.embed_model
    )

    print("Documents added to ChromaDB successfully.")
    return index

def query_mappings(index, query_text):
    """
    Queries ChromaDB for relevant XML and specification mappings.
    """

    # Create a query engine
    query_engine = index.as_query_engine()

    # Query for relevant information
    response = query_engine.query(query_text)

    return response

if __name__ == "__main__":
    index = load_and_store_documents("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/xml_comparator/ovrs2.xml", "/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/xml_comparator/output2.xml", "/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/xml_comparator/specs.md")
    print(query_mappings(index, "Verify the input and output XML as per specifications. Explain each differences in tabular format."))