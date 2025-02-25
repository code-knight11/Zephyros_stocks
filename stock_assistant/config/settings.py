import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("open_ai_api_key")
FINNHUB_API_KEY = os.getenv("finnhub_api_key")
PINECONE_API_KEY= os.getenv("PINECONE_API_KEY")

# Ensure CA certificates for secure connection
os.environ['CURL_CA_BUNDLE'] = "C:\\Users\\swajanghosh\\Downloads\\stock_assistant (2)\\stock_assistant\\cacert.pem"
# os.environ['CURL_CA_BUNDLE'] = "C:\\Users\\RACHANAA\\Downloads\\stock_assistant_v5\\stock_assistant\\cacert.pem"

# Database metadata
META_DATA = [
    {
        "Database": "zephyros_marketdata",
        "table_name": "user_portfolios",
        "columns": [
            {
                "name": "portfolio_id",
                "desc": "Primary key, Unique identifier for the portfolio",
                "data type": "integer",
                "example": "1"
            },
            {
                "name": "user_id",
                "desc": "Foreign key referencing users.user_id, representing the user who owns the portfolio",
                "data type": "integer",
                "example": "3"
            },
            {
                "name": "stock_id",
                "desc": "Foreign key referencing stocks.stock_id, representing the stock in the portfolio",
                "data type": "integer",
                "example": "101"
            },
            {
                "name": "quantity",
                "desc": "Number of shares owned by the user",
                "data type": "integer",
                "example": "20"
            },
            {
                "name": "purchase_price",
                "desc": "Price at which the user bought the stock",
                "data type": "decimal(10,2)",
                "example": "150.25"
            },
            {
                "name": "purchase_date",
                "desc": "Timestamp of when the stock was purchased",
                "data type": "timestamp",
                "example": "2024-01-15 10:30:00"
            }
        ]
    },
    {
        "Database": "zephyros_marketdata",
        "table_name": "stocks",
        "columns": [
            {
                "name": "stock_id",
                "desc": "Primary key, unique stock identifier",
                "data type": "integer",
                "example": "101"
            },
            {
                "name": "symbol",
                "desc": "Stock symbol (ticker)",
                "data type": "varchar(10)",
                "example": "BCOMF"
            },
            {
                "name": "company_name",
                "desc": "Company name",
                "data type": "varchar(100)",
                "example": "B COMMUNICATIONS LTD"
            },
            {
                "name": "currency",
                "desc": "Currency of the stock (e.g., USD)",
                "data type": "varchar(10)",
                "example": "USD"
            },
            {
                "name": "display_symbol",
                "desc": "Display symbol for the stock",
                "data type": "varchar(10)",
                "example": "BCOMF"
            },
            {
                "name": "figi",
                "desc": "Financial Instrument Global Identifier",
                "data type": "varchar(20)",
                "example": "BBG000TK6G65"
            },
            {
                "name": "mic",
                "desc": "Market Identifier Code (exchange or market)",
                "data type": "varchar(10)",
                "example": "OOTC"
            },
            {
                "name": "share_class_figi",
                "desc": "Financial Instrument Global Identifier for the share class",
                "data type": "varchar(20)",
                "example": "BBG001SRC3F1"
            },
            {
                "name": "stock_type",
                "desc": "Type of stock (e.g., Common Stock)",
                "data type": "varchar(255)",
                "example": "Common Stock"
            }
        ]
    },
    {
        "Database": "zephyros_userdata",
        "table_name": "users",
        "columns": [
            {
                "name": "user_id",
                "desc": "User identity code",
                "data type": "integer",
                "example": "3"
            },
            {
                "name": "name",
                "desc": "User's full name",
                "data type": "varchar(100)",
                "example": "Rachana A"
            },
            {
                "name": "email",
                "desc": "User's email address",
                "data type": "varchar(100)",
                "example": "rachanaa@virtusa.com"
            },
            {
                "name": "password",
                "desc": "User's hashed password",
                "data type": "varchar(255)",
                "example": "hashed_password_value"
            },
            {
                "name": "phone_number",
                "desc": "User's phone number",
                "data type": "varchar(20)",
                "example": "+1-234-567-8901"
            },
            {
                "name": "address",
                "desc": "User's home or billing address",
                "data type": "varchar(255)",
                "example": "1234 Elm Street, Some City, Some State, 12345"
            },
            {
                "name": "date_of_birth",
                "desc": "User's date of birth",
                "data type": "date",
                "example": "1990-05-15"
            },
            {
                "name": "join_date",
                "desc": "Date when the user registered",
                "data type": "timestamp",
                "example": "2022-10-10 12:30:45"
            }
        ]
    }
]

