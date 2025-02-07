import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Ensure CA certificates for secure connection
os.environ['CURL_CA_BUNDLE'] = 'C:/Users/RACHANAA/Downloads/cacert.pem'

# Database metadata
META_DATA = [
    {
        "table_name": "users_table",
        "columns": [
            {"name": "user_id", "desc": "user identity code", "data type": "integer", "example": "1"},
            {"name": "name", "desc": "user name", "data type": "varchar", "example": "Rachana A"},
            {"name": "email", "desc": "user email", "data type": "varchar", "example": "rachanaa@virtusa.com"},
        ],
    },
    {
        "table_name": "stocks_table",
        "columns": [
            {"name": "stock_id", "desc": "stock identity code", "data type": "varchar", "example": "1"},
            {"name": "symbol", "desc": "stock identification symbol", "data type": "varchar", "example": "AAPL"},
            {"name": "company_name", "desc": "company name for the stock", "data type": "string", "example": "Apple Inc."}
        ],
    }
]
