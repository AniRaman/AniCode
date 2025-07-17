from llama_index.llms.azure_openai import AzureOpenAI as LlamaAzureOpenAI
from dotenv import load_dotenv, find_dotenv
import os
import httpx
import chromadb
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import PrevNextNodePostprocessor
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

httpx_client = httpx.Client(verify=False)

def db_setup():
    chroma_client = chromadb.Client()
    chroma_client = chromadb.PersistentClient(path="./chromaDB")
    chroma_client.reset()
    return chroma_client

def embed_setup():
    _ = load_dotenv(find_dotenv())
    ada_model_name = os.getenv("ADA_EMBD_MODEL_DEPLOYMENT_NAME")
    azure_endpoint = os.getenv("ADA_EMBD_AZURE_OPENAI_ENDPOINT") 
    api_key=os.getenv("ADA_EMBD_AZURE_OPENAI_KEY")
    api_version=os.getenv("ADA_EMBD_AZURE_API_VERSION")
    
    embed_model = AzureOpenAIEmbedding(
        model="text-embedding-ada-002",
        deployment_name=ada_model_name,
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        http_client=httpx_client
    )
    return embed_model

def db_llm_setup():
    _ = load_dotenv(find_dotenv())
    api_key = os.getenv("GPT4O_AZURE_OPENAI_KEY")
    azure_endpoint = os.getenv("GPT4O_AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("GPT4O_AZURE_API_VERSION")
    deployment_model_name = os.getenv("GPT4O_MODEL_DEPLOYMENT_NAME")

    llm_4t = LlamaAzureOpenAI(
        model="gpt-4o",
        deployment_name=deployment_model_name,
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        http_client=httpx_client
    )
    return llm_4t

def query_eng_setup(documents):
    embedModel = embed_setup()
    Settings.llm = db_llm_setup()
    Settings.embed_model = embedModel
    chroma_collection_4t = db_setup().create_collection("my_collection_4t")

    # set up ChromaVectorStore and load in data
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection_4t)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=embedModel
    )

    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=15,
    )

    # configure response synthesizer
    response_synthesizer = get_response_synthesizer()

    # Assuming 'index' is your document index
    postprocessor = PrevNextNodePostprocessor(
        docstore=index.docstore,  # Your document store
        num_nodes=5,              # Number of nodes to fetch
        mode="both"               # Mode can be 'previous', 'next', or 'both'
    )

    # assemble query engine
    query_engine_llm = RetrieverQueryEngine.from_args(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        response_mode="no_text",
        node_postprocessors=[postprocessor]
        #node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.1)],
    )
    return query_engine_llm

def get_answer_llm(query_engine_llm,question):
    return query_engine_llm.query(question)


# response = query_engine_llm.query(f"Billing address")

# print(response)