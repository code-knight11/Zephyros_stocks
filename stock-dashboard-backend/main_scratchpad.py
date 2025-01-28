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
from langgraph.graph import StateGraph, START
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import tools_condition, ToolNode
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("open_ai_api_key")
FINNHUB_API_KEY = os.getenv("finnhub_api_key")

# Initialize LLM
llm = ChatOpenAI(
   model="gpt-3.5-turbo",
   openai_api_key=OPENAI_API_KEY,
)

# Define State
class State(TypedDict):
   messages: Annotated[list[AnyMessage], add_messages]

# Assistant Class with Scratchpad
class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
        self.scratchpad = []

    def __call__(self, state, config: RunnableConfig):
        while True:
            # Add scratchpad to state
            state_with_scratchpad = {
                **state,
                "scratchpad": "\n".join([
                    f"Thought: {thought}" if i % 2 == 0 else f"Action: {thought}"
                    for i, thought in enumerate(self.scratchpad)
                ])
            }
            
            result = self.runnable.invoke(state_with_scratchpad)
            
            # Record tool usage in scratchpad - Fixed the tool_calls access
            if hasattr(result, 'tool_calls') and result.tool_calls:
                # Correctly access the function name from tool_calls
                tool_name = result.tool_calls[0]
                self.scratchpad.append(f"Using tool: {tool_name}")
                print(f"DEBUG - Tool Used: {tool_name}")  # Debug print
            
            #Checking for 'no tool calls' , 'no content' or if the content is a list and the first item is empty
            #Then it is an invalid response from llm side and hence adds the message that response with real output
            if not getattr(result, 'tool_calls', None) and (
                not getattr(result, 'content', None)
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
                
        # Print final scratchpad for debugging
        print("\nScratchpad Contents:")
        print("\n".join(self.scratchpad))
        
        return {"messages": result}
# Enhanced Prompt Template with Scratchpad
primary_assistant_prompt = ChatPromptTemplate.from_messages([
   ("system", """You are a sophisticated financial analysis assistant specialized in stocks and company information.

   Available Tools:
   1. fetch_stock_price: Retrieves real-time stock data including:
      - Current price
      - Price changes
      - Trading volume
      - Day's high/low
      
   2. get_company_details: Provides comprehensive company information:
      - Company overview
      - Market capitalization
      - Industry sector
      - Key financial metrics

   Analysis Process:
   1. Carefully understand the user's query
   2. Choose the most appropriate tool(s) for the request
   3. Analyze the gathered data thoroughly
   4. Provide clear, actionable insights
   5. Explain any significant findings or trends

   Remember to:
   - Use precise financial terminology
   - Highlight important price movements
   - Mention relevant company developments
   - Provide context for the information

   Current Thought Process:
   {scratchpad}
   """),
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

   while True:
       user_input= input("User: ")
       if user_input.lower() in ["quit","q"]:
           print("Goodbye")
           break
       
       initial_input = {'messages': [('user', user_input)]}
       result = graph.invoke(initial_input, config)
       parser = OutputParser()
       readable_output = parser.parse(result)
       print("\nProcessed Output:")
       print(readable_output)

       for event in graph.stream(initial_input):
        print(event.values())
        for value in event.values():
            print("Assistant:", value['messages'].content)
           
#    # Example interaction
#    initial_input = {"messages": [("user", "Search for market news for apple")]}
#    result = graph.invoke(initial_input, config)
#    parser = OutputParser()
#    readable_output = parser.parse(result)
#    print("\nProcessed Output:")
#    print(readable_output)