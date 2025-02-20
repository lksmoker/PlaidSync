
from flask import Flask, jsonify
from get_transactions import get_unprocessed_transactions

app = Flask(__name__)

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


print("🚀 Available Routes:")
print(app.url_map)

import os

if __name__ == "__main__":
        host = "0.0.0.0"
        port = 5000

        print("\n🚀 Available Routes:")
        print(app.url_map)

        # Try detecting Replit's public URL
        replit_url = os.getenv("REPLIT_APP_URL")
        if replit_url:
            print(f"🌍 Public API URL: {replit_url}/unprocessed-transactions")
        else:
            print(f"🛠 No public URL detected. Try accessing: http://127.0.0.1:{port}/unprocessed-transactions")

        app.run(debug=False, host=host, port=port)