from flask import Blueprint, request, jsonify
from supabase_client import supabase

summary_blueprint = Blueprint("summary", __name__)

@summary_blueprint.route("/summary", methods=["GET"])
def get_summary():
    """Retrieve a spending summary for a given month and year."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Month and year are required"}), 400

        response = (
            supabase.table("transactions")
            .select("user_category_id, categories(name), user_subcategory_id, subcategories(name), amount")
            .eq("EXTRACT(MONTH FROM date)", month)
            .eq("EXTRACT(YEAR FROM date)", year)
            .execute()
        )

        transactions = response.data

        # Aggregate spending per category
        summary = {}
        for tx in transactions:
            category_name = tx.get("subcategories", {}).get("name") or tx.get("categories", {}).get("name") or "Unknown"
            if category_name not in summary:
                summary[category_name] = 0
            summary[category_name] += tx["amount"]

        summary_list = [{"category_name": cat, "total_spent": total} for cat, total in summary.items()]

        return jsonify(summary_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500