# import requests
# from langchain_core.tools import tool
# import os
# from dotenv import load_dotenv
# import asyncio

# load_dotenv()


# {FINNHUB_API_KEY}=os.getenv("{FINNHUB_API_KEY}")
# print({FINNHUB_API_KEY})
 
# @tool
# async def fetch_stock_price(symbol: str):
#     """Fetch current stock price from Finnhub API."""
#     url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={{FINNHUB_API_KEY}}"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         await asyncio.sleep(1)
#         return f"{symbol} current price: ${data['c']:.2f} (Previous close: ${data['pc']:.2f})"
#     except Exception as e:
#         return f"Error fetching stock price: {str(e)}"
   
   
# @tool
# async def get_company_details(symbol:str):
#     """Fetch company details from Finnhub API"""
#     url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={{FINNHUB_API_KEY}}"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         await asyncio.sleep(1)
#         return f"{symbol} company details: ${data}"
#     except Exception as e:
#         return f"Error fetching company details: {str(e)}"
    
 
# import requests
# from langchain_core.tools import tool
# from datetime import datetime, timedelta
# from dotenv import load_dotenv
# import asyncio
# import os

# load_dotenv()
# FINNHUB_API_KEY=os.getenv("{FINNHUB_API_KEY}")
# print({FINNHUB_API_KEY})


 
# AVAILABLE_METRICS = ["10DayAverageTradingVolume", "52WeekHigh", "52WeekLow", "beta", "peAnnual", "marketCapitalization"]
 
# @tool
# async def fetch_stock_prices(symbol:str):
#     """Get real-time quote data for US stocks and use the following:
#     c: Current price
#     d: Change
#     dp: Percent change
#     h: High price of the day
#     l: Low price of the day
#     o: Open price of the day
#     pc: Previous close price
#     """
#     url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         await asyncio.sleep(1)
#         return f"{symbol} quote data: ${data}"
#     except Exception as e:
#         return f"Error fetching quote data: {str(e)}"
 
   
# @tool
# async def get_company_profile(identifier: str, id_type: str = 'symbol'):
#     """Fetch company profile from Finnhub API using symbol, ISIN, or CUSIP
   
#     Args:
#         identifier (str): The company identifier (symbol, ISIN, or CUSIP)
#         id_type (str): Type of identifier ('symbol', 'isin', or 'cusip'). Defaults to 'symbol'
   
#     Returns:
#         str: Company profile data or error message
#     """
#     # Validate id_type
#     valid_types = ['symbol', 'isin', 'cusip']
#     if id_type.lower() not in valid_types:
#         return f"Error: id_type must be one of {valid_types}"
   
#     base_url = "https://finnhub.io/api/v1/stock/profile2"
#     params = {
#         id_type.lower(): identifier,
#         'token': '{{FINNHUB_API_KEY}}'
#     }
   
#     try:
#         response = requests.get(base_url, params=params)
#         response.raise_for_status()  # Raise an exception for bad status codes
#         data = response.json()
       
#         # Check if the response is empty
#         if not data:
#             return f"No data found for {id_type} {identifier}"
        
#         await asyncio.sleep(1)   
#         return f"Company details for {id_type} {identifier}: {data}"
#     except requests.exceptions.RequestException as e:
#         return f"Error fetching company details: {str(e)}"
   
# @tool
# async def get_company_news(symbol: str):
#     """Fetch the company news for the specified symbol for the past 5 days"""
#     # Calculate current date and 5 days prior
#     to_date = datetime.now().strftime("%Y-%m-%d")
#     from_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
   
#     # Construct the URL
#     url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"
   
#     try:
#         response = requests.get(url)
#         data = response.json()
#         await asyncio.sleep(1)
#         return f"{symbol} company news: {data}"
#     except Exception as e:
#         return f"Error fetching company news: {str(e)}"
 
# @tool
# async def get_basic_financials(symbol:str, metric:str=None):
#     """Fetch a specific financial metric for a given stock symbol. If the user doesn't specify a metric, prompt them to select one."""
#     url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         metrics = data.get('metric', {})
#         if not metrics:
#             return "No financial metrics available for this stock"
#         if metric is None:
#             await asyncio.sleep(1)
#             return f"Which metric are you looking for? Available options: {', '.join(metrics.keys())}"
#         if metric in metrics:
#             await asyncio.sleep(1)
#             return f"The {metrics} for {symbol.upper()} is {metrics[metric]}."
#         else:
#             await asyncio.sleep(1)
#             return f"Sorry, {metric} is not a recognized metric. Available metrics: {', '.join(metrics.keys())}"
#     except Exception as e:
#         return f"Error fetching basic financials: {str(e)}"
   
   
# @tool
# async def get_recommendation_trends(symbol:str):
#     """Fetch analyst recommendation trends for the specified symbol.
#      Returns detailed breakdown of analyst recommendations including:
#     - Strong Buy recommendations
#     - Buy recommendations
#     - Hold recommendations
#     - Sell recommendations
#     - Strong Sell recommendations
#     - Period of recommendations
#     """
#     url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={FINNHUB_API_KEY}"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         await asyncio.sleep(1)
#         return f"{symbol} recommendation trends: ${data}"
#     except Exception as e:
#         return f"Error fetching recommendation trends: {str(e)}"
 
   
# @tool
# async def search_results(company:str):
#     """Fetch company names based on the search input"""
#     url = f"https://finnhub.io/api/v1/search?q={company}&exchange=US&token={FINNHUB_API_KEY}"
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             top_1_results = data.get('result', [])[:1]
#             for i, result in enumerate(top_1_results):
#                 print("Results:")
#                 print(f"  Symbol: {result.get('symbol')}")
#                 print(f"  Description: {result.get('description')}")
#                 print(f"  Type: {result.get('type')}")
#                 print(f"  Display Symbol: {result.get('displaySymbol')}")
#                 print()
 
