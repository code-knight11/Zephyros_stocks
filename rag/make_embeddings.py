from langchain_community.vectorstores.pinecone import Pinecone
import pinecone
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from settings import OPENAI_API_KEY,PINECONE_API_KEY

load_dotenv()

pinecone.Pinecone(api_key=PINECONE_API_KEY)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY
)
vector_store = Pinecone.from_existing_index("stockrag", embeddings)

def load_pdf(page_path):
    loader = PyPDFLoader(page_path)
    pages = []

    for page in loader.load():
        pages.append(page)

    print(f"{pages[0].metadata}\n")
    print(pages[0].page_content)

    return pages

def create_chunks(document_pages):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                   chunk_overlap=200,
                                                   separators=["\n\n", "\n", " ", ""])

    split_docs = text_splitter.split_documents(document_pages)
    print(f"Total chunks created: {len(split_docs)}")
    print(f"First chunk preview:\n{split_docs[0].page_content[:200]}...")

    return split_docs


loaded_pages=load_pdf("/workspaces/Zephyros_stocks/rag/IPT_Stocks_2015_Arkansas.pdf")
split_documents=create_chunks(loaded_pages)

# Creating a vector store and adding the vector values into it
vector_store.add_documents(split_documents)
print("Vector Store Created")
