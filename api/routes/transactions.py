from flask import Blueprint, jsonify, request
from supabase_client import supabase

transactions_blueprint = Blueprint("transactions", __name__)

# ✅ Fetch ALL transactions
@transactions_blueprint.route("/transactions", methods=["GET"])
def get_transactions():
    """Fetch all transactions."""
    try:
        response = supabase.table("transactions").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Fetch UNPROCESSED Transactions
@transactions_blueprint.route("/unprocessed-transactions", methods=["GET"])
def get_unprocessed_transactions():
    """Fetch transactions that have NOT been categorized and are NOT ignored."""
    try:
        response = (
            supabase.table("transactions")
            .select("*")
            .is_("user_category_id", None)  # No category assigned
            .eq("is_ignore", False)  # Not ignored
            .execute()
        )

        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Fetch PROCESSED Transactions
@transactions_blueprint.route("/processed-transactions", methods=["GET"])
def get_processed_transactions():
    """Fetch transactions that HAVE been categorized OR are ignored."""
    try:
        response = (
            supabase.table("transactions")
            .select("*")
            .or_(
                "not.is(user_category_id, null),is_ignore.eq.true"  # Either categorized OR ignored
            )
            .execute()
        )

        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Add a NEW Transaction
@transactions_blueprint.route("/transactions", methods=["POST"])
def add_transaction():
    """Add a new transaction."""
    try:
        data = request.json
        response = supabase.table("transactions").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Update a Transaction
@transactions_blueprint.route("/transactions/<string:transaction_id>", methods=["PUT"])
def update_transaction(transaction_id):
    """Update an existing transaction."""
    try:
        data = request.json
        response = (
            supabase.table("transactions")
            .update(data)
            .eq("transaction_id", transaction_id)
            .execute()
        )
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Delete a Transaction
@transactions_blueprint.route("/transactions/<string:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id):
    """Delete a transaction."""
    try:
        response = (
            supabase.table("transactions")
            .delete()
            .eq("transaction_id", transaction_id)
            .execute()
        )
        return jsonify({"message": "Transaction deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_blueprint.route("/update-transactions", methods=["POST"])
def update_transactions():
    """Update multiple transactions at once."""
    try:
        data = request.json.get("transactions", [])

        if not data:
            return jsonify({"error": "No transactions provided"}), 400

        updates = []
        for txn in data:
            txn_id = txn["transaction_id"]
            category_id = txn.get("user_category_id")
            subcategory_id = txn.get("user_subcategory_id")

            updates.append(
                supabase.table("transactions")
                .update({"user_category_id": category_id, "user_subcategory_id": subcategory_id})
                .eq("transaction_id", txn_id)
            )

        # Execute all updates in bulk
        for update in updates:
            update.execute()

        return jsonify({"success": True, "updated": len(updates)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
