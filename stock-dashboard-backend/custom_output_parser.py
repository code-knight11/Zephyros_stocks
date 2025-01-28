import json
 
class OutputParser:
    @staticmethod
    def parse(result):
        messages = result.get('messages', [])
       
        for message in messages:
            # Handle stock price tool
            if message.name == 'fetch_stock_price':
                return message.content
           
            # Handle company details tool
            elif message.name == 'get_company_details':
                content_str = message.content.split(": $", 1)[-1]
                content_data = json.loads(content_str.replace("'", '"'))
               
                return (
                    f"**Company Details:**\n"
                    f"- **Name:** {content_data.get('name')}\n"
                    f"- **Ticker:** {content_data.get('ticker')}\n"
                    f"- **Exchange:** {content_data.get('exchange')}\n"
                    f"- **Industry:** {content_data.get('finnhubIndustry')}\n"
                    f"- **Country:** {content_data.get('country')}\n"
                    f"- **Currency:** {content_data.get('currency')}\n"
                    f"- **Market Capitalization:** ${content_data.get('marketCapitalization', 0) * 1000000:,.0f}\n"
                    f"- **Shares Outstanding:** {content_data.get('shareOutstanding')}\n"
                    f"- **IPO Date:** {content_data.get('ipo')}\n"
                    f"- **Phone:** +1-{content_data.get('phone')}\n"
                    f"- **Website:** {content_data.get('weburl')}\n"
                    f"- **Logo URL:** {content_data.get('logo')}"
                )
       
        return "No information found"