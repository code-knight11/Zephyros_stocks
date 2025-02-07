import random
from datetime import datetime
from typing import Annotated, TypedDict
import requests
import os
import asyncio
import uuid
from custom_output_parser import OutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tools import fetch_stock_prices, get_company_profile, search_results, get_company_news, get_basic_financials, get_recommendation_trends
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
    temperature=0,
   model="gpt-3.5-turbo",
   openai_api_key=OPENAI_API_KEY,
)

# Initialize tools
tools = [fetch_stock_prices, get_company_profile, search_results, get_company_news, get_basic_financials, get_recommendation_trends]

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
# Enhanced Prompt Template with Scratchpad
primary_assistant_prompt = ChatPromptTemplate.from_messages([
   ("system", """You are a helpful sophisticated financial analysis assistant specialized in providing comprehensive stock market analysis and company insights. The following tools below are there in your for you to use and frame your response. Make sure you make the most out of them for generating the best response for the user's query. Make sure you are polite, insightful and helpful talking like a person who really understands stock market.
 
   Available Tools:
   1.fetch_stock_prices: Retrieves real-time stock quotes including:
      - Current price (c)
      - Price change (d)
      - Percent change (dp)
      - Day's high price (h)
      - Day's low price (l)
      - Opening price (o)
      - Previous close price (pc)
 
   2. get_company_profile: Provides detailed company information using:
      - Symbol
      - ISIN
      - CUSIP
      Returns comprehensive company profile and market data
 
   3. get_company_news: Fetches latest company news:
      - Last 5 days of news articles
      - Headlines and summaries
      - News sources
      - Publication dates
 
   4. get_basic_financials: Retrieves key financial metrics:
      - Margins and ratios
      - P/E ratios
      - 52-week price ranges
      - Performance indicators
      - Growth metrics
 
   5. get_recommendation_trends: Provides detailed recommendations if the user is in some sort of doubt whether to buy the stock or not or if the user asks for feedback and recommendations on stock. The recommendations should come with proper analysis and this tool should be user at the slightest hint of user asking for recommendations on stocks :
      - Strong Buy ratings
      - Buy ratings
      - Hold ratings
      - Sell ratings
      - Strong Sell ratings
      - Analysis period
      - Consensus overview
 
   6. search_results: Performs company searches providing:
      - Company symbols
      - Company descriptions
      - Security types
      - Display symbols
 
   Analysis Process:
   1. Understand the user's specific financial query
   2. Select appropriate tools for comprehensive analysis
   3. Gather and process relevant market data
   4. Analyze patterns and trends
   5. Provide actionable insights
 
   Best Practices:
   - Use precise financial terminology
   - Highlight significant market movements
   - Provide context for financial metrics
   - Consider overall market conditions
   - Include relevant risk factors
   - Maintain objective analysis
   - Cite data sources when applicable
 
   Current Thought Process:
   {scratchpad}
   """),
   ("placeholder", "{messages}"),
])

# Runnable
assistant_runnable = primary_assistant_prompt | llm.bind_tools(tools)

# Graph Construction
def build_graph():
   builder = StateGraph(State)
   builder.add_node("assistant", Assistant(assistant_runnable))
   builder.add_node("tools", ToolNode(tools))
   
   builder.add_edge(START, "assistant")
   builder.add_conditional_edges("assistant", tools_condition)
   builder.add_edge("tools", "assistant")

   return builder

async def process_graph(initial_input,graph):
    async for event in graph.astream(initial_input):  # Use astream for async streaming
        for value in event.values():
            if isinstance(value['messages'], list):
                # Handle list of messages
                for message in value['messages']:
                    if hasattr(message, 'content') and message.content:
                        print("Assistant1:", message.content)
                    elif hasattr(message, 'name'):  # This is a tool message
                        print("Assistant2:", message.content)
            else:
                # Handle single message
                message = value['messages']
                if hasattr(message, 'content') and message.content:
                    print("Assistant3:", message.content)
                elif hasattr(message, 'additional_kwargs') and 'tool_calls' in message.additional_kwargs:
                    # Just print that we're processing the tool call
                    print("Processing tool request...")

async def main():
    
   
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
       await process_graph(initial_input,graph)



# Main Execution
if __name__ == "__main__":

    asyncio.run(main())
