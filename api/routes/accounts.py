from flask import Blueprint, jsonify, request
from supabase_client import supabase  # ✅ Import shared Supabase client
from utils.logger import log_message  # ✅ Import the logger utility

accounts_blueprint = Blueprint("accounts", __name__)

@accounts_blueprint.route("/accounts", methods=["GET"])
def get_accounts():
    """Fetch all accounts."""
    if supabase is None:
        log_message("Supabase client not initialized", "ERROR", "Backend", "Accounts Route")
        return jsonify({"error": "Supabase not initialized"}), 500

    try:
        response = supabase.table("accounts").select("*").execute()
        log_message("Fetched all accounts successfully", "INFO", "Backend", "Accounts Route")
        return jsonify(response.data), 200
    except Exception as e:
        log_message(f"Error fetching accounts: {str(e)}", "ERROR", "Backend", "Accounts Route")
        return jsonify({"error": str(e)}), 500

@accounts_blueprint.route("/accounts", methods=["POST"])
def add_account():
    """Add a new account."""
    try:
        data = request.json
        response = supabase.table("accounts").insert(data).execute()
        log_message(f"Added new account: {data}", "INFO", "Backend", "Accounts Route")
        return jsonify(response.data), 201
    except Exception as e:
        log_message(f"Error adding account: {str(e)}", "ERROR", "Backend", "Accounts Route")
        return jsonify({"error": str(e)}), 500

@accounts_blueprint.route("/accounts/<int:id>", methods=["PUT"])
def update_account(id):
    """Update an account."""
    try:
        data = request.json
        response = supabase.table("accounts").update(data).eq("id", id).execute()
        log_message(f"Updated account {id}: {data}", "INFO", "Backend", "Accounts Route")
        return jsonify(response.data), 200
    except Exception as e:
        log_message(f"Error updating account {id}: {str(e)}", "ERROR", "Backend", "Accounts Route")
        return jsonify({"error": str(e)}), 500

@accounts_blueprint.route("/accounts/<int:id>", methods=["DELETE"])
def delete_account(id):
    """Delete an account."""
    try:
        response = supabase.table("accounts").delete().eq("id", id).execute()
        log_message(f"Deleted account {id}", "INFO", "Backend", "Accounts Route")
        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        log_message(f"Error deleting account {id}: {str(e)}", "ERROR", "Backend", "Accounts Route")
        return jsonify({"error": str(e)}), 500