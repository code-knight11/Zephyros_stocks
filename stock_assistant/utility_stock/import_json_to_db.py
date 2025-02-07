import json
import mysql.connector
from tqdm import tqdm

# Database connection configuration
DB_CONFIG = {
    "host": "https://urban-broccoli-65xgp6499xphx6g5-3306.app.github.dev",  # Change from 'localhost' to '127.0.0.1'
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "zephyros_marketdata"
}


# Path to the JSON file
JSON_FILE_PATH = "/workspaces/Zephyros_stocks/stock_assistant/utility_stock/market_data.json"

# Connect to MySQL
def get_db_connection():
    """Establish a database connection and return the connection object."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Successfully connected to the database!")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")
        exit(1)  # Stop execution if DB connection fails

# Check if the table exists
def validate_table_exists(cursor):
    """Verify that the 'stocks' table exists in the database."""
    cursor.execute("SHOW TABLES LIKE 'stocks'")
    result = cursor.fetchone()
    if not result:
        print("❌ Error: Table 'stocks' does not exist in the database.")
        exit(1)  # Stop execution if table is missing

# Function to insert data in batches
def insert_data_in_batches(data, batch_size=1000):
    """Insert JSON data into the 'stocks' table in batches."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Validate if the table exists
    validate_table_exists(cursor)

    insert_query = """
    INSERT INTO stocks (symbol, company_name, currency, display_symbol, figi, mic, share_class_figi, stock_type)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    batch = []
    for record in tqdm(data, desc="Inserting records", unit="rows"):
        batch.append((
            record.get("symbol", None),
            record.get("description", None),  # Mapping JSON "description" to company_name
            record.get("currency", None),
            record.get("displaySymbol", None),
            record.get("figi", None),
            record.get("mic", None),
            record.get("shareClassFIGI", None),
            record.get("type", None)
        ))

        if len(batch) >= batch_size:
            try:
                cursor.executemany(insert_query, batch)
                conn.commit()
                print(f"✅ Inserted {len(batch)} records successfully!")
            except mysql.connector.Error as err:
                print(f"❌ Database Insertion Error: {err}")
            batch.clear()

    if batch:
        try:
            cursor.executemany(insert_query, batch)
            conn.commit()
            print(f"✅ Inserted {len(batch)} final records successfully!")
        except mysql.connector.Error as err:
            print(f"❌ Database Insertion Error: {err}")

    cursor.close()
    conn.close()
    print("✅ Data import completed successfully!")

# Read the entire JSON array from the file and process
def process_large_json(file_path, batch_size=10000):
    """Read the entire JSON array and process it in batches."""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            # Load the entire JSON array into a Python list
            data = json.load(f)
            print(f"✅ Successfully loaded {len(data)} records from the JSON file.")
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding JSON file: {e}")
            exit(1)

        # Process and insert data in batches
        data_batch = []
        for i, record in enumerate(data):
            data_batch.append(record)

            # Insert the data in batches of batch_size
            if len(data_batch) >= batch_size:
                print(f"📌 Inserting batch of {batch_size} records...")
                insert_data_in_batches(data_batch)
                data_batch.clear()

        # Insert any remaining records
        if data_batch:
            print(f"📌 Inserting final batch of {len(data_batch)} records...")
            insert_data_in_batches(data_batch)

# Run the import process
if __name__ == "__main__":
    # Test database connection
    conn = get_db_connection()
    conn.close()

    # Start processing JSON
    process_large_json(JSON_FILE_PATH)
