from flask import Blueprint, request, jsonify
from supabase_client import supabase

budgets_blueprint = Blueprint("budgets", __name__)

@budgets_blueprint.route("/budgets", methods=["GET"])
def get_budgets():
    """Fetch budget data for a given month and year."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Month and year are required parameters"}), 400

        response = (
            supabase.table("budgets")
            .select("id, category_id, budgeted_amount, adjusted_amount, month, year, categories(name, parent_id)")
            .eq("month", month)
            .eq("year", year)
            .execute()
        )

        if response.data:
            # ✅ Separate into Regular & Reserve budgets
            regular_budgets = []
            reserve_budgets = []

            for item in response.data:
                category = item.get("categories", {})
                parent_id = category.get("parent_id")

                budget_entry = {
                    "id": item["id"],
                    "category_id": item["category_id"],
                    "category_name": category.get("name", "Unknown"),
                    "budgeted_amount": item["budgeted_amount"],
                    "adjusted_amount": item["adjusted_amount"],
                }

                if parent_id == 9:  # ✅ Reserve Category
                    reserve_budgets.append(budget_entry)
                else:  # ✅ Regular Category
                    regular_budgets.append(budget_entry)

            return jsonify({"regular_budgets": regular_budgets, "reserve_budgets": reserve_budgets}), 200

        return jsonify({"regular_budgets": [], "reserve_budgets": []}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500