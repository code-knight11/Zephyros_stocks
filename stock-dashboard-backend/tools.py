
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