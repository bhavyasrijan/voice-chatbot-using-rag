# query_engine_setup.py

import os
from llama_index.llms.vertex import Vertex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from llama_index.core import get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine


# Set environment variables
os.environ['GOOGLE_API_KEY'] = 'AIzaSyC-ASsI6zwI9UiDcR9xqEH7SyeHl2MS8HY'

# Set embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Set LLM model
from llama_index.llms.gemini import Gemini
Settings.llm = Gemini(model_name="models/gemini-1.0-pro-001")

from llama_index.core import StorageContext, load_index_from_storage

# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="E:/Rag-app-testing/llamaenv/indexing")

# load index
index = load_index_from_storage(storage_context)

# Configure retriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=10,
)

# Configure response synthesizer
response_synthesizer = get_response_synthesizer()

# Assemble query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
)

def get_query_engine():
    return query_engine
