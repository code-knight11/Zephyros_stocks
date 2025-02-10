# from langchain_core.runnables import Runnable, RunnableConfig
# from langchain_core.messages import SystemMessage
# import json
# from rag_tools import semantic_search

# class rag_assistant:
#     def __init__(self, runnable: Runnable):
#         self.runnable = runnable
#         self.scratchpad = []

#     def process_search_results(self, results_str: str) -> str:
#         """Process the search results into a coherent response"""
#         try:
#             results = json.loads(results_str)
#             context = "\n\n".join([doc['content'] for doc in results])
#             return context
#         except:
#             return results_str

#     def __call__(self, state, config):
#         message_content = None
#         for message in reversed(state["messages"]):
#             if hasattr(message, "content") and "route_to" not in message.content:
#                 message_content = message.content
#                 break
                
#         if not message_content:
#             return {"messages": SystemMessage(content="No valid message found")}
        
#         # First, get search results
#         search_results = semantic_search(message_content)
#         print("****************************************************************")
#         print(search_results)
#         print("****************************************************************")
#         processed_results = self.process_search_results(search_results)
            
#         # Then, prepare the full context for the LLM
#         state_with_context = {
#             "messages": message_content,
#             "tool_use": f"I found the following relevant information:\n{processed_results}",
#             "response": "Let me analyze this information and provide a comprehensive answer."
#         }
        
#         # Get final response
#         result = self.runnable.invoke(state_with_context)
#         return {"messages": result}

from langchain_community.vectorstores.pinecone import Pinecone
import pinecone
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from settings import OPENAI_API_KEY, PINECONE_API_KEY
import os

load_dotenv()

# Initialize Pinecone and embeddings
pinecone.Pinecone(api_key=PINECONE_API_KEY)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY
)
vector_store = Pinecone.from_existing_index("stockrag", embeddings)

llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-3.5-turbo",
    api_key=OPENAI_API_KEY
)

RESPONSE_TEMPLATE = """
You are a helpful financial advisor assistant. Using the provided context, answer the user's question in a clear, concise, and informative way.
If the information in the context is not sufficient, say so.

Context from documents:
{context}

User Question: {question}

Please provide a well-structured response that:
1. Directly answers the question
2. Includes relevant examples or explanations where appropriate
3. Highlights any important caveats or considerations

Response:
"""

response_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=RESPONSE_TEMPLATE
)

class EnhancedRAGSystem:
    def __init__(self, vector_store, llm, prompt):
        self.vector_store = vector_store
        # Store the prompt template separately
        self.prompt_template = prompt
        # Create the chain
        self.chain = prompt | llm
    
    def get_relevant_docs(self, question: str, k: int = 3) -> List:
        """Get relevant documents from vector store"""
        if not isinstance(question, str):
            question = str(question)
        # Fix: This line was incorrectly indented in your code
        results = self.vector_store.similarity_search(
            query=question,
            k=k
        )
        return results
    
    def generate_response(self, question: str, context_docs: List) -> str:
        """Generate a response using the LLM chain"""
        # Combine context from all relevant documents
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        input_dict = {
            "context": context,
            "question": question
        }

        # Generate response
        response = self.chain.invoke(input_dict)
        
        return response.content if hasattr(response, 'content') else str(response)

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

# Initialize the enhanced RAG system
rag_system = EnhancedRAGSystem(vector_store, llm, response_prompt)

def query_system(state) -> dict:
    """Query the RAG system and print the response"""
    try:
        # Extract the question from the messages
        messages = state['messages']
        if isinstance(messages, list):
            # Handle tuple format (user, message)
            question = messages[0][1] if isinstance(messages[0], tuple) else messages[0]
        else:
            # Handle direct message content
            question = messages
            
        if hasattr(question, 'content'):
            # Handle LangChain message objects
            question = question.content
            
        # Now process the query with the extracted question
        result = rag_system.process_query(str(question))
        print(result)
        
        if result["success"]:
            print("\nResponse:")
            print("-" * 50)
            print(result["response"])
            print("\nSources:")
            print("-" * 50)
            for source in result["sources"]:
                print(f"Page {source['page']} from {source['source']}")
            return {"messages": result["response"]}
        else:
            error_response = f"Error processing query: {result['response']}"
            print("\nError:", error_response)
            return {"messages": error_response}
            
    except Exception as e:
        error_message = f"Error in query processing: {str(e)}"
        print("\nError:", error_message)
        return {"messages": error_message}