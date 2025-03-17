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

        query = """
        SELECT 
            t.user_category_id,
            COALESCE(subcat.name, maincat.name) AS category_name,  -- Use subcategory name if it exists
            SUM(t.amount) AS total_spent
        FROM transactions t
        LEFT JOIN categories maincat ON t.user_category_id = maincat.id
        LEFT JOIN categories subcat ON t.user_subcategory_id = subcat.id
        WHERE EXTRACT(MONTH FROM t.date) = %s AND EXTRACT(YEAR FROM t.date) = %s
        GROUP BY t.user_category_id, subcat.name, maincat.name
        ORDER BY total_spent DESC;
        """

        response = supabase.rpc("run_sql", {"sql": query, "params": [month, year]}).execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500