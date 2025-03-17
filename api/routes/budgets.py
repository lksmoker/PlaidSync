from flask import Blueprint, request, jsonify
from supabase_client import supabase

budgets_blueprint = Blueprint("budgets", __name__)

@budgets_blueprint.route("/budgets", methods=["GET"])
def get_budgets():
    """Fetch budgeted amounts for a given month and year, including subcategories."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Month and year are required parameters"}), 400

        # ✅ Fetch budget items for the selected month & year
        response = (
            supabase.table("budget_items")
            .select("amount, category_id, subcategory_id, categories(name, parent_id), subcategories(name)")
            .eq("month", month)
            .eq("year", year)
            .execute()
        )

        if response.data:
            budget_totals = {}

            for budget in response.data:
                main_category_id = budget.get("category_id")
                subcategory_id = budget.get("subcategory_id")

                main_category_name = budget.get("categories", {}).get("name", "Uncategorized")
                subcategory_name = budget.get("subcategories", {}).get("name")

                # ✅ Format category key (Main > Sub if applicable)
                category_key = f"{main_category_name} > {subcategory_name}" if subcategory_name else main_category_name

                if category_key not in budget_totals:
                    budget_totals[category_key] = {
                        "category_name": category_key,
                        "total_budgeted": 0
                    }

                budget_totals[category_key]["total_budgeted"] += budget["amount"]

            return jsonify({"budgets": list(budget_totals.values())}), 200

        return jsonify({"budgets": []}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500