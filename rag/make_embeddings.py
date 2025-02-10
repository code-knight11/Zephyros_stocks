# from langchain_community.vectorstores.pinecone import Pinecone
# import pinecone
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# import os
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PyPDFLoader
# from settings import OPENAI_API_KEY,PINECONE_API_KEY

# load_dotenv()

# pinecone.Pinecone(api_key=PINECONE_API_KEY)
# embeddings = OpenAIEmbeddings(
#     model="text-embedding-3-small",
#     api_key=OPENAI_API_KEY
# )
# vector_store = Pinecone.from_existing_index("stockrag", embeddings)

# def load_pdf(page_path):
#     loader = PyPDFLoader(page_path)
#     pages = []

#     for page in loader.load():
#         pages.append(page)

#     print(f"{pages[0].metadata}\n")
#     print(pages[0].page_content)

#     return pages

# def create_chunks(document_pages):
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
#                                                    chunk_overlap=200,
#                                                    separators=["\n\n", "\n", " ", ""])

#     split_docs = text_splitter.split_documents(document_pages)
#     print(f"Total chunks created: {len(split_docs)}")
#     print(f"First chunk preview:\n{split_docs[0].page_content[:200]}...")

#     return split_docs

# def get_relevant_docs(user_question):
#     results = vector_store.similarity_search(query=user_question, k=1)

#     for doc in results:
#         print(f"{doc.page_content}")

#     return results

# # loaded_pages=load_pdf("/workspaces/Zephyros_stocks/rag/IPT_Stocks_2015_Arkansas.pdf")
# # split_documents=create_chunks(loaded_pages)

# # # Creating a vector store and adding the vector values into it
# # vector_store.add_documents(split_documents)
# # print("Vector Store Created")

# question = "what should be the investment objectives?"
# relevant_results = get_relevant_docs(question)
# print(relevant_results)



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

# Initialize ChatOpenAI for response generation
llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-3.5-turbo",
    api_key=OPENAI_API_KEY
)

# Create prompt template for response generation
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
        self.llm_chain = LLMChain(llm=llm, prompt=prompt)
    
    def load_pdf(self, page_path: str) -> List:
        """Load PDF and return pages"""
        loader = PyPDFLoader(page_path)
        pages = loader.load()
        print(f"Loaded PDF with {len(pages)} pages")
        return pages

    def create_chunks(self, document_pages: List) -> List:
        """Create chunks from document pages"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?"],
            length_function=len
        )
        
        split_docs = text_splitter.split_documents(document_pages)
        print(f"Created {len(split_docs)} chunks")
        return split_docs

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

# Initialize the enhanced RAG system
rag_system = EnhancedRAGSystem(vector_store, llm, response_prompt)

def index_new_document(file_path: str) -> None:
    """Index a new document into the vector store"""
    loaded_pages = rag_system.load_pdf(file_path)
    split_documents = rag_system.create_chunks(loaded_pages)
    vector_store.add_documents(split_documents)
    print("Document indexed successfully")

def query_system(question: str) -> None:
    """Query the RAG system and print the response"""
    result = rag_system.process_query(question)
    
    if result["success"]:
        print("\nResponse:")
        print("-" * 50)
        print(result["response"])
        print("\nSources:")
        print("-" * 50)
        for source in result["sources"]:
            print(f"Page {source['page']} from {source['source']}")
    else:
        print("\nError:")
        print(result["response"])

# Example usage:
if __name__ == "__main__":
    # To index a new document:
    # index_new_document("/path/to/your/document.pdf")
    
    # To query the system:
    question = "what are DON’Ts for investing in IPOs/FPOs"
    query_system(question)