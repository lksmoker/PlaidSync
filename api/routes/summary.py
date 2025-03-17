from flask import Blueprint, jsonify, request
from supabase_client import supabase
from utils.logger import log_message  # ✅ Import the logger utility

summary_blueprint = Blueprint("summary", __name__)

@summary_blueprint.route("/summary", methods=["GET"])
def get_summary():
    """Fetch transaction summary for a given month and year."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            log_message("Missing month or year in summary request", "WARN", "Backend", "Summary Route")
            return jsonify({"error": "Month and year are required"}), 400

        # ✅ Fetch categorized transactions with main and subcategory names
        response = supabase.rpc("fetch_summary", {"month": month, "year": year}).execute()

        if response.data is None:
            log_message("No summary data found", "INFO", "Backend", "Summary Route")
            return jsonify([]), 200

        log_message(f"Fetched summary for {month}/{year}", "INFO", "Backend", "Summary Route")
        return jsonify(response.data), 200

    except Exception as e:
        log_message(f"Error fetching summary: {str(e)}", "ERROR", "Backend", "Summary Route")
        return jsonify({"error": str(e)}), 500