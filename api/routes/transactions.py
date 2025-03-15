from flask import Blueprint, jsonify, request
from supabase_client import supabase

transactions_blueprint = Blueprint("transactions", __name__)


### ✅ Fetch **Unprocessed Transactions**
@transactions_blueprint.route("/unprocessed-transactions", methods=["GET"])
def get_unprocessed_transactions():
    """Fetch transactions that have NOT been categorized and are NOT ignored."""
    try:
        response = (
            supabase.table("transactions").select("*").is_(
                "user_category_id", None)  # No category assigned
            .eq("ignored", False)  # Not ignored
            .execute())

        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


### ✅ Fetch **Processed Transactions**              
@transactions_blueprint.route("/processed-transactions", methods=["GET"])
def get_processed_transactions():
    """Fetch transactions that are categorized OR ignored."""
    try:
        response = (
            supabase.table("transactions")
            .select("*")
            .or_("user_category_id.not.is.null,ignored.eq.true")  # ✅ Corrected syntax
            .execute()
        )

        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

### ✅ Fetch **ALL Transactions**
@transactions_blueprint.route("/transactions", methods=["GET"])
def get_all_transactions():
    """Fetch all transactions."""
    try:
        response = supabase.table("transactions").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


### ✅ Add a New Transaction (Manual Entry)
@transactions_blueprint.route("/transactions", methods=["POST"])
def add_transaction():
    """Add a new transaction."""
    try:
        data = request.json
        response = supabase.table("transactions").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


### ✅ Update a Transaction (Categorize, Ignore, Modify)
@transactions_blueprint.route("/transactions/<int:id>", methods=["PUT"])
def update_transaction(id):
    """Update an existing transaction."""
    try:
        data = request.json
        response = supabase.table("transactions").update(data).eq(
            "id", id).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


### ✅ Delete a Transaction
@transactions_blueprint.route("/transactions/<int:id>", methods=["DELETE"])
def delete_transaction(id):
    """Delete a transaction."""
    try:
        response = supabase.table("transactions").delete().eq("id",
                                                              id).execute()
        return jsonify(response.data), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500
