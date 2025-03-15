from flask import Blueprint, jsonify, request
from supabase_client import supabase  # ✅ Import shared Supabase client

accounts_blueprint = Blueprint("accounts", __name__)

@accounts_blueprint.route("/accounts", methods=["GET"])
def get_accounts():
    """Fetch all accounts."""
    if supabase is None:
        return jsonify({"error": "Supabase not initialized"}), 500

    try:
        response = supabase.table("accounts").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@accounts_blueprint.route("/accounts", methods=["POST"])
def add_account():
    """Add a new account."""
    try:
        data = request.json
        response = supabase.table("accounts").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@accounts_blueprint.route("/accounts/<int:id>", methods=["PUT"])
def update_account(id):
    """Update an account."""
    try:
        data = request.json
        response = supabase.table("accounts").update(data).eq("id", id).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@accounts_blueprint.route("/accounts/<int:id>", methods=["DELETE"])
def delete_account(id):
    """Delete an account."""
    try:
        response = supabase.table("accounts").delete().eq("id", id).execute()
        return jsonify(response.data), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500