import streamlit as st
import re

try:
    from llama_index.llms.azure_openai import AzureOpenAI as LlamaAzureOpenAI
    from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from dotenv import load_dotenv, find_dotenv
    import os
    import os.path
    import sys
    import httpx
    from llama_index.core import Settings
    import chromadb
    from llama_index.core import StorageContext
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
except ModuleNotFoundError as e:
    pattern = r"\'(.*)\'"
    module_name = re.search(pattern, str(e)).group(1)
    st.error(f"ModuleNotFoundError: please install the required module by running `pip install {module_name}`\n ({e})")

class DatabaseConfigurator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConfigurator, cls).__new__(cls)
        return cls._instance

    llama_index = None

    def __init__(self, directory):
        model = "GPT4O"
        _ = load_dotenv(find_dotenv())
        self.api_key = os.getenv(f"{model}_AZURE_OPENAI_KEY")
        self.azure_endpoint = os.getenv(f"{model}_AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv(f"{model}_AZURE_API_VERSION")
        self.deployment_model_name = os.getenv(f"{model}_MODEL_DEPLOYMENT_NAME")
        self.llm = self.init_llm()
        self.embed_model = self.init_embedding()
        self.settings()
        self.llm_index = self.configure_database(directory)

    @property
    def llm_index(self):
        return self._llm_index

    @llm_index.setter
    def llm_index(self, value):
        self._llm_index = value

    def init_llm(self):
        return LlamaAzureOpenAI(
            engine="gpt-4o",
            model="gpt-4o",
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version,
            http_client=httpx.Client(verify=False)
        )

    def settings(self):
        Settings.llm = self.init_llm()
        Settings.embed_model = self.init_embedding()

    @st.cache_resource
    def init_embedding(_self):
        api_key = os.getenv(f"ADA_EMBEDDING_AZURE_OPENAI_KEY")
        azure_endpoint = os.getenv(f"ADA_EMBEDDING_AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv(f"ADA_EMBEDDING_AZURE_API_VERSION")
        deployment_model_name = os.getenv(f"ADA_EMBEDDING_MODEL_DEPLOYMENT_NAME")
        return AzureOpenAIEmbedding(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            deployment_model_name=deployment_model_name
            )

    def configure_database(self, directory):
        chroma_client = chromadb.EphemeralClient()
        chroma_collection = chroma_client.get_or_create_collection("llama_chroma")
        if not os.path.exists(directory):
            raise ValueError(f"Directory {directory} does not exist.")
        documents = SimpleDirectoryReader(directory).load_data()
        vector_store = ChromaVectorStore(chroma_collection = chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store = vector_store)
        index = VectorStoreIndex.from_documents(documents, 
                                                storage_context= storage_context, 
                                                embed_model = Settings.embed_model)
        return index

    def get_answer_from_db(self, query):
        query_engine = self.llm_index.as_query_engine()
        answer = query_engine.query(query)
        return str(answer)

# configurator = DatabaseConfigurator("/Users/nlepakshi/Library/CloudStorage/OneDrive-AmadeusWorkplace/genai/master/content-transformer/1_6_1_openai/learning/xslt_generator/config/prompts/Navitaire/Specs")
# answer = configurator.get_answer_from_db("what is the mapping for AMA_ConnectivityLayerRS/Requests/Request/set/product/ID")
# print("Answer is \n")
# print(answer)
# answer = configurator.get_answer_from_db("For the ContactInfoList, should the email and label elements be included for all actors, or only for those with PTC=ADT?")
# print("Answer is \n")
# print(answer)
