import requests
from langchain_core.tools import tool
from datetime import datetime, timedelta

AVAILABLE_METRICS = ["10DayAverageTradingVolume", "52WeekHigh", "52WeekLow", "beta", "peAnnual", "marketCapitalization"]

@tool
def fetch_stock_prices(symbol:str):
    """Get real-time quote data for US stocks and use the following:
    c: Current price
    d: Change
    dp: Percent change
    h: High price of the day
    l: Low price of the day
    o: Open price of the day
    pc: Previous close price
    """
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token=cu8u0q9r01qgljarpsh0cu8u0q9r01qgljarpshg"
    try:
        response = requests.get(url)
        data = response.json()
        return f"{symbol} quote data: ${data}"
    except Exception as e:
        return f"Error fetching quote data: {str(e)}"

    
@tool 
def get_company_profile(identifier: str, id_type: str = 'symbol'):
    """Fetch company profile from Finnhub API using symbol, ISIN, or CUSIP
    
    Args:
        identifier (str): The company identifier (symbol, ISIN, or CUSIP)
        id_type (str): Type of identifier ('symbol', 'isin', or 'cusip'). Defaults to 'symbol'
    
    Returns:
        str: Company profile data or error message
    """
    # Validate id_type
    valid_types = ['symbol', 'isin', 'cusip']
    if id_type.lower() not in valid_types:
        return f"Error: id_type must be one of {valid_types}"
    
    base_url = "https://finnhub.io/api/v1/stock/profile2"
    params = {
        id_type.lower(): identifier,
        'token': 'cu8u0q9r01qgljarpsh0cu8u0q9r01qgljarpshg'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Check if the response is empty
        if not data:
            return f"No data found for {id_type} {identifier}"
            
        return f"Company details for {id_type} {identifier}: {data}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching company details: {str(e)}"
    
@tool
def get_company_news(symbol: str):
    """Fetch the company news for the specified symbol for the past 5 days"""
    # Calculate current date and 5 days prior
    to_date = datetime.now().strftime("%Y-%m-%d")
    print(to_date)
    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(from_date)
    print("symbol: ",symbol)
    # Construct the URL
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2025-01-15&to=2025-02-20&token=cu89f81r01qhqu5cej5gcu89f81r01qhqu5cej60"
    
    try: 
        response = requests.get(url)
        print("company news response: ",response)
        data = response.json()
        print("json daata: ",data)
        return f"{symbol} company news: {data}"
    except Exception as e: 
        return f"Error fetching company news: {str(e)}"

@tool
def get_basic_financials(symbol:str):
    """Fetch a specific financial metric for a given stock symbol. If the user doesn't specify a metric, prompt them to select one."""
    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=52WeekHigh&token=cu8u0q9r01qgljarpsh0cu8u0q9r01qgljarpshg"
    try:
        response = requests.get(url)
        data = response.json()
        financials=data["metric"]
        # print("Financials",financials)
        return f"{symbol} financials: {financials}"
        # metrics = data.get('metric', {})
        # print("metrics: ",metrics)
        # if not metrics:
        #     return "No financial metrics available for this stock"
        # if metric is None:
        #     return f"Which metric are you looking for? Available options: {', '.join(metrics.keys())}"
        # if metric in metrics:
        #     return f"The {metrics} for {symbol.upper()} is {metrics[metric]}."
        # else:
        #     return f"Sorry, {metric} is not a recognized metric. Available metrics: {', '.join(metrics.keys())}"
    except Exception as e:
        return f"Error fetching basic financials: {str(e)}"
    
    
@tool 
def get_recommendation_trends(symbol:str):
    """Fetch analyst recommendation trends for the specified symbol.
     Returns detailed breakdown of analyst recommendations including:
    - Strong Buy recommendations
    - Buy recommendations
    - Hold recommendations
    - Sell recommendations
    - Strong Sell recommendations
    - Period of recommendations
    """
    url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token=cu8u0q9r01qgljarpsh0cu8u0q9r01qgljarpshg"
    try:
        response = requests.get(url)
        data = response.json()
        return f"{symbol} recommendation trends: ${data}"
    except Exception as e:
        return f"Error fetching recommendation trends: {str(e)}"

    
@tool 
def search_results(company:str):
    """Fetch company names based on the search input"""
    url = f"https://finnhub.io/api/v1/search?q={company}&exchange=US&token=cu8u0q9r01qgljarpsh0cu8u0q9r01qgljarpshg"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            top_1_results = data.get('result', [])[:1]
            for i, result in enumerate(top_1_results):
                print("Results:")
                print(f"  Symbol: {result.get('symbol')}")
                print(f"  Description: {result.get('description')}")
                print(f"  Type: {result.get('type')}")
                print(f"  Display Symbol: {result.get('displaySymbol')}")
                print()

        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        return f"Error fetching search results: {str(e)}"
