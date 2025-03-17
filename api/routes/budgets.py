from flask import Blueprint, jsonify, request
from supabase_client import supabase

budgets_blueprint = Blueprint("budgets", __name__)

@budgets_blueprint.route("/budgets", methods=["GET"])
def get_budgets():
    """Fetch budgeted amounts for the given month and year, grouped by main and subcategories."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Missing required parameters: month and year"}), 400

        query = """
            SELECT 
                c.id AS category_id,
                c.name AS category_name,
                c.parent_id,
                COALESCE(SUM(b.budgeted_amount), 0) AS total_budgeted,
                COALESCE(SUM(b.adjusted_amount), 0) AS total_adjusted
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.month = %s AND b.year = %s
            GROUP BY c.id, c.name, c.parent_id
            ORDER BY c.parent_id NULLS FIRST, c.id;
        """

        response = supabase.rpc("run_sql", {"sql": query, "params": [month, year]}).execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500