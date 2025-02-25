from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage
from langgraph.prebuilt import ToolNode
import json
from models.state import State
from assistants.stock_assistant import StockAssistant
from assistants.router import Router 
from langchain_core.messages import SystemMessage
from assistants.rag_assistant import query_system
from assistants.portfolio_analyzer import PortfolioAnalysisAssistant

def route_condition(state):
    print("State Messages: ",state["messages"][-2])
    system_messages = [msg.content for msg in state["messages"] if isinstance(msg, SystemMessage)]
    second_last_system_message = system_messages[-2]
    try:
        parsed_content = json.loads(second_last_system_message)  # Parse JSON
        reply = parsed_content.get("reply")  # Extract "reply"
        print(reply) 
        if reply == "Routing to analyzer":
            print("Routing to analyzer")
            return "analyzer"
        elif reply == "Routing to rag":
            print("Routing to rag")
            return "rag"
        elif reply == "Routing to default":
            print("Routing to default")
            return "default"
        else:
            print("Routing to stock assistant")
            return "stock" # Output: Routing to stock
    except json.JSONDecodeError:
        print("Error: System message is not valid JSON")# Default to stock assistant if no route specified

def enhanced_route_condition(state):
        messages = state["messages"]
        if any("user_id" in str(msg.content) for msg in messages):
            return "portfolio_analyzer"
        return route_condition(state)

def stock_tools_condition(state):
    last_message = state["messages"][-1]
    if hasattr(last_message, 'additional_kwargs') and last_message.additional_kwargs.get('tool_calls'):
        return "stock_tools"
    return None

def portfolio_tools_condition(state):
    last_message = state["messages"][-1]
    return "portfolio_tools" if hasattr(last_message, 'additional_kwargs') and \
           last_message.additional_kwargs.get('tool_calls') else None
           


def build_graph(llm,portfolio_tools, stock_tools, stock_assistant_runnable, portfolio_assistant_runnable,stock_analyzer_runnable):
    builder = StateGraph(State)
    
    # db_tool_node = ToolNode(db_tools)
    stock_tool_node = ToolNode(stock_tools)
    portfolio_tool_node=ToolNode(portfolio_tools)
    
    # Add nodes
    builder.add_node("router", Router(llm)) 
    builder.add_node("stock_assistant", StockAssistant(stock_assistant_runnable))
    builder.add_node("stock_tools", stock_tool_node)
    
    #TODO get the user_id into the assistant class
    #TODO to write the proper Assistant class
    builder.add_node("portfolio_assistant", PortfolioAnalysisAssistant(portfolio_assistant_runnable,stock_analyzer_runnable))
    # builder.add_node("db_tools", db_tool_node)
    builder.add_node("portfolio_tools",portfolio_tool_node)
    builder.add_node("rag_assistant", query_system)
    builder.add_node("default_assistant", lambda state: END)
    
    
    # Add edges
    builder.add_edge(START, "router")
    
    # Add conditional edges for the router
    builder.add_conditional_edges(
        "router",
        route_condition,
        {
            "stock": "stock_assistant",
            "rag": "rag_assistant",
            "analyzer": "portfolio_assistant",
            "default": "default_assistant"
        }
    )
    
    # Rest of the edges remain the same
    builder.add_conditional_edges(
        "stock_assistant",
        stock_tools_condition,
        {
            "stock_tools": "stock_tools",
            None: END
        }
    )
    builder.add_edge("stock_tools", "stock_assistant")
    
    builder.add_conditional_edges(
        "portfolio_assistant",
        portfolio_tools_condition,
        {
            "portfolio_tools":"portfolio_tools",
            None: END
        }
    )
    builder.add_edge("portfolio_tools", END)
    builder.add_edge("rag_assistant", END)
    return builder
