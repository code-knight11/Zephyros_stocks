from langchain_core.prompts import ChatPromptTemplate

rag_assistant_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a RAG assistant. Your role is to help users manage and query documents.
    Available tools:
    - semantic_search: Search for relevant information in indexed documents
    
    For each query:
    2. Use appropriate tools to handle the request
    3. Provide clear, concise responses
    """),
    ("user", "{messages}")
])