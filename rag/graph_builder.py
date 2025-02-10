from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage
from langgraph.prebuilt import ToolNode
import json
from state import State 
# from stock_assistant.assistants.db_assistant import DBAssistant
from stock_assistant import StockAssistant
from rag_assistant import query_system
from router import Router 
from langchain_core.messages import SystemMessage

def route_condition(state):
    print("State Messages: ",state["messages"][-2])
    system_messages = [msg.content for msg in state["messages"] if isinstance(msg, SystemMessage)]
    second_last_system_message = system_messages[-2]
    try:
        parsed_content = json.loads(second_last_system_message)  # Parse JSON
        reply = parsed_content.get("reply")  # Extract "reply"
        print(reply) 
        if reply == "Routing to database":
            print("Routing to database")
            return "database"
        elif reply == "Routing to rag":
            print("Routing to rag")
            return "rag"
        else:
            print("Routing to stock assistant")
            return "stock" # Output: Routing to stock
    except json.JSONDecodeError:
        print("Error: System message is not valid JSON")# Default to stock assistant if no route specified


def stock_tools_condition(state):
    last_message = state["messages"][-1]
    if hasattr(last_message, 'additional_kwargs') and last_message.additional_kwargs.get('tool_calls'):
        return "stock_tools"
    return None

# def rag_tools_condition(state):
#     last_message=state["messages"][-1]
#     if hasattr(last_message,'additional_kwargs') and last_message.additional_kwargs.get('tool_calls'):
#         return 'rag_tools'
#     return None

def db_tools_condition(state):
    last_message = state["messages"][-1]
    return "db_tools" if hasattr(last_message, 'additional_kwargs') and \
           last_message.additional_kwargs.get('tool_calls') else None

def build_graph(llm, stock_tools ,stock_assistant_runnable):
    builder = StateGraph(State)
    
    builder.add_node("router", Router(llm))
    builder.add_node("stock_assistant", StockAssistant(stock_assistant_runnable))
    builder.add_node("stock_tools", ToolNode(stock_tools))
    builder.add_node("rag_assistant",query_system)
    # builder.add_node("rag_tools",ToolNode(rag_tools))
    # builder.add_node("db_assistant", DBAssistant(db_assistant_runnable))
    # builder.add_node("db_tools", ToolNode(db_tools))
    
    builder.add_edge(START, "router")
    
    builder.add_conditional_edges(
        "router",
        route_condition,
        {
            "stock": "stock_assistant",
            "rag":"rag_assistant"
            
        }
    )
    
    builder.add_conditional_edges(
        "stock_assistant",
        stock_tools_condition,
        {
            "stock_tools": "stock_tools",
            None: END
        }
    )
    builder.add_edge("stock_tools", "stock_assistant")
    builder.add_edge("rag_assistant", END)
    
    
    
    
    # builder.add_conditional_edges(
    #     "db_assistant",
    #     db_tools_condition,
    #     {
    #         "db_tools": "db_tools",
    #         None: END
    #     }
    # )
    # builder.add_edge("db_tools", END)
    
    return builder