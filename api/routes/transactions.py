from flask import Blueprint, jsonify, request
from supabase_client import supabase
from utils.logger import log_message  # ✅ Import the logger utility

transactions_blueprint = Blueprint("transactions", __name__)

# ✅ Fetch ALL transactions
@transactions_blueprint.route("/transactions", methods=["GET"])
def get_transactions():
    """Fetch all transactions."""
    try:
        response = supabase.table("transactions").select("*").execute()
        log_message("Fetched all transactions successfully", "INFO", "Backend", "Transactions Route")
        return jsonify(response.data), 200
    except Exception as e:
        log_message(f"Error fetching transactions: {str(e)}", "ERROR", "Backend", "Transactions Route")
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
            .eq("is_ignored", False)  # Not ignored
            .execute()
        )
        log_message("Fetched unprocessed transactions successfully", "INFO", "Backend", "Transactions Route")
        return jsonify(response.data), 200
    except Exception as e:
        log_message(f"Error fetching unprocessed transactions: {str(e)}", "ERROR", "Backend", "Transactions Route")
        return jsonify({"error": str(e)}), 500

# ✅ Fetch PROCESSED Transactions
@transactions_blueprint.route("/processed-transactions", methods=["GET"])
def get_processed_transactions():
    """Fetch transactions that have been categorized or ignored."""
    try:
        response = (
            supabase.table("transactions")
            .select("*")
            .or_(
                "not.is.user_category_id.null,is_ignored.eq.true"
            )
            .execute()
        )
        log_message("Fetched processed transactions successfully", "INFO", "Backend", "Transactions Route")
        return jsonify(response.data), 200
    except Exception as e:
        log_message(f"Error fetching processed transactions: {str(e)}", "ERROR", "Backend", "Transactions Route")
        return jsonify({"error": str(e)}), 500


# ✅ Add a NEW Transaction
@transactions_blueprint.route("/transactions", methods=["POST"])
def add_transaction():
    """Add a new transaction."""
    try:
        data = request.json
        response = supabase.table("transactions").insert(data).execute()
        log_message(f"Added new transaction: {data}", "INFO", "Backend", "Transactions Route")
        return jsonify(response.data), 201
    except Exception as e:
        log_message(f"Error adding transaction: {str(e)}", "ERROR", "Backend", "Transactions Route")
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
        log_message(f"Updated transaction {transaction_id}: {data}", "INFO", "Backend", "Transactions Route")
        return jsonify(response.data), 200
    except Exception as e:
        log_message(f"Error updating transaction {transaction_id}: {str(e)}", "ERROR", "Backend", "Transactions Route")
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
        log_message(f"Deleted transaction {transaction_id}", "INFO", "Backend", "Transactions Route")
        return jsonify({"message": "Transaction deleted successfully"}), 200
    except Exception as e:
        log_message(f"Error deleting transaction {transaction_id}: {str(e)}", "ERROR", "Backend", "Transactions Route")
        return jsonify({"error": str(e)}), 500

# ✅ Update Multiple Transactions
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

        log_message(f"Updated {len(updates)} transactions", "INFO", "Backend", "Transactions Route")
        return jsonify({"success": True, "updated": len(updates)}), 200
    except Exception as e:
        log_message(f"Error updating transactions: {str(e)}", "ERROR", "Backend", "Transactions Route")
        return jsonify({"error": str(e)}), 500

# ✅ Split Transaction
@transactions_blueprint.route("/split-transaction", methods=["POST"])
def split_transaction():
    """Splits a transaction into multiple sub-transactions, preserving account_id."""
    try:
        data = request.json
        original_transaction_id = data.get("transaction_id")
        splits = data.get("splits", [])

        # ✅ Step 1: Fetch the Original Transaction Data
        original_transaction = (
            supabase.table("transactions")
            .select("amount, account_id")  # Fetch account_id
            .eq("transaction_id", original_transaction_id)
            .single()
            .execute()
        )

        if not original_transaction.data:
            return jsonify({"error": "Original transaction not found"}), 404

        original_amount = original_transaction.data["amount"]
        account_id = original_transaction.data["account_id"]

        # ✅ Step 2: Validate Split Amounts
        split_total = sum(s["amount"] for s in splits)
        if round(split_total, 2) != round(original_amount, 2):
            return jsonify({"error": "Split amounts must total the original amount"}), 400

        # ✅ Step 3: Insert New Split Transactions
        new_transactions = []
        for i, split in enumerate(splits, start=1):
            new_transactions.append({
                "transaction_id": f"{original_transaction_id}-split-{i}",
                "date": split.get("date"),
                "name": split.get("name"),
                "amount": split["amount"],
                "account_id": account_id,  # ✅ Include account_id
                "user_category_id": split.get("user_category_id"),
                "user_subcategory_id": split.get("user_subcategory_id"),
                "is_ignored": False,  # New splits are not ignored
                "is_split": False  # These are not split transactions themselves
            })

        supabase.table("transactions").insert(new_transactions).execute()

        # ✅ Step 4: Mark Original Transaction as BOTH `is_ignored = TRUE` and `is_split = TRUE`
        supabase.table("transactions").update({
            "is_ignored": True,
            "is_split": True
        }).eq("transaction_id", original_transaction_id).execute()

        log_message(f"Split transaction {original_transaction_id} into {len(splits)} parts", "INFO", "Backend", "Transactions Route")
        return jsonify({"message": "Transaction split successfully"}), 200
    except Exception as e:
        log_message(f"Error splitting transaction {original_transaction_id}: {str(e)}", "ERROR", "Backend", "Transactions Route")
        return jsonify({"error": str(e)}), 500