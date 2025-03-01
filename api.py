from flask import Flask, jsonify, request, render_template
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

# Example route to get all categories (replace SQLite queries with Supabase queries)
@app.route('/categories', methods=['GET'])
def get_categories():
    categories = supabase.table('categories').select('*').execute()
    return jsonify(categories.data)

# Example route to get all transactions (replace SQLite queries with Supabase queries)
@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = supabase.table('transactions').select('*').execute()
    return jsonify(transactions.data)

# Example route to add a new category (replace SQLite queries with Supabase queries)
@app.route('/categories', methods=['POST'])
def add_category():
    data = request.json
    category = supabase.table('categories').insert({
        'name': data['name'],
        'parent_id': data.get('parent_id', None)
    }).execute()

    return jsonify(category.data), 201

# Example route to update a category (replace SQLite queries with Supabase queries)
@app.route('/categories/<int:id>', methods=['PUT'])
def update_category(id):
    data = request.json
    category = supabase.table('categories').update({
        'name': data['name'],
        'parent_id': data.get('parent_id', None)
    }).eq('id', id).execute()

    return jsonify(category.data)

# Example route to delete a category (replace SQLite queries with Supabase queries)
@app.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    response = supabase.table('categories').delete().eq('id', id).execute()
    return jsonify(response.data), 204

# Start the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
