from flask import Blueprint, jsonify
from supabase import Client

accounts_blueprint = Blueprint("accounts", __name__)

@accounts_blueprint.route("/accounts", methods=["GET"])
def get_accounts():
    """Fetch all accounts from Supabase."""
    try:
        # ✅ Dynamically retrieve the Supabase instance
        supabase = getattr(accounts_blueprint, "supabase", None)

        if supabase is None:
            print("❌ Supabase client is missing in accounts.py!")
            return jsonify({"error": "Supabase client not initialized"}), 500

        print("🔍 Fetching accounts from Supabase...")
        response = supabase.table("accounts").select("*").execute()

        if response.data:
            accounts = [{"account_id": acc["account_id"], **acc} for acc in response.data]
            print(f"✅ {len(accounts)} accounts found.")
            return jsonify(accounts), 200
        else:
            print("⚠️ No accounts found in Supabase.")
            return jsonify({"message": "No accounts found"}), 404
    except Exception as e:
        print(f"❌ Error fetching accounts: {str(e)}")
        return jsonify({"error": str(e)}), 500
