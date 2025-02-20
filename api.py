
from flask import Flask, jsonify, request
from flask_cors import CORS  
import sqlite3
from werkzeug.serving import WSGIRequestHandler
import ssl

# Create Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE = "transactions_dev.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "GET /unprocessed-transactions": "Get all unprocessed transactions",
            "GET /transactions": "Get all transactions",
            "GET /accounts": "Get all accounts"
        }
    })

@app.route('/unprocessed-transactions')
def unprocessed_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT transaction_id, date, name, amount, iso_currency_code, pending
        FROM transactions 
        WHERE user_category_id IS NULL 
        ORDER BY date DESC
    """)
    
    transactions = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(tx) for tx in transactions])

@app.route('/transactions')
def all_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    
    transactions = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(tx) for tx in transactions])

@app.route('/accounts')
def accounts():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM accounts")
    
    accounts = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(acc) for acc in accounts])

if __name__ == '__main__':
    # Enable HTTP/1.1 support
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        ssl_context=None
    )
