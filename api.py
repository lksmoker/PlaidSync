from flask import Flask, jsonify
from flask_cors import CORS
from get_transactions import get_unprocessed_transactions

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["GET"])
def home():
    return """
    API is running. Available endpoints:
    - GET /unprocessed-transactions
    
    Access /unprocessed-transactions to see the transaction data.
    """

@app.route("/unprocessed-transactions", methods=["GET"])
def unprocessed_transactions():
    """API endpoint to get unprocessed transactions."""
    transactions = get_unprocessed_transactions()

    formatted_transactions = [
        {
            "transaction_id": tx[0],
            "date": tx[1],
            "name": tx[2],
            "amount": tx[3],
            "currency": tx[4],
            "pending": bool(tx[5])
        }
        for tx in transactions
    ]

    response = jsonify(formatted_transactions)
    response.headers['Content-Type'] = 'application/json'
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)