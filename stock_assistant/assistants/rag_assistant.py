from langchain_community.vectorstores.pinecone import Pinecone
import pinecone
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from config.settings import OPENAI_API_KEY, PINECONE_API_KEY
import os
from langchain_core.messages import SystemMessage, AIMessage

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
    """Query the RAG system and return the response in the expected format"""
    try:
        # Extract the question from the messages
        messages = state['messages']
        if isinstance(messages, list):
            # Get the last non-routing message
            for msg in reversed(messages):
                if isinstance(msg, tuple):
                    question = msg[1]
                    break
                elif hasattr(msg, 'content') and 'route_to' not in str(msg.content):
                    question = msg.content
                    break
                else:
                    question = str(msg)
        else:
            question = messages
            
        if hasattr(question, 'content'):
            question = question.content
            
        # Process the query with the extracted question
        result = rag_system.process_query(str(question))
        
        if result["success"]:
            # Return in a format that process_message can handle
            from langchain_core.messages import AIMessage
            return {
                "messages": AIMessage(
                    content=result["response"],
                    additional_kwargs={"sources": result["sources"]}
                )
            }
        else:
            return {
                "messages": AIMessage(
                    content=f"Error processing query: {result['response']}"
                )
            }
            
    except Exception as e:
        return {
            "messages": AIMessage(
                content=f"Error in query processing: {str(e)}"
            )
        }
