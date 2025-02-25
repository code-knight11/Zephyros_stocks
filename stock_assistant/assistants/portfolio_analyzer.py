from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from config.settings import OPENAI_API_KEY 
from langchain_core.prompts import ChatPromptTemplate
from tools.stock_tools import (
    fetch_stock_prices,
    get_company_profile,
    get_company_news,
    get_basic_financials,
    get_recommendation_trends
)
from tools.portfolio_tools import run_database_query
import json
import uuid
from typing import Dict, Any, List
import re

class PortfolioAnalysisAssistant:
    def __init__(self, runnable: Runnable, runnable2:Runnable):
        self.runnable = runnable
        self.runnable2=runnable2
        self.scratchpad = []
        
    def __call__(self, state: Dict[str, Any], config: RunnableConfig):
        # Extract user_id from context
        user_id = state.get("context", {}).get("user_id")
        print("user id: ",user_id)
        if not user_id:
            return {"messages": SystemMessage(content="Error: No user_id provided in context")}

        last_message = state["messages"][-1]
        print("last message: ",last_message)
            
        # Process initial user message
        return self._process_initial_message(state, user_id)
    
    
    def handle_message_result(self,result):
        try:
            print("inside try")
            # Extract tool calls if they exist
            if hasattr(result, 'tool_calls') and result.tool_calls:
                print("inside if")
                print("result tool: ",result)
                tool_call = result.tool_calls[0]  # Assuming we want the first tool call
                print("first tool call: ",tool_call)
                
                # Extract the function details
                # function_args = tool_call.function.arguments if hasattr(tool_call, 'function') else {}
                function_name=tool_call['name']
                arguments=tool_call['args']
                print("F NAME: ",function_name)
                print("ARGS NAME: ",arguments)
                
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        pass
                
                print("ARGS 2: ",arguments)
                # # If function_args is a string, parse it as JSON
                # if isinstance(function_args, str):
                #     try:
                #         function_args = json.loads(function_args)
                #     except json.JSONDecodeError:
                #         pass
                    
                return {
                'function_name': function_name,
                'arguments': arguments
            }
                
            # If no tool calls, return the content if it exists
            elif hasattr(result, 'content') and result.content:
                return {'content': result.content}
                
            # Fallback case
            return {'error': 'Unable to parse result'}
            
        except Exception as e:
            return {'error': f'Error processing result: {str(e)}'}
        
        
    def _process_initial_message(self, state: Dict[str, Any], user_id: int) -> Dict:
        """Process the initial user message and generate appropriate queries"""
        
        message_content = None
        for message in reversed(state["messages"]):
            if hasattr(message, "content") and "route_to" not in message.content:
                message_content = message.content
                break
        
        if not message_content:
            return {"messages": SystemMessage(content="No valid message found")}
        
        # Prepare state with user message and user_id
        state_with_message = {
            "messages": [("user", message_content)],
            "user_id": {"user_id": user_id}
        }
        
        # Get response from the runnable
        result = self.runnable.invoke(state_with_message)
        print(result)
        try:
            if hasattr(result, "content"):
                print("failing after this 1")
                # raw_result = result.content.strip()
                print("failing after this 2")
                
                print("failing after this 99")
                parsed_result = self.handle_message_result(result)
                print("parsed result: ",parsed_result)
                
                if parsed_result.get("function_name") == "run_database_query":
                    # Execute database query directly
                    query_result = run_database_query(parsed_result["arguments"])
                    print("query result : ",type(query_result))
                    start = query_result.find("'output': '") + len("'output': '")
                    # Find the index where the closing single quote appears
                    end = query_result.find("'", start)

                    # Extract the substring
                    portfolio_data = query_result[start:end]
                    # portfolio_data = output_content
                    print("portfolio data: ",portfolio_data)
                    
                    # formatted_portfolio_data= self.format_portfolio_data(portfolio_data)

                    if portfolio_data:
                        # Get analysis results
                        print("inside if")
                        stock_state_with_message = {"messages": [("portfolio data", portfolio_data)],}
                        print("stock state:",stock_state_with_message)
                        analysis_output=self.runnable2.invoke(stock_state_with_message)
                        print((analysis_output))
                        
                        #Trying to get the symbols from the anaylysis output inside List[Dict]
                        symbols = []
                        seen = set()
                        for tool_call in analysis_output.tool_calls:
                            symbol = tool_call['args'].get('symbol')
                            # Add a print statement to debug
                            print(f"Current tool call: {tool_call['name']}, Args: {tool_call['args']}")
                            if symbol and symbol not in seen:
                                symbols.append(symbol)
                                seen.add(symbol)

                        print(f"Final symbols list: {symbols}")
                        
                        
                        
                        analysis_results = self._analyze_portfolio(symbols)
                        # print("Analysis Results",analysis_results)
                        # Compile final analysis
                        final_analysis = self.format_analysis_data(analysis_results,portfolio_data)
                        
                        return {"messages": SystemMessage(content=final_analysis)}    
            
        except json.JSONDecodeError as e:
            return {"messages": SystemMessage(content=f"Error processing request: {e}")}
            
        return {"messages": result}
    
     
    def _analyze_portfolio(self, symbols: List) -> List[Dict]:
        """Analyze portfolio data using stock tools"""
        analysis_results = []
        
        for symbol in symbols:
            print("symbol inside analysis", symbol)
            
            # Fetch current prices
            try:
                prices = fetch_stock_prices(symbol)
                # print("Prices: ", prices)
                analysis_results.append({"type": "prices", "data": prices})
            except Exception as e:
                print(f"Error fetching prices for {symbol}: {str(e)}")
                analysis_results.append({"type": "prices", "data": f"Error: {str(e)}"})
            
            # Get company profile
            try:
                profile = get_company_profile(symbol)
                # print("profile: ", profile)
                analysis_results.append({"type": "profile", "data": profile})
            except Exception as e:
                print(f"Error fetching profile for {symbol}: {str(e)}")
                analysis_results.append({"type": "profile", "data": f"Error: {str(e)}"})
            
        
            try:
                financials = get_basic_financials(symbol)
                # print("financials: ", financials)  # Fixed the print label from "profile" to "financials"
                analysis_results.append({"type": "financials", "data": financials})
            except Exception as e:
                print(f"Error fetching financials for {symbol}: {str(e)}")
                analysis_results.append({"type": "financials", "data": f"Error: {str(e)}"})
            
            # Get recommendations
            try:
                recommendations = get_recommendation_trends(symbol)
                # print("recommendations: ", recommendations)  # Fixed the print label from "profile" to "recommendations"
                analysis_results.append({"type": "recommendations", "data": recommendations})
            except Exception as e:
                print(f"Error fetching recommendations for {symbol}: {str(e)}")
                analysis_results.append({"type": "recommendations", "data": f"Error: {str(e)}"})
        
        return analysis_results
    
    
    def format_analysis_data(self, results: List[Dict], portfolio_details) -> str:
        """
        Simple function to format portfolio data in a readable way.
        Takes list of dictionaries containing stock data and returns formatted string.
        """
        formatted_output = ["Portfolio Data Summary\n"]
        
        # Process each result
        for result in results:
            data_type = result.get('type', 'unknown')
            data = result.get('data', '')
            
            # Format based on data type
            if data_type == 'profile':
                formatted_output.append("Company Profile:")
                if ': ' in data:
                    data = data.split(': ', 1)[1]
                formatted_output.append(f"{data}\n")
                
            elif data_type == 'prices':
                formatted_output.append("Price Information:")
                if '$' in data:
                    price_data = data.split('$', 1)[1]
                    print("Purchase Price: ", price_data)
                    formatted_output.append(f"{price_data}\n")
                    
            elif data_type == 'news':
                formatted_output.append("Latest News:")
                if 'news: ' in data:
                    news_data = data.split('news: ', 1)[1]
                    formatted_output.append(f"{news_data}\n")
                    
            elif data_type == 'financials':
                formatted_output.append("Financial Information:")
                if ': ' in data:
                    financial_data = data.split(': ', 1)[1]
                    formatted_output.append(f"{financial_data}\n")
                    
            elif data_type == 'recommendations':
                formatted_output.append("Analyst Recommendations:")
                if '$' in data:
                    rec_data = data.split('$', 1)[1]
                    formatted_output.append(f"{rec_data}\n")

        # First join the formatted output into a single string
        compiled_output = "\n".join(formatted_output)
        
        # Create the LLM and prompt
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=OPENAI_API_KEY
        )
        
        # Create the chain
        response_formatter_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a stock analyst expert. Analyze the user portfolio details that you will receive and compare them against how the stock is performing, then provide an appropriate response. Below is an example.
            
            User Portfolio Details: {portfolio}
            Actual Stock Details: {stock_details}
            
            Make sure you analyze the portfolio details with comparison to the actual stock details and come up with an analysis report.
            
            Here's a sample response template for you:
            
            Stock Analysis - BCOMF (B COMMUNICATIONS LTD)

                Purchase Price of User: $120.00 | Current Price of Stock: $130.50 (+8.75%)
                Total Investment: $1,200 | Current Value: $1,305 (+$105)
                Market Comparison: Outperformed S&P 500 by +3.55%
                📊 Company Insights:
                ✅ Strong Q4 earnings | ✅ Revenue growth (+8% YoY)
                ⚠️ Regulatory risks in telecom sector

                🔍 Analyst Sentiment: 2 BUY | 1 HOLD | 0 SELL

                📌 Recommendation: Hold for further growth 📈 Sell partially to secure gains 💰 Monitor regulatory changes ⚠️
            """),
            ("human", "{stock_details}")  # Placeholder for stock details
        ])
        
        # Create the input dictionary for the prompt
        input_data = {
            "stock_details": compiled_output,
            "portfolio": portfolio_details
        }
        
        # Format the prompt with the input dictionary
        formatted_prompt = response_formatter_prompt.format(**input_data)
        
        # Invoke the LLM with the formatted prompt
        llm_response = llm.invoke(formatted_prompt)
        
        # Extract the content from the AIMessage
        if hasattr(llm_response, "content"):
            response_content = llm_response.content
            print("LLM Response:", response_content)
            return response_content
        else:
            print("Unexpected Response Format:", llm_response)
            return "Unexpected response format."
  
