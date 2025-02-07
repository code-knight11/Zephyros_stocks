from flask import Flask, request, jsonify
import random
from datetime import datetime
from typing import Annotated, TypedDict
import requests
import os
import asyncio
from flask_cors import CORS
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
from functools import partial
from langchain_core.messages import (HumanMessage,ChatMessage,BaseMessage)
from typing import List

app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",  # Vite default development port
            "https://urban-broccoli-65xgp6499xphx6g5-5173.app.github.dev"  # Your GitHub Codespace frontend URL
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("open_ai_api_key")
FINNHUB_API_KEY = os.getenv("finnhub_api_key")

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
)

# Initialize tools
tools = [fetch_stock_prices, get_company_profile, search_results, get_company_news, get_basic_financials, get_recommendation_trends]

# Define State
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    chat_history:List[BaseMessage]

# Assistant Class with Scratchpad
class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable
        self.scratchpad = []

    def __call__(self, state, config: RunnableConfig):
        while True:
            state_with_scratchpad = {
                **state,
                "scratchpad": "\n".join([
                    f"Thought: {thought}" if i % 2 == 0 else f"Action: {thought}"
                    for i, thought in enumerate(self.scratchpad)
                ]),
                "chat_history": state.get("chat_history", [])  
            }
            
            result = self.runnable.invoke(state_with_scratchpad)
            
            if hasattr(result, 'tool_calls') and result.tool_calls:
                tool_name = result.tool_calls[0]
                self.scratchpad.append(f"Using tool: {tool_name}")
                print(f"DEBUG - Tool Used: {tool_name}")
            
            if not getattr(result, 'tool_calls', None) and (
                not getattr(result, 'content', None)
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
                
        return {"messages": result, "chat_history": state["chat_history"] + [result]}

# Enhanced Prompt Template with Scratchpad
primary_assistant_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a professional financial analysis assistant specialized in providing comprehensive stock market information and company insights that guides users to make better decisions regarding stocks


You are a helpful AI assistant designed to answer user queries about stocks, companies, and financial data. You have access to the following tools:

1. **fetch_stock_prices**: Use this tool to get real-time stock price data for a given stock symbol.
2. **get_company_profile**: Use this tool to fetch detailed company information using a stock symbol, ISIN, or CUSIP.
3. **get_company_news**: Use this tool to fetch the latest news articles about a company for the past 5 days.
4. **get_basic_financials**: Use this tool to fetch financial metrics (e.g., market capitalization, P/E ratio) for a given stock symbol. If the user doesn't specify a metric, prompt them to choose one.
5. **get_recommendation_trends**: Use this tool to fetch analyst recommendation trends (e.g., Strong Buy, Hold, Sell) for a given stock symbol.
6. **search_results**: Use this tool to search for companies by name and retrieve their stock symbols and descriptions.

---

### **Instructions for Tool Usage**
1. Analyze the user's query and determine which tool is most appropriate to answer it.
2. If the query requires multiple steps, break it down and use the necessary tools in sequence.
3. After using a tool, provide a clear and concise response to the user. Include the source of the information if applicable.
4. If a tool fails or you cannot find the required information, inform the user and suggest an alternative solution.
5. If the user's query is unclear, ask follow-up questions to clarify.

---

### **Examples of Tool Usage**
1. **User Query**: "What is the current stock price of AAPL?"
   - **Agent Action**: Use the `fetch_stock_prices` tool for "AAPL" and respond with the current stock price.
   - **Response**: "The current stock price of AAPL is $XXX.XX."

2. **User Query**: "Tell me about Apple Inc."
   - **Agent Action**: Use the `get_company_profile` tool for "AAPL" and respond with the company details.
   - **Response**: "Apple Inc. (AAPL) is a technology company headquartered in Cupertino, California. It specializes in consumer electronics, software, and online services."

3. **User Query**: "What are the latest news articles about Tesla?"
   - **Agent Action**: Use the `get_company_news` tool for "TSLA" and respond with the latest news.
   - **Response**: "Here are the latest news articles about Tesla: [List of articles]."

4. **User Query**: "What is the market capitalization of Microsoft?"
   - **Agent Action**: Use the `get_basic_financials` tool for "MSFT" and respond with the market capitalization.
   - **Response**: "The market capitalization of Microsoft (MSFT) is $XXX billion."

5. **User Query**: "What are the analyst recommendations for Amazon?"
   - **Agent Action**: Use the `get_recommendation_trends` tool for "AMZN" and respond with the analyst recommendations.
   - **Response**: "Analyst recommendations for Amazon (AMZN) are: Strong Buy (X%), Buy (X%), Hold (X%), Sell (X%), Strong Sell (X%)."

6. **User Query**: "Search for companies named 'Tesla'."
   - **Agent Action**: Use the `search_results` tool for "Tesla" and respond with the top result.
   - **Response**: "The top result for 'Tesla' is: Symbol: TSLA, Description: Tesla Inc., Type: Stock, Display Symbol: TSLA."

---

### **Handling Edge Cases**
1. If a tool fails or returns no data, inform the user and suggest an alternative solution.
   - Example: "Sorry, I couldn't fetch the stock price for XYZ. Please check if the symbol is correct or try again later."

2. If the user's query is unclear, ask follow-up questions to clarify.
   - Example: "Could you please specify which company or stock symbol you're referring to?"

---

### **Final Response Format**
- Always provide a clear and concise response to the user.
- If the user needs to make a choice (e.g., selecting a financial metric), provide a list of options.

---
     ### **Chat History**
{chat_history}

---

Now, respond to the following user query:
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

async def process_response(event):
    responses = []
    for value in event.values():
        if isinstance(value['messages'], list):
            for message in value['messages']:
                if hasattr(message, 'content') and message.content:
                    responses.append({"role": "assistant1", "content": message.content})
                elif hasattr(message, 'name'):
                    responses.append({"role": "tool", "content": message.content})
        else:
            message = value['messages']
            if hasattr(message, 'content') and message.content:
                responses.append({"role": "assistant2", "content": message.content})
            elif hasattr(message, 'additional_kwargs') and 'tool_calls' in message.additional_kwargs:
                responses.append({"role": "system", "content": "Processing tool request..."})
    return responses

# Initialize graph
graph = build_graph().compile()

@app.route('/chat', methods=['POST'])
async def chat():
    try:
        data = request.get_json()
        user_input = data.get('message')
        thread_id = data.get('thread_id', str(uuid.uuid4()))
        
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        
        # Initialize or retrieve chat history
        chat_history = data.get("chat_history", [])
        
        # Add the user's input to the chat history
        chat_history.append(HumanMessage(content=user_input))

        initial_input = {
            'messages': [('user', user_input)],
            'chat_history': chat_history
        }
        
        # Create a new event loop for async operations
        responses = []
        graph = build_graph().compile()
        
        async for event in graph.astream(initial_input):
            response = []
            for value in event.values():
                if isinstance(value['messages'], list):
                    for message in value['messages']:
                        if hasattr(message, 'content') and message.content:
                            response.append({
                                "role": "assistant1",
                                "content": message.content
                            })
                else:
                    message = value['messages']
                    if hasattr(message, 'content') and message.content:
                        response.append({
                            "role": "assistant2",
                            "content": message.content
                        })
            responses.extend(response)


        return jsonify({
            "thread_id": thread_id,
            "responses": responses,
            "chat_history": [msg.content for msg in chat_history]  # Return updated chat history
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
async def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

# New run.py file for running the application
if __name__ == '__main__':
    app.run(debug=True, port=5000)