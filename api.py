from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
import os

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")  # Fetch from environment variables
supabase_key = os.getenv("SUPABASE_KEY")  # Fetch from environment variables
supabase = create_client(supabase_url, supabase_key)

# Route to check server status
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "GET /categories": "Get all categories in a nested structure",
            "POST /categories": "Add a new category",
            "PUT /categories/<id>": "Update a category",
            "DELETE /categories/<id>": "Delete a category",
            "GET /processed-transactions": "Get all categorized or ignored transactions",
            "GET /unprocessed-transactions": "Get all unprocessed transactions",
            "GET /transactions": "Get all transactions",
            "POST /update-transactions": "Update or insert transactions",
            "POST /confirm-duplicate": "Mark a transaction as confirmed duplicate or not",
            "GET /duplicate-pairs": "Get potential duplicate transactions as pairs",
            "GET /duplicate-review": "Interactive page to review duplicate transactions",
            "GET /duplicate-transactions": "Get all potential duplicate transactions"
        }
    })

@app.route('/test-connection', methods=['GET'])
def test_connection():
    try:
        # Attempt a basic query to check the connection
        response = supabase.table('transactions').select('*').limit(1).execute()
        return jsonify({"message": "Connection successful", "data": response.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# Route to get all categories
@app.route('/categories', methods=['GET'])
def get_categories():
    categories = supabase.table('categories').select('*').execute()
    return jsonify(categories.data)

# Route to get all transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = supabase.table('transactions').select('*').order('date', desc=True).execute()
    return jsonify(transactions.data)

# Route to get all processed (categorized/ignored) transactions
@app.route('/processed-transactions', methods=['GET'])
def get_processed_transactions():
    transactions = supabase.table('transactions').select('*').eq('ignored', True).execute()
    return jsonify(transactions.data)

# Route to get all unprocessed transactions
@app.route('/unprocessed-transactions', methods=['GET'])
def get_unprocessed_transactions():
    transactions = supabase.table('transactions').select('*').is_('ignored', None).execute()
    return jsonify(transactions.data)

# Route to add a new category
@app.route('/categories', methods=['POST'])
def add_category():
    data = request.json
    category = supabase.table('categories').insert({
        'name': data['name'],
        'parent_id': data.get('parent_id', None)
    }).execute()
    return jsonify(category.data), 201

# Route to update a category
@app.route('/categories/<int:id>', methods=['PUT'])
def update_category(id):
    data = request.json
    category = supabase.table('categories').update({
        'name': data['name'],
        'parent_id': data.get('parent_id', None)
    }).eq('id', id).execute()
    return jsonify(category.data)

# Route to delete a category
@app.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    response = supabase.table('categories').delete().eq('id', id).execute()
    return jsonify(response.data), 204

# Route to confirm a transaction as a duplicate or not
@app.route('/confirm-duplicate', methods=['POST'])
def confirm_duplicate():
    data = request.json
    transaction_id = data['transaction_id']
    confirmed = data['confirmed']  # True or False
    transaction = supabase.table('transactions').update({
        'confirmed_duplicate': confirmed
    }).eq('transaction_id', transaction_id).execute()
    return jsonify(transaction.data)

# Route to update or insert transactions
@app.route('/update-transactions', methods=['POST'])
def update_transactions():
    data = request.json
    # Example logic: Iterate over incoming transactions and insert/update them
    for transaction_data in data:
        transaction = supabase.table('transactions').upsert(transaction_data).execute()
    return jsonify({"message": "Transactions updated"}), 200

# Route to get potential duplicate transaction pairs
@app.route('/duplicate-pairs', methods=['GET'])
def get_duplicate_pairs():
    # Example logic: You may need to adjust the logic based on how duplicates are tracked
    duplicates = supabase.table('transactions').select('*').eq('potential_duplicate', 1).execute()
    return jsonify(duplicates.data)

# Route to get all potential duplicate transactions
@app.route('/duplicate-transactions', methods=['GET'])
def get_duplicate_transactions():
    duplicates = supabase.table('transactions').select('*').eq('confirmed_duplicate', None).execute()
    return jsonify(duplicates.data)

# Route to review duplicate transactions (interactive)
@app.route('/duplicate-review', methods=['GET'])
def duplicate_review():
    # This could be a placeholder for the interactive review page
    return jsonify({"message": "Review page for duplicates"}), 200

# Start the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
