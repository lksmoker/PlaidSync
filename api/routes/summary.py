from flask import Blueprint, request, jsonify
from supabase_client import supabase

summary_blueprint = Blueprint("summary", __name__)

@summary_blueprint.route("/summary", methods=["GET"])
def get_summary():
    """Fetch the spending summary for a given month and year, including subcategories."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Month and year are required parameters"}), 400

        # ✅ Fetch transactions within the selected month & year
        response = (
            supabase.table("transactions")
            .select("amount, user_category_id, user_subcategory_id, categories(name, parent_id), subcategories(name)")
            .gte("date", f"{year}-{month:02d}-01")
            .lt("date", f"{year}-{month + 1:02d}-01")
            .execute()
        )

        if response.data:
            category_totals = {}

            for txn in response.data:
                main_category_id = txn.get("user_category_id")
                subcategory_id = txn.get("user_subcategory_id")

                main_category_name = txn.get("categories", {}).get("name", "Uncategorized")
                subcategory_name = txn.get("subcategories", {}).get("name")

                # ✅ Format category key (Main > Sub if applicable)
                category_key = f"{main_category_name} > {subcategory_name}" if subcategory_name else main_category_name

                if category_key not in category_totals:
                    category_totals[category_key] = {
                        "category_name": category_key,
                        "total_spent": 0
                    }

                category_totals[category_key]["total_spent"] += txn["amount"]

            return jsonify({"summary": list(category_totals.values())}), 200

        return jsonify({"summary": []}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500