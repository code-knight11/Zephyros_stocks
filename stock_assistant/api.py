# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import uuid
from langchain_openai import ChatOpenAI
from config.settings import OPENAI_API_KEY 
from tools.stock_tools import fetch_stock_prices, get_company_profile, search_results, get_company_news, get_basic_financials, get_recommendation_trends
from tools.portfolio_tools import run_database_query
from prompts.stock_prompts import stock_assistant_prompt
from prompts.stock_analyzer_prompt import stock_analyzer_prompt
from prompts.portfolio_analysis_prompt import portfolio_analysis_prompt
from utility_stock.graph_builder import build_graph
from models import state
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_userdata_connection():
    # Replace with your actual connection parameters.
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            # password='',
            database='zephyros_userdata'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"DB connection error: {err}")
        return None


# Initialize tools and LLM
stock_tools = [fetch_stock_prices, get_company_profile, search_results, get_company_news, get_basic_financials, get_recommendation_trends]
portfolio_tools=[run_database_query,fetch_stock_prices, get_company_profile, search_results, get_company_news, get_basic_financials, get_recommendation_trends]

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.4
)

# Initialize assistants
stock_assistant_runnable = stock_assistant_prompt | llm.bind_tools(stock_tools)
portfolio_assistant_runnable = portfolio_analysis_prompt | llm.bind_tools(portfolio_tools)
# portfolio_assistant_runnable = portfolio_analysis_prompt
stock_analyzer_runnable= stock_analyzer_prompt | llm.bind_tools(stock_tools)

# Build graph
builder = build_graph(llm,portfolio_tools, stock_tools, stock_assistant_runnable, portfolio_assistant_runnable,stock_analyzer_runnable)
graph = builder.compile()

# Store chat histories
chat_histories = {}

