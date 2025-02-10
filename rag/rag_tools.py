from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os
import pinecone
from langchain_community.vectorstores.pinecone import Pinecone
from settings import PINECONE_API_KEY
from typing import List, Dict
import json

embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

pinecone.Pinecone(api_key=PINECONE_API_KEY)
vector_store = Pinecone.from_existing_index("stockrag", embeddings)

@tool
def emantic_search(query: str, k: int = 3) -> str:
    """
    Perform semantic search on indexed documents.
    Args:
        query: Search query
        k: Number of results to return
    """
    try:
        retriever = vector_store.as_retriever(search_kwargs={"k":1})
        results=retriever.get_relevant_documents(query=query)
        
        formatted_results = []
        for doc in results:
            formatted_results.append({
                'content': doc.page_content,
                'metadata': doc.metadata
            })
        return json.dumps(formatted_results)
    except Exception as e:
        return f"Error performing search: {str(e)}"


def get_relevant_docs(self, question: str, k: int = 3) -> List:
        """Get relevant documents from vector store"""
        results = self.vector_store.similarity_search(
            query=question,
            k=k
        )
        return results

def generate_response(self, question: str, context_docs: List) -> str:
        """Generate a response using the LLM chain"""
        # Combine context from all relevant documents
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        # Generate response
        response = self.llm_chain.run(
            context=context,
            question=question
        )
        
        return response

def process_query(self, question: str, k: int = 3) -> dict:
        """Process a query end-to-end"""
        try:
            # Get relevant documents
            relevant_docs = self.get_relevant_docs(question, k)
            
            # Generate response
            response = self.generate_response(question, relevant_docs)
            
            # Prepare source information
            sources = [
                {
                    "page": doc.metadata.get("page", "Unknown"),
                    "source": doc.metadata.get("source", "Unknown")
                }
                for doc in relevant_docs
            ]
            
            return {
                "response": response,
                "sources": sources,
                "success": True
            }
            
        except Exception as e:
            return {
                "response": f"Error processing query: {str(e)}",
                "sources": [],
                "success": False
            }


# @tool
# def semantic_search(query: str, k: int = 3) -> str:
#     """
#     Perform semantic search on indexed documents.
#     Args:
#         query: Search query
#         k: Number of results to return
#     """
#     try:
#         results = vector_store.similarity_search(query, k=k)
#         formatted_results = []
#         for doc in results:
#             formatted_results.append({
#                 'content': doc.page_content,
#                 'metadata': doc.metadata,
#                 'similarity': doc.metadata.get('score', 'N/A')
#             })
#         return str(formatted_results)
#     except Exception as e:
#         return f"Error performing search: {str(e)}"

################################################################################################33


# @tool
# def enhanced_semantic_search(query: str, k: int = 2) -> str:
#     """
#     Perform semantic search and return processed results
#     Args:
#         query: Search query
#         k: Number of results to return
#     """
#     try:
#         results = vector_store.similarity_search(query, k=k)
#         formatted_results = []
#         for doc in results:
#             formatted_results.append({
#                 'content': doc.page_content,
#                 'metadata': doc.metadata,
#                 'similarity': doc.metadata.get('score', 'N/A')
#             })
        
#         # Process the results into a coherent response
#         raw_content = process_search_results(formatted_results)
        
#         # Structure the response
#         response = {
#             'answer': raw_content,
#             'source_count': len(formatted_results),
#             'sources': [doc['metadata'].get('source', 'Unknown') for doc in formatted_results]
#         }
        
#         return json.dumps(response)
#     except Exception as e:
#         return f"Error performing search: {str(e)}"


