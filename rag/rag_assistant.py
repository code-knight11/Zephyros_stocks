from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import SystemMessage
import json
from rag_tools import semantic_search

class rag_assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
        self.scratchpad = []

    def process_search_results(self, results_str: str) -> str:
        """Process the search results into a coherent response"""
        try:
            results = json.loads(results_str)
            context = "\n\n".join([doc['content'] for doc in results])
            return context
        except:
            return results_str

    def __call__(self, state, config):
        message_content = None
        for message in reversed(state["messages"]):
            if hasattr(message, "content") and "route_to" not in message.content:
                message_content = message.content
                break
                
        if not message_content:
            return {"messages": SystemMessage(content="No valid message found")}
        
        # First, get search results
        search_results = semantic_search(message_content)
        print("****************************************************************")
        print(search_results)
        print("****************************************************************")
        processed_results = self.process_search_results(search_results)
            
        # Then, prepare the full context for the LLM
        state_with_context = {
            "messages": message_content,
            "tool_use": f"I found the following relevant information:\n{processed_results}",
            "response": "Let me analyze this information and provide a comprehensive answer."
        }
        
        # Get final response
        result = self.runnable.invoke(state_with_context)
        return {"messages": result}