def save_chat_history(history):
    conn = get_userdata_connection()
    if conn is None:
        print("DB connection failed when saving chat history.")
        return
    cursor = conn.cursor()
    try:
        for msg in history:
            query = """
                INSERT INTO chat_history (thread_id, user_id, role, content)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (msg.get("thread_id", ""), msg["user_id"], msg["role"], msg["content"]))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Error saving chat history: ", e)
    finally:
        cursor.close()
        conn.close()
        
def create_conversation(thread_id, user_id):
    """
    Creates a new conversation entry with a name like "Conversation 1", "Conversation 2", etc.
    """
    conn = get_userdata_connection()
    if conn is None:
        print("DB connection failed when creating conversation.")
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        # Count the existing conversations for this user
        cursor.execute("SELECT COUNT(*) as count FROM conversations WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        conversation_number = result['count'] + 1
        conversation_name = f"Conversation {conversation_number}"
        # Insert the new conversation into the table
        cursor.execute(
            "INSERT INTO conversations (thread_id, user_id, conversation_name) VALUES (%s, %s, %s)",
            (thread_id, user_id, conversation_name)
        )
        conn.commit()
        return conversation_name
    except Exception as e:
        conn.rollback()
        print("Error creating conversation: ", e)
        return None
    finally:
        cursor.close()
        conn.close()
         
async def process_message(message, thread_id, user_id):
    responses = []
    context = {
        'user_id': user_id,
        'thread_id': thread_id
    }
    
    async for event in graph.astream({
        'messages': [('user', message)],
        'context': context
    }):
        for value in event.values():
            if isinstance(value['messages'], list):
                for msg in value['messages']:
                    if isinstance(msg, dict) or (hasattr(msg, 'content') and 'route_to' in str(msg.content)):
                        continue
                    
                    if hasattr(msg, 'content'):
                        # Check if this is a RAG response with sources
                        if hasattr(msg, 'additional_kwargs') and 'sources' in msg.additional_kwargs:
                            responses.append({
                                "role": "rag_assistant",
                                "content": msg.content,
                                "sources": msg.additional_kwargs['sources'],
                                "user_id": user_id,
                                "thread_id": thread_id
                            })
                        else:
                            responses.append({
                                "role": "assistant1",
                                "content": msg.content,
                                "user_id": user_id,
                                "thread_id": thread_id
                            })
                    elif hasattr(msg, 'name'):
                        responses.append({
                            "role": "tool", 
                            "content": f"Using tool: {msg.name}",
                            "user_id": user_id,
                            "thread_id": thread_id
                        })
            else:
                msg = value['messages']
                if hasattr(msg, 'content'):
                    # Check if this is a RAG response with sources
                    if hasattr(msg, 'additional_kwargs') and 'sources' in msg.additional_kwargs:
                        responses.append({
                            "role": "rag_assistant",
                            "content": msg.content,
                            "sources": msg.additional_kwargs['sources'],
                            "user_id": user_id,
                            "thread_id": thread_id
                        })
                    elif 'route_to' not in str(msg.content):
                        responses.append({
                            "role": "assistant2",
                            "content": msg.content,
                            "user_id": user_id,
                            "thread_id": thread_id
                        })
    if thread_id not in chat_histories:
        chat_histories[thread_id] = []
    
    chat_histories[thread_id].extend([
        {"role": "user", "content": message, "user_id": user_id, "thread_id": thread_id},
        *responses
    ])
    return responses

@app.route('/api/chat/<user_id>', methods=['POST'])
def chat(user_id):
    print("Received POST /api/chat/{}".format(user_id))
    data = request.json
    message = data.get('message')
    # Generate new thread_id if not provided
    thread_id = data.get('thread_id') or str(uuid.uuid4())
    print("Received thread_id:", thread_id)
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # If thread_id is new, create a conversation entry.
    if data.get('thread_id') is None:
        conv_name = create_conversation(thread_id, user_id)
        print(f"Created new conversation: {conv_name}")
    
    try:
        responses = asyncio.run(process_message(message, thread_id, user_id))
        
        # Save the conversation (user message and responses) to the database
        history_to_save = [
            {"thread_id": thread_id, "user_id": user_id, "role": "user", "content": message},
            *responses
        ]
        save_chat_history(history_to_save)
        
        return jsonify({
            "user_id": user_id,
            "thread_id": thread_id,
            "responses": responses
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
    
@app.route('/api/chathistory/<int:user_id>', methods=['GET'])
def get_chat_history(user_id):
    conn = get_userdata_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT id, thread_id, user_id, role, content, timestamp 
            FROM chat_history 
            WHERE user_id = %s 
            ORDER BY timestamp ASC
        """
        cursor.execute(query, (user_id,))
        history = cursor.fetchall()
        return jsonify({"history": history}), 200
    except mysql.connector.Error as err:
        print("Database error:", err)
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    """
    Retrieve all conversations (threads) for a given user along with conversation names.
    """
    conn = get_userdata_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT thread_id, conversation_name, created_at
            FROM conversations
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, (user_id,))
        conversations = cursor.fetchall()
        return jsonify({"conversations": conversations}), 200
    except mysql.connector.Error as err:
        print("Database error:", err)
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.route('/api/thread/<thread_id>', methods=['GET'])
def get_thread_messages(thread_id):
    """
    Retrieve all chat messages for a specific thread_id.
    Messages are ordered by timestamp to maintain conversation flow.
    """
    conn = get_userdata_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # First verify if the thread exists
        cursor.execute(
            "SELECT * FROM conversations WHERE thread_id = %s",
            (thread_id,)
        )
        conversation = cursor.fetchone()
        
        if not conversation:
            return jsonify({"error": "Thread not found"}), 404

        # Get all messages for this thread
        query = """
            SELECT 
                id,
                thread_id,
                user_id,
                role,
                content,
                timestamp
            FROM chat_history 
            WHERE thread_id = %s 
            ORDER BY timestamp ASC
        """
        cursor.execute(query, (thread_id,))
        messages = cursor.fetchall()

        # Format the response
        response = {
            "thread_id": thread_id,
            "conversation_name": conversation["conversation_name"],
            "created_at": conversation["created_at"],
            "messages": messages
        }

        return jsonify(response), 200

    except mysql.connector.Error as err:
        print("Database error:", err)
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/new_conversation/<user_id>', methods=['POST'])
def new_conversation(user_id):
    # Generate a new thread id
    new_thread_id = str(uuid.uuid4())
    
    # Create a new conversation entry using your existing helper.
    conv_name = create_conversation(new_thread_id, user_id)
    if conv_name is None:
        return jsonify({"error": "Could not create new conversation"}), 500

    # Optionally, clear any in-memory history if needed.
    if new_thread_id in chat_histories:
        del chat_histories[new_thread_id]

    return jsonify({
        "thread_id": new_thread_id,
        "conversation_name": conv_name
    }), 201
        
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Test successful"}), 200


if __name__ == '__main__':
    app.run(debug=True)
