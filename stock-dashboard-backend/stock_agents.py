import requests
import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import StateGraph, START
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import tools_condition, ToolNode

load_dotenv()

OPENAI_API_KEY= os.getenv("open_ai_api_key")
FINNHUB_API_KEY=os.getenv("finnhub_api_key")

print(FINNHUB_API_KEY)
 
# Initialize ChatGroq
llm= ChatOpenAI(api_key=OPENAI_API_KEY,model="gpt-4o-mini")


# Pydantic Model for Stock Information
class StockInfo(BaseModel):
    symbol: str = Field(description="Stock symbol")
    current_price: float = Field(description="Current stock price")
    previous_close: float = Field(description="Previous closing price")
    price_change: float = Field(description="Price change")

# Stock Price Tool
@tool
def fetch_stock_price(symbol: str) -> StockInfo:
    """Fetch current stock price from Finnhub API."""
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        return StockInfo(
            symbol=symbol,
            current_price=data['c'],
            previous_close=data['pc'],
            price_change=data['c'] - data['pc']
        )
    except Exception as e:
        raise ValueError(f"Error fetching stock price: {str(e)}")

# State Definition
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# Assistant Class
class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

# Prompt Template with Output Parser
primary_assistant_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are a helpful stock price assistant. 
    Use the fetch_stock_price tool to get current stock information.
    Parse the stock information into a clear, concise format.
    """),
    ("placeholder", "{messages}"),
])

# Runnable with Tool Binding
assistant_runnable = primary_assistant_prompt | llm.bind_tools([fetch_stock_price])

# Graph Construction
def build_graph():
    builder = StateGraph(State)
    builder.add_node("assistant", Assistant(assistant_runnable))
    builder.add_node("tools", ToolNode([fetch_stock_price]))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder

# Main Execution
if __name__ == "__main__":
    import uuid
    
    builder = build_graph()
    graph = builder.compile()
    
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "user_id": "stock_assistant",
            "thread_id": thread_id,
        }
    }

    # Example interaction
    initial_input = {"messages": [("user", "What is the current price of AAPL?")]}
    result = graph.invoke(initial_input, config)
    print(result)