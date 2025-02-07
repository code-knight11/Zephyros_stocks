from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os
import pinecone
from langchain_community.vectorstores.pinecone import Pinecone
from settings import PINECONE_API_KEY

embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

pinecone.Pinecone(api_key=PINECONE_API_KEY)
vector_store = Pinecone.from_existing_index("stockrag", embeddings)

@tool
def semantic_search(query: str, k: int = 3) -> str:
    """
    Perform semantic search on indexed documents.
    Args:
        query: Search query
        k: Number of results to return
    """
    try:
        results = vector_store.similarity_search(query, k=k)
        formatted_results = []
        for doc in results:
            formatted_results.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'similarity': doc.metadata.get('score', 'N/A')
            })
        return str(formatted_results)
    except Exception as e:
        return f"Error performing search: {str(e)}"
