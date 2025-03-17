from flask import Blueprint, request, jsonify
from supabase_client import supabase

budgets_blueprint = Blueprint("budgets", __name__)

@budgets_blueprint.route("/budgets", methods=["GET"])
def get_budgets():
    """Retrieve budgeted amounts for a given month and year."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Month and year are required"}), 400

        response = (
            supabase.table("budgets")
            .select("category_id, categories(name), subcategory_id, subcategories(name), budgeted_amount")
            .eq("month", month)
            .eq("year", year)
            .execute()
        )

        budgets = response.data

        # Aggregate budgets per category
        budget_summary = {}
        for b in budgets:
            category_name = b.get("subcategories", {}).get("name") or b.get("categories", {}).get("name") or "Unknown"
            if category_name not in budget_summary:
                budget_summary[category_name] = 0
            budget_summary[category_name] += b["budgeted_amount"]

        budget_list = [{"category_name": cat, "total_budgeted": total} for cat, total in budget_summary.items()]

        return jsonify(budget_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500