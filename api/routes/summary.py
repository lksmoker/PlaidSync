from flask import Blueprint, jsonify, request
from supabase_client import supabase

summary_blueprint = Blueprint("summary", __name__)

@summary_blueprint.route("/summary", methods=["GET"])
def get_summary():
    """Fetch transaction summaries grouped by main and subcategories."""
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
                COALESCE(SUM(t.amount), 0) AS total_spent
            FROM transactions t
            LEFT JOIN categories c ON t.user_category_id = c.id
            WHERE EXTRACT(MONTH FROM t.date) = %s AND EXTRACT(YEAR FROM t.date) = %s
            GROUP BY c.id, c.name, c.parent_id
            ORDER BY c.parent_id NULLS FIRST, c.id;
        """

        response = supabase.rpc("run_sql", {"sql": query, "params": [month, year]}).execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500