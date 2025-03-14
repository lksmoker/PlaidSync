from flask import Blueprint, jsonify
from supabase import Client

accounts_blueprint = Blueprint("accounts", __name__)
supabase: Client = None  # This will be set in app.py and passed here

@accounts_blueprint.route("/accounts", methods=["GET"])
def get_accounts():
    """Fetch all accounts from Supabase."""
    try:
        response = supabase.table("accounts").select("*").execute()

        if response.data:
            accounts = [{"account_id": acc["account_id"], **acc} for acc in response.data]
            return jsonify(accounts), 200
        else:
            return jsonify({"message": "No accounts found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500