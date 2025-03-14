from flask import Blueprint, request, jsonify
from supabase_client import supabase

transactions_blueprint = Blueprint('transactions', __name__)

@transactions_blueprint.route('/transactions', methods=['GET'])
def get_transactions():
    """Fetches all transactions."""
    try:
        transactions = supabase.table('transactions').select('*').order('date', desc=True).execute()
        return jsonify(transactions.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_blueprint.route('/transactions', methods=['POST'])
def insert_transaction():
    """Adds a new transaction."""
    try:
        data = request.json
        response = supabase.table('transactions').insert(data).execute()
        return jsonify({"message": "Transaction added", "data": response.data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500