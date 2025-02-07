import os
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy.engine import create_engine
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_core.tools import tool

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Database connection
mysql_username = "root"
mysql_password = "root"
mysql_host = "127.0.0.1"
mysql_database = "zephyros_db"
mysql_port = 3306

connection_string = f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
engine = create_engine(connection_string)
db = SQLDatabase(engine)

# Toolkit & Agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm, 
    toolkit=toolkit, 
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    handle_parsing_errors=True
)

# Function to handle database queries

@tool
def run_database_query(user_query: str) -> str:
    """
    Executes a user-provided query on the database and returns the result.

    Args:
        user_query (str): The natural language query to be converted into an SQL query and executed.

    Returns:
        str: The result of the query execution or an error message in case of failure.
    """
    try:
        result = agent_executor.invoke(user_query)
        print(result)
        return str(result)
    except Exception as e:
        return f"Error executing database query: {str(e)}"

