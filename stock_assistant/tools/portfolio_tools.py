import os
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy.engine import create_engine
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_core.tools import tool
import requests
from langchain_core.tools import tool
from datetime import datetime, timedelta
import json

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)
AVAILABLE_METRICS = ["10DayAverageTradingVolume", "52WeekHigh", "52WeekLow", "beta", "peAnnual", "marketCapitalization"]
# Database connection
mysql_username = "root"
mysql_password = ""
mysql_host = "localhost"
mysql_port = 3306
databases = ["zephyros_userdata", "zephyros_marketdata"]

# creating separate connections for each database
engine_userdata = create_engine(f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/zephyros_userdata")
engine_marketdata = create_engine(f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/zephyros_marketdata")

# initializing SQLDatabase instances for each database
db_userdata = SQLDatabase(engine_userdata, include_tables=["users","stocks"])
db_marketdata = SQLDatabase(engine_marketdata, include_tables=["user_portfolios"])

# Create toolkits for each database
toolkit_userdata = SQLDatabaseToolkit(db=db_userdata, llm=llm)
toolkit_marketdata = SQLDatabaseToolkit(db=db_marketdata, llm=llm)

# agents for both databases
agent_executor_userdata = create_sql_agent(
    llm=llm, 
    toolkit=toolkit_userdata, 
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    handle_parsing_errors=True
)

agent_executor_marketdata = create_sql_agent(
    llm=llm, 
    toolkit=toolkit_marketdata, 
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    handle_parsing_errors=True
)

# Function to handle database queries
@tool
def run_database_query(user_query: str, database: str) -> str:
    """
    Executes a user-provided query on the selected database and returns the result.
 
    Args:
        user_query (str): The natural language query to be converted into an SQL query and executed.
        database (str): The database to query ("userdata" or "marketdata").
 
    Returns:
        str: The result of the query execution or an error message in case of failure.
    """
    try:
        if database == "userdata":
            result = agent_executor_userdata.invoke(user_query)
        elif database == "marketdata":
            print("Tool calling taking place for marketdata")
            result = agent_executor_marketdata.invoke(user_query)
            print("Result of the tool call: ",result)
        else:
            return "Invalid database selection. Choose 'userdata' or 'marketdata'."
       
        print(result)
        return str(result)
   
    except Exception as e:
        return f"Error executing database query: {str(e)}"
