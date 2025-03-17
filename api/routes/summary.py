from flask import Blueprint, request, jsonify
from supabase_client import supabase

summary_blueprint = Blueprint("summary", __name__)

@summary_blueprint.route("/summary", methods=["GET"])
def get_summary():
    """Fetch the spending summary for a given month and year."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Month and year are required parameters"}), 400

        # ✅ Step 1: Fetch all transactions for the given month/year
        response = (
            supabase.table("transactions")
            .select("amount, user_category_id, categories(name, parent_id)")
            .gte("date", f"{year}-{month:02d}-01")
            .lt("date", f"{year}-{month + 1:02d}-01")
            .execute()
        )

        if response.data:
            category_totals = {}

            for txn in response.data:
                category_id = txn.get("user_category_id")
                category_name = txn.get("categories", {}).get("name", "Uncategorized")

                if category_id not in category_totals:
                    category_totals[category_id] = {
                        "category_name": category_name,
                        "total_spent": 0
                    }

                category_totals[category_id]["total_spent"] += txn["amount"]

            return jsonify({"summary": list(category_totals.values())}), 200

        return jsonify({"summary": []}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500