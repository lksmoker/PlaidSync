from flask import Blueprint, jsonify, request
from supabase_client import supabase

transactions_blueprint = Blueprint("transactions", __name__)

@transactions_blueprint.route("/transactions", methods=["GET"])
def get_transactions():
    """Fetch all transactions."""
    try:
        response = supabase.table("transactions").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_blueprint.route("/transactions", methods=["POST"])
def add_transaction():
    """Add a new transaction."""
    try:
        data = request.json
        response = supabase.table("transactions").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_blueprint.route("/transactions/<int:id>", methods=["PUT"])
def update_transaction(id):
    """Update a transaction."""
    try:
        data = request.json
        response = supabase.table("transactions").update(data).eq("id", id).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_blueprint.route("/transactions/<int:id>", methods=["DELETE"])
def delete_transaction(id):
    """Delete a transaction."""
    try:
        response = supabase.table("transactions").delete().eq("id", id).execute()
        return jsonify(response.data), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500