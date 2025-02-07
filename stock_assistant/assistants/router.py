
# assistants/router.py
from dataclasses import dataclass
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.runnables import Runnable, RunnableConfig
import json
from prompts.router_prompt import router_prompt

@dataclass
class RouteMessage:
    route_to: Literal["stock", "database"]
    original_message: str

class Router:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
        
    def __call__(self, state: dict, config: RunnableConfig):
        last_message = state["messages"][-1]
        message_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        formatted_messages = router_prompt.format_messages(input=message_content)
        result = self.runnable.invoke(formatted_messages)
        
        route_to = "database" if "database" in result.content.lower() else "stock"
        
        debug_info = {
            "thought": f"I analyzed the query and found keywords that indicate a preference for '{route_to}'.",
            "reply": f"Routing to {route_to}",
            "tool_calls": result.tool_calls if hasattr(result, 'tool_calls') else []
        }
        
        routing_message = SystemMessage(content=json.dumps(debug_info))
        original_message = SystemMessage(content=message_content)
        return {"messages": [routing_message, original_message]}