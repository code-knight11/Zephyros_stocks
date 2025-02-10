import asyncio
import uuid
from langchain_openai import ChatOpenAI
from settings import OPENAI_API_KEY
from stock_tools import fetch_stock_prices, get_company_profile, search_results, get_company_news, get_basic_financials, get_recommendation_trends
# from tools.db_tools import run_database_query
from stock_prompts import stock_assistant_prompt
# from stock_assistant.prompts.db_prompts import db_assistant_prompt
from rag_prompt import rag_assistant_prompt
from graph_builder import build_graph
# from rag_tools import semantic_search

# db_tools = [run_database_query]
stock_tools = [fetch_stock_prices, get_company_profile, search_results, get_company_news, get_basic_financials, get_recommendation_trends]
# rag_tools=[semantic_search]

async def process_graph(initial_input, graph):
    async for event in graph.astream(initial_input):
        for value in event.values():
            if isinstance(value['messages'], list):
                for message in value['messages']:
                    if isinstance(message, dict) or (hasattr(message, 'content') and 'route_to' in message.content):
                        continue
                    if hasattr(message, 'content') and message.content[1]:
                        print("Assistant1:", message.content)
                    elif hasattr(message, 'name'):
                        print("Tool:", message.name)
            else:
                message = value['messages']
                if hasattr(message, 'content') and message.content:
                    if 'route_to' not in message.content:
                        print("Assistant2:", message.content)

async def main():
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo",
        openai_api_key=OPENAI_API_KEY,
    )
    
    stock_assistant_runnable = stock_assistant_prompt | llm.bind_tools(stock_tools)
    # db_assistant_runnable = db_assistant_prompt | llm.bind_tools(db_tools)
    builder = build_graph(llm, stock_tools=stock_tools, stock_assistant_runnable=stock_assistant_runnable)
    graph = builder.compile()
   
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {
           "user_id": "stock_assistant",
           "thread_id": thread_id,
        }
    }

    print("Assistant: Hi! Welcome to the StockBot. How can I help you today?")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "q"]:
            print("Goodbye")
            break
       
        initial_input = {'messages': [('user', user_input)]}
        await process_graph(initial_input, graph)

if __name__ == "__main__":
    asyncio.run(main())