#         else:
#             print(f"Failed to fetch data. Status code: {response.status_code}")
#     except Exception as e:
#         return f"Error fetching search results: {str(e)}"
   

import aiohttp
from langchain_core.tools import tool
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any

load_dotenv()
FINNHUB_API_KEY = os.getenv("finnhub_api_key")
print(FINNHUB_API_KEY)

AVAILABLE_METRICS = ["10DayAverageTradingVolume", "52WeekHigh", "52WeekLow", "beta", "peAnnual", "marketCapitalization"]

async def make_api_request(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper function to make async API requests with proper error handling"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"API request failed: {str(e)}")

@tool
async def fetch_stock_prices(symbol: str) -> str:
    """Get real-time quote data for US stocks"""
    url = f"https://finnhub.io/api/v1/quote"
    params = {
        "symbol": symbol,
        "token": FINNHUB_API_KEY
    }
    print("Type: ",type(params["symbol"]))
    print("Type: ",type(params["token"]))
    try:
        data = await make_api_request(url, params)
        return f"{symbol} quote data: {data}"
    except Exception as e:
        return f"Error fetching quote data: {str(e)}"

@tool
async def get_company_profile(identifier: str, id_type: str = 'symbol') -> str:
    """Fetch company profile from Finnhub API using symbol, ISIN, or CUSIP
   
    Args:
        identifier (str): The company identifier (symbol, ISIN, or CUSIP)
        id_type (str): Type of identifier ('symbol', 'isin', or 'cusip'). Defaults to 'symbol'
   
    Returns:
        str: Company profile data or error message
    """
    valid_types = ['symbol', 'isin', 'cusip']
    if id_type.lower() not in valid_types:
        return f"Error: id_type must be one of {valid_types}"
    
    url = "https://finnhub.io/api/v1/stock/profile2"
    params = {
        id_type.lower(): identifier,
        'token': FINNHUB_API_KEY
    }
    
    try:
        data = await make_api_request(url, params)
        if not data:
            return f"No data found for {id_type} {identifier}"
        return f"Company details for {id_type} {identifier}: {data}"
    except Exception as e:
        return f"Error fetching company details: {str(e)}"

@tool
async def get_company_news(symbol: str) -> str:
    """Fetch the company news for the specified symbol for the past 5 days"""
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    
    url = "https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": symbol,
        "from": from_date,
        "to": to_date,
        "token": FINNHUB_API_KEY
    }
    
    try:
        data = await make_api_request(url, params)
        return f"{symbol} company news: {data}"
    except Exception as e:
        return f"Error fetching company news: {str(e)}"

@tool
async def get_basic_financials(symbol: str, metric: Optional[str] = None) -> str:
    """Fetch a specific financial metric for a given stock symbol. If the user doesn't specify a metric, prompt them to select one."""

    url = "https://finnhub.io/api/v1/stock/metric"
    params = {
        "symbol": symbol,
        "metric": "all",
        "token": FINNHUB_API_KEY
    }
    
    try:
        data = await make_api_request(url, params)
        metrics = data.get('metric', {})
        
        if not metrics:
            return "No financial metrics available for this stock"
        if metric is None:
            return f"Which metric are you looking for? Available options: {', '.join(metrics.keys())}"
        if metric in metrics:
            return f"The {metric} for {symbol.upper()} is {metrics[metric]}."
        return f"Sorry, {metric} is not a recognized metric. Available metrics: {', '.join(metrics.keys())}"
    except Exception as e:
        return f"Error fetching basic financials: {str(e)}"

@tool
async def get_recommendation_trends(symbol: str) -> str:
    """Fetch analyst recommendation trends for the specified symbol.
     Returns detailed breakdown of analyst recommendations including:
    - Strong Buy recommendations
    - Buy recommendations
    - Hold recommendations
    - Sell recommendations
    - Strong Sell recommendations
    - Period of recommendations
    """
    url = "https://finnhub.io/api/v1/stock/recommendation"
    params = {
        "symbol": symbol,
        "token": FINNHUB_API_KEY
    }
    
    try:
        data = await make_api_request(url, params)
        return f"{symbol} recommendation trends: {data}"
    except Exception as e:
        return f"Error fetching recommendation trends: {str(e)}"

@tool
async def search_results(company: str) -> str:
    """Fetch company names based on the search input"""
    url = "https://finnhub.io/api/v1/search"
    params = {
        "q": company,
        "exchange": "US",
        "token": FINNHUB_API_KEY
    }
    
    try:
        data = await make_api_request(url, params)
        top_1_results = data.get('result', [])[:1]
        
        output = []
        for result in top_1_results:
            output.extend([
                "Results:",
                f"  Symbol: {result.get('symbol')}",
                f"  Description: {result.get('description')}",
                f"  Type: {result.get('type')}",
                f"  Display Symbol: {result.get('displaySymbol')}"
            ])
        return "\n".join(output) if output else "No results found"
    except Exception as e:
        return f"Error fetching search results: {str(e)}"