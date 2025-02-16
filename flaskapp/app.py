from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import mysql.connector
from dateutil.relativedelta import relativedelta
from datetime import date

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


FINNHUB_TOKEN =
MARKET_DATA_API =
os.environ['CURL_CA_BUNDLE'] = 
ALPHA_VANTAGE_TOKEN = 

def get_userdata_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='',
            password='',
            database='zephyros_userdata'
        )
        print("Connection to database established successfully!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def get_marketdata_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='',
            password='',
            database='zephyros_marketdata' 
        )
        print("Connection to zephyros_marketdata established successfully!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to zephyros.market_data: {err}")
        return None


@app.route('/')
def index():
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    return "Routes printed to console"

# ---------- REGISTER ----------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    username = data.get('username')
    email = data.get('email')
    pswd = data.get('pswd')
    age = data.get('age')

    # check if all fields are there
    if not name or not username or not email or not pswd or not age:
        print(name, username, email, pswd, age)
        return jsonify({"message": "All fields are required!"}), 400

    conn = get_userdata_connection()
    cursor = conn.cursor()

    try:
        # Execute the insert query
        cursor.execute("INSERT INTO users (name, username, email, pswd, age) VALUES (%s, %s, %s, %s, %s)",
                       (name, username, email, pswd, age))
        conn.commit()  

        print(f"User {username} registered successfully in the database!")
        return jsonify({"message": f"User {username} registered successfully!"}), 201
    
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")  # Add detailed error logging
        return jsonify({"message": f"Error: {err}"}), 500
    
    finally:
        cursor.close()
        conn.close()
        
# ---------- LOGIN ----------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    pswd = data.get('pswd') 
    
    if not username or not pswd:
        return jsonify({"message": "Missing username or password!"}), 400

    conn = get_userdata_connection()
    cursor = conn.cursor()
    try:
        # Query the database to check if the username and password match
        cursor.execute("SELECT user_id, name, username, email, pswd, age FROM users WHERE username = %s AND pswd = %s", (username, pswd))
        user = cursor.fetchone()  # Assuming user is returned as a tuple

        if user:
            # Assuming user[0] is the user_id
            return jsonify({
                "message": f"User {username} logged in successfully!",
                "user_id": user[0]
            }), 200
        else:
            return jsonify({"message": "Invalid username or password!"}), 401

    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

