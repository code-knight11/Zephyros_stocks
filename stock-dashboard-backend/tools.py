import requests
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()


FINNHUB_API_KEY=os.getenv("finnhub_api_key")
print(FINNHUB_API_KEY)
 
@tool
async def fetch_stock_price(symbol: str):
    """Fetch current stock price from Finnhub API."""
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        await asyncio.sleep(1)
        return f"{symbol} current price: ${data['c']:.2f} (Previous close: ${data['pc']:.2f})"
    except Exception as e:
        return f"Error fetching stock price: {str(e)}"
   
   
@tool
async def get_company_details(symbol:str):
    """Fetch company details from Finnhub API"""
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        await asyncio.sleep(1)
        return f"{symbol} company details: ${data}"
    except Exception as e:
        return f"Error fetching company details: {str(e)}"
    
 