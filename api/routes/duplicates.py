from flask import Blueprint, jsonify, request
from supabase import Client

duplicates_blueprint = Blueprint("duplicates", __name__)
supabase: Client = None  # This will be set in app.py and passed here

@duplicates_blueprint.route("/duplicate-pairs", methods=["GET"])
def get_duplicate_pairs():
    """Fetch potential duplicate transaction pairs."""
    try:
        duplicates = supabase.table("transactions").select("*").eq("potential_duplicate", True).execute()

        if not duplicates.data:
            return jsonify([]), 200

        pairs = []
        for i in range(0, len(duplicates.data), 2):
            if i + 1 < len(duplicates.data):
                pairs.append({
                    "date": duplicates.data[i]["date"],
                    "amount": duplicates.data[i]["amount"],
                    "account_id": duplicates.data[i].get("account_id", ""),
                    "transaction1": duplicates.data[i],
                    "transaction2": duplicates.data[i + 1],
                })

        return jsonify(pairs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@duplicates_blueprint.route("/duplicate-transactions", methods=["GET"])
def get_duplicate_transactions():
    """Fetch all potential duplicate transactions."""
    try:
        duplicates = supabase.table("transactions").select("*").eq("confirmed_duplicate", None).execute()
        return jsonify(duplicates.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@duplicates_blueprint.route("/confirm-duplicate", methods=["POST"])
def confirm_duplicate():
    """Confirm whether a transaction is a duplicate."""
    try:
        data = request.json
        if not data or "transaction_id" not in data or "is_duplicate" not in data:
            return jsonify({"error": "Missing required fields: transaction_id or is_duplicate"}), 400

        transaction_id = data["transaction_id"]
        is_duplicate = data["is_duplicate"]

        transaction = supabase.table("transactions").update({"confirmed_duplicate": is_duplicate}).eq("id", transaction_id).execute()
        return jsonify({"success": True, "data": transaction.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500