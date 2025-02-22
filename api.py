
from flask import Flask, jsonify, request
from flask_cors import CORS  
import sqlite3
from werkzeug.serving import WSGIRequestHandler
import ssl

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Database configuration
DATABASE = "transactions_dev.db"

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "GET /unprocessed-transactions": "Get all unprocessed transactions",
            "GET /transactions": "Get all transactions",
            "GET /accounts": "Get all accounts",
            "POST /update-transactions": "Update transaction categories and ignored status"
        }
    })

@app.route('/unprocessed-transactions')
def unprocessed_transactions():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE user_category_id IS NULL 
            ORDER BY date DESC
        """)
        transactions = [dict(row) for row in cursor.fetchall()]
        return jsonify(transactions)
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/transactions')
def get_transactions():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        transactions = [dict(row) for row in cursor.fetchall()]
        return jsonify(transactions)
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/accounts')
def get_accounts():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts")
        accounts = [dict(row) for row in cursor.fetchall()]
        return jsonify(accounts)
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/update-transactions', methods=['POST'])
def update_transactions():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transactions 
            SET user_category_id = ? 
            WHERE transaction_id = ?
        """, (data.get('category_id'), data.get('transaction_id')))
        conn.commit()
        return jsonify({"message": "Transaction updated successfully"})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
