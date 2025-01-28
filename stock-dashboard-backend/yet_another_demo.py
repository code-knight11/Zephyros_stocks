from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from IPython.display import Image,display
from tools import fetch_stock_price,get_company_details
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
OPENAI_API_KEY= os.getenv("open_ai_api_key")
FINNHUB_API_KEY=os.getenv("finnhub_api_key")

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    # Add scratchpad to state

# Enhanced prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial analyst with deep knowledge of stock markets and company valuations. 

    Available Tools:
    1. fetch_stock_price: Use this to get real-time stock prices, including current price, daily changes, and trading volume
    2. get_company_details: Use this to obtain company information, including business overview, market cap, and key metrics

    When asked about stocks or companies:
    - Always use appropriate tools to get current data
    - Provide comprehensive analysis
    - Explain significant price movements
    """),
    ("human", "{input}")
])

def chatbot(state: State):
    # Format prompt with current state
    formatted_prompt = prompt.format(
        input=state['messages'],  # Get last message content
        )
    
    # Get LLM response
    response = llm.invoke(formatted_prompt)

    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_name = response.tool_calls[0]
        print(f"DEBUG - Tool Used: {tool_name}")


    return {
        "messages": response,
    }

tools = [fetch_stock_price, get_company_details]
llm.bind_tools(tools=tools)

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    pass  

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "q"]:
        print("Good Bye")
        break
    
    initial_state = {
        'messages': ('user', user_input),
        'scratchpad': ''  # Initialize empty scratchpad
    }
    
    for event in graph.stream(initial_state):
        print(event.values())
        for value in event.values():
            print("Assistant:", value['messages'].content)