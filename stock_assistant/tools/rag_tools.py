from langchain_core.tools import tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict
import os
from langchain_community.vectorstores.pinecone import Pinecone
import pinecone
from langchain_community.document_loaders import PyPDFLoader
import hashlib
import json
from pathlib import Path

class DocumentManager:
    def __init__(self, index_name: str):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize Pinecone
        pinecone.Pinecone(api_key=os.environ['PINECONE_API_KEY'])
        self.vector_store = Pinecone.from_existing_index(index_name, self.embeddings)
        
        # Create a directory to store processed document records
        self.processed_docs_dir = Path("processed_documents")
        self.processed_docs_dir.mkdir(exist_ok=True)
        self.processed_docs_file = self.processed_docs_dir / "processed_docs.json"
        
        # Load processed documents record
        self.processed_docs = self._load_processed_docs()

    def _load_processed_docs(self) -> dict:
        """Load the record of processed documents"""
        if self.processed_docs_file.exists():
            with open(self.processed_docs_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_processed_docs(self):
        """Save the record of processed documents"""
        with open(self.processed_docs_file, 'w') as f:
            json.dump(self.processed_docs, f)

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def load_and_index_pdf(self, pdf_path: str) -> str:
        """Load and index a PDF if it hasn't been processed before"""
        # Calculate file hash
        file_hash = self._calculate_file_hash(pdf_path)
        
        # Check if file has already been processed
        if file_hash in self.processed_docs:
            return f"Document {pdf_path} has already been processed. Skipping..."
        
        try:
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            
            texts = []
            metadatas = []
            
            for page in pages:
                splits = text_splitter.split_text(page.page_content)
                texts.extend(splits)
                page_metadata = page.metadata.copy()
                page_metadata['source_file'] = pdf_path
                metadatas.extend([page_metadata] * len(splits))
            
            # Add to vector store
            self.vector_store.add_texts(texts=texts, metadatas=metadatas)
            
            # Record the processed document
            self.processed_docs[file_hash] = {
                'path': pdf_path,
                'chunks': len(texts),
                'processed_date': str(Path(pdf_path).stat().st_mtime)
            }
            self._save_processed_docs()
            
            return f"Successfully indexed {len(texts)} chunks from {pdf_path}"
            
        except Exception as e:
            return f"Error processing document {pdf_path}: {str(e)}"

    def semantic_search(self, query: str, k: int = 3) -> List[Dict]:
        """Perform semantic search on indexed documents"""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return [{
                'content': doc.page_content,
                'metadata': doc.metadata,
                'similarity': doc.metadata.get('score', 'N/A')
            } for doc in results]
        except Exception as e:
            raise Exception(f"Error performing search: {str(e)}")

# Usage example
doc_manager = DocumentManager("stockrag")

@tool
def index_pdf(pdf_path: str) -> str:
    """Index a PDF document if it hasn't been processed before"""
    return doc_manager.load_and_index_pdf(pdf_path)

@tool
def search_documents(query: str, k: int = 3) -> str:
    """Search indexed documents"""
    return str(doc_manager.semantic_search(query, k=k))