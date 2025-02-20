
from flask import Flask, jsonify, make_response
from flask_cors import CORS
from get_transactions import get_unprocessed_transactions

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.before_request
def before_request():
    """Ensure proper content type for API responses"""
    if request.path.startswith('/unprocessed-transactions'):
        return make_response().headers['Content-Type'] = 'application/json'

@app.route("/unprocessed-transactions", methods=["GET"])
def unprocessed_transactions():
    """API endpoint to get unprocessed transactions."""
    transactions = get_unprocessed_transactions()
    
    # Debugging: Print transactions to console
    print("🟢 Retrieved transactions:", transactions)
    
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
    
    return jsonify(formatted_transactions)

if __name__ == "__main__":
    print("\n🚀 Available Routes:")
    print(app.url_map)
    app.run(host='0.0.0.0', port=5000)
