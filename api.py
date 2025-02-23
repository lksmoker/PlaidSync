from flask import Flask, jsonify, request
from flask_cors import CORS  
import sqlite3
from werkzeug.serving import WSGIRequestHandler

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
            "GET /accounts": "Get all accounts",
            "POST /update-transactions": "Update or insert transactions"
        }
    })

@app.route('/processed-transactions')
def processed_transactions():
    """Fetch all transactions that have been categorized or ignored."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transaction_id, date, name, amount, iso_currency_code, pending, user_category_id, ignored
        FROM transactions
        WHERE user_category_id IS NOT NULL OR ignored = 1
        ORDER BY date DESC
    """)

    transactions = cursor.fetchall()
    conn.close()

    return jsonify([dict(tx) for tx in transactions])

@app.route('/unprocessed-transactions')
def unprocessed_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transaction_id, date, name, amount, iso_currency_code, pending, user_category_id, ignored
        FROM transactions 
        WHERE user_category_id IS NULL AND ignored = 0
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

@app.route('/update-transactions', methods=['POST'])
def update_transactions():
    data = request.json
    transactions = data.get("transactions", [])

    print("🚀 Received Transactions for Update:", transactions)

    if not transactions:
        print("❌ No transactions received!")
        return jsonify({"success": False, "error": "No transactions provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for txn in transactions:
            txn.setdefault("ignored", 0)  # ✅ Default ignored = 0 if missing
            print(f"🔄 Processing transaction: {txn}")

            if "transaction_id" not in txn:
                print("❌ Missing transaction_id, skipping:", txn)
                continue

            # ✅ Check if the transaction already exists
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE transaction_id = ?", (txn["transaction_id"],))
            exists = cursor.fetchone()[0]

            if exists:
                print(f"✏️ Updating existing transaction in DB: {txn}")
                cursor.execute("""
                    UPDATE transactions
                    SET user_category_id = ?, ignored = ?
                    WHERE transaction_id = ?
                """, (txn.get("category", ""), txn["ignored"], txn["transaction_id"]))
            else:
                print(f"🆕 Inserting new manual transaction: {txn}")
                cursor.execute("""
                    INSERT INTO transactions (transaction_id, date, name, amount, iso_currency_code, pending, user_category_id, ignored)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (txn["transaction_id"], txn["date"], txn["name"], txn["amount"], txn["iso_currency_code"], txn["pending"], txn.get("category", ""), txn["ignored"]))

        conn.commit()
        conn.close()
        print("✅ Transactions successfully updated!")
        return jsonify({"success": True, "updated": len(transactions)})

    except Exception as e:
        print("🚨 Error updating transactions:", str(e))
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Enable HTTP/1.1 support
    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    # Run the app
    app.run(
        host='0.0.0.0',
        port=80,
        debug=False
    )