# ---------- GET USER PORTFOLIO ----------
@app.route('/api/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    # Connect to the zephyros_userdata database.
    conn = get_userdata_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Fetch user details from zephyros_userdata.users table.
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            return jsonify({"message": "User not found"}), 404

        # 2. Fetch user's portfolio from zephyros_marketdata.user_portfolios,
        #    joined with zephyros_userdata.stocks (the correct database for stocks).
        portfolio_query = """
            SELECT 
                up.portfolio_id,
                up.user_id,
                up.stock_id,
                up.share_quantity,
                up.purchase_price,
                up.purchase_date,
                s.symbol,
                s.company_name,
                s.currency,
                s.display_symbol,
                s.figi,
                s.mic,
                s.share_class_figi,
                s.stock_type
            FROM zephyros_marketdata.user_portfolios AS up
            JOIN zephyros_userdata.stocks AS s ON up.stock_id = s.stock_id
            WHERE up.user_id = %s
        """
        cursor.execute(portfolio_query, (user_id,))
        portfolio = cursor.fetchall()

        return jsonify({
            "user": user_data,
            "portfolio": portfolio
        }), 200

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        conn.close()

# ---------- POST USER PORTFOLIO ----------
@app.route('/api/addportfolio', methods=['POST'])
def add_portfolio_item():
    print("Inside API ADDPORTFOLIO")
    data = request.get_json()

    # Ensure all required fields are present in the incoming JSON.
    required_fields = [
        'user_id', 
        'stock_id', 
        'symbol', 
        'company_name', 
        'share_quantity', 
        'purchase_price', 
        'purchase_date'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    # Extract data from the request.
    try:
        user_id = int(data['user_id'])
        stock_id = int(data['stock_id'])
        symbol = data['symbol']
        company_name = data['company_name']
        share_quantity = int(data['share_quantity'])
        purchase_price = float(data['purchase_price'])
        purchase_date = data['purchase_date']  # Expecting "YYYY-MM-DD" format.
    except Exception as e:
        return jsonify({"message": f"Invalid input: {str(e)}"}), 400

    # Connect to the zephyros_marketdata database.
    conn = get_marketdata_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = conn.cursor()
    try:
        # Validate that the stock exists in the parent table: zephyros_userdata.stocks.
        validation_query = "SELECT COUNT(*) FROM zephyros_userdata.stocks WHERE stock_id = %s"
        cursor.execute(validation_query, (stock_id,))
        result = cursor.fetchone()
        if result[0] == 0:
            return jsonify({"error": "Invalid stock_id. The referenced stock does not exist."}), 400

        # Insert the portfolio data into zephyros_marketdata.user_portfolios.
        query = """
            INSERT INTO user_portfolios (
                user_id, stock_id, symbol, company_name, share_quantity, purchase_price, purchase_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id, 
            stock_id, 
            symbol, 
            company_name, 
            share_quantity, 
            purchase_price, 
            purchase_date
        ))
        conn.commit()
        inserted_id = cursor.lastrowid

        return jsonify({
            "portfolio_id": inserted_id,
            "user_id": user_id,
            "stock_id": stock_id,
            "symbol": symbol,
            "company_name": company_name,
            "share_quantity": share_quantity,
            "purchase_price": purchase_price,
            "purchase_date": purchase_date
        }), 201

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()
        
# ----------- GET ALL STOCKS ----------
@app.route('/api/getallstocks', methods=['GET'])
def get_all_stocks():
    # Connect to the zephyros_marketdata database.
    conn = get_userdata_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed"}), 500

    # Use a dictionary cursor to return rows as dictionaries.
    cursor = conn.cursor(dictionary=True)
    try:
        # Query to fetch all stocks.
        query = "SELECT * FROM stocks"
        cursor.execute(query)
        stocks = cursor.fetchall()
        
        # Return the stocks as JSON.
        return jsonify(stocks), 200

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        conn.close()

# ---------- HISTORICAL DATA ----------
@app.route('/api/historical/<resolution>/<symbol>', methods=['GET'])
def get_historical_data(resolution, symbol):
    today = date.today()  
    from_date = today - relativedelta(years=1) + relativedelta(days=1)
    to_date = today

    from_date_str = from_date.strftime("%Y-%m-%d")
    to_date_str = to_date.strftime("%Y-%m-%d")
    
    url = (
        f"https://api.marketdata.app/v1/stocks/candles/"
        f"{resolution}/{symbol.upper()}/?from={from_date_str}&to={to_date_str}&token={MARKET_DATA_API}"
    )
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        data = response.json()
        return jsonify(data), 200
    except requests.RequestException as e:
        print(f"Error fetching historical data: {e}")
        return jsonify({
            "error": "Error fetching historical data from MarketData API",
            "message": str(e)
        }), 500
                
# ---------- STOCK QUOTE ----------
@app.route('/api/quote/<symbol>', methods=['GET'])
def get_stock_quote(symbol):
    print(symbol)
    try:
        finnhub_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_TOKEN}"
        app.logger.info(f"Requesting Finnhub stock quote URL: {finnhub_url}")
        response = requests.get(finnhub_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return jsonify(data), 200
    except requests.RequestException as e:
        app.logger.error(f"Error fetching stock quote for {symbol}: {e}")
        return jsonify({
            "error": "Error fetching stock quote",
            "message": str(e)
        }), 500
    except Exception as e:
        app.logger.error(f"Unhandled exception for {symbol}: {e}")
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e)
        }), 500
        
# ---------- COMPANY PROFILE ----------
@app.route('/api/company/<symbol>', methods=['GET'])
def get_company_profile(symbol):
    try:
        finnhub_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_TOKEN}"
        app.logger.info(f"Requesting Finnhub company profile URL: {finnhub_url}")
        response = requests.get(finnhub_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return jsonify(data), 200
    except requests.RequestException as e:
        app.logger.error(f"Error fetching company profile for {symbol}: {e}")
        return jsonify({
            "error": "Error fetching company profile",
            "message": str(e)
        }), 500
    except Exception as e:
        app.logger.error(f"Unhandled exception for company profile {symbol}: {e}")
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e)
        }), 500
        
        
@app.route('/api/stock-symbol')
def stock_symbol():
    try:
        # Build the Finnhub URL for stock symbols.
        finnhub_url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_TOKEN}"
        app.logger.info(f"Requesting Finnhub URL for Company Details: {finnhub_url}")

        response = requests.get(finnhub_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return jsonify(data), 200
    
    except requests.RequestException as e:
        app.logger.error(f"RequestException in /api/stock-symbol: {e}")
        return jsonify({
            "error": "Error fetching stock symbols from Finnhub",
            "message": str(e)
        }), 500

    except Exception as e:
        app.logger.error(f"Unhandled exception in /api/stock-symbol: {e}")
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e)
        }), 500

# ---------- SEARCH RESULTS ----------
@app.route('/api/search')
def search():
    try:
        query = request.args.get("query", "").strip()
        print(query)
        if not query:
            return jsonify({"result": [], "count": 0}), 200

        finnhub_url = f"https://finnhub.io/api/v1/search?q={query}&exchange=US&token={FINNHUB_TOKEN}"
        app.logger.info(f"Requesting Finnhub URL: {finnhub_url}")

        response = requests.get(finnhub_url, timeout=5)
        response.raise_for_status()

        data = response.json()
        return jsonify(data), 200

    except requests.RequestException as e:
        return jsonify({
            "error": "Error fetching data from Finnhub",
            "message": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e)
        }), 500
        


if __name__ == "__main__":
    app.run(debug=True, port=5002)
