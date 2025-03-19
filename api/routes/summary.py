from flask import Blueprint, jsonify, request
from supabase_client import supabase
from utils.logger import log_message  # ✅ Import the logger utility

summary_blueprint = Blueprint("summary", __name__)

from flask import Blueprint, jsonify, request
from supabase_client import supabase
from utils.logger import log_message

summary_blueprint = Blueprint("summary", __name__)

# ✅ Fetch Regular Summary
@summary_blueprint.route("/summary/regular", methods=["GET"])
def get_regular_summary():
    """Fetch spending summary for regular budgets."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Missing month or year parameters"}), 400

        response = (
            supabase.rpc("fetch_summary", {"month": month, "year": year})
            .filter("type", "eq", "regular")  # Only regular transactions
            .execute()
        )

        log_message("Fetched regular summary successfully", "INFO", "/summary/regular")
        return jsonify(response.data), 200

    except Exception as e:
        log_message(f"Error fetching regular summary: {str(e)}", "ERROR", "/summary/regular")
        return jsonify({"error": str(e)}), 500


# ✅ Fetch Reserve Summary
@summary_blueprint.route("/summary/reserve", methods=["GET"])
def get_reserve_summary():
    """Fetch spending summary for reserve budgets."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Missing month or year parameters"}), 400

        response = (
            supabase.rpc("fetch_summary", {"month": month, "year": year})
            .filter("type", "eq", "reserve")  # Only reserve transactions
            .execute()
        )

        log_message("Fetched reserve summary successfully", "INFO", "/summary/reserve")
        return jsonify(response.data), 200

    except Exception as e:
        log_message(f"Error fetching reserve summary: {str(e)}", "ERROR", "/summary/reserve")
        return jsonify({"error": str(e)}), 500

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