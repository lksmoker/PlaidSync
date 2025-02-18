
from flask import Flask, jsonify
from get_transactions import get_unprocessed_transactions

app = Flask(__name__)


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
    return jsonify(formatted_transactions)


print("🚀 Available Routes:")
print(app.url_map)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
