import random
from datetime import datetime
from typing import Annotated, TypedDict
import requests
import os
from custom_output_parser import OutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tools import fetch_stock_price, get_company_details
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import StateGraph, START,END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import tools_condition, ToolNode
from dotenv import load_dotenv
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image
 
load_dotenv()
OPENAI_API_KEY= os.getenv("open_ai_api_key")
FINNHUB_API_KEY=os.getenv("finnhub_api_key")
 
# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
)
 
# Define State
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
 
# Prompt Template
primary_assistant_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful stock price assistant. Use the fetch_stock_price tool to get current stock information and use get_company_details to get details about the company."),
    ("placeholder", "{messages}"),
])
 
# Runnable
assistant_runnable = primary_assistant_prompt | llm.bind_tools([fetch_stock_price, get_company_details])
 
# Graph Construction
def build_graph():
    builder = StateGraph(State)
    builder.add_node("assistant", Assistant(assistant_runnable))
    builder.add_node("tools", ToolNode([fetch_stock_price, get_company_details]))
   
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    builder.add_edge("assistant",END)
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
    initial_input = {"messages": [("user", "Give me the stock price of nvidia8?")]}
    result = graph.invoke(initial_input, config)
    # print("-------------------------",result)
    parser = OutputParser()
    readable_output = parser.parse(result)
    print(readable_output)