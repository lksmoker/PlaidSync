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

        query = """
        SELECT 
            b.category_id,
            COALESCE(subcat.name, maincat.name) AS category_name,  -- Use subcategory name if available
            SUM(b.budgeted_amount) AS total_budgeted
        FROM budgets b
        LEFT JOIN categories maincat ON b.category_id = maincat.id
        LEFT JOIN categories subcat ON b.subcategory_id = subcat.id
        WHERE b.month = %s AND b.year = %s
        GROUP BY b.category_id, subcat.name, maincat.name
        ORDER BY total_budgeted DESC;
        """

        response = supabase.rpc("run_sql", {"sql": query, "params": [month, year]}).execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500