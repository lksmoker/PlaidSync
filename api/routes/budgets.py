from flask import Blueprint, jsonify, request
from supabase_client import supabase
from utils.logger import log_message

budgets_blueprint = Blueprint("budgets", __name__)

# ✅ Fetch Regular Budgets 
@budgets_blueprint.route("/budgets/regular", methods=["GET"])
def get_regular_budgets():
    """Fetch regular budgets using the /categories/regular endpoint dynamically."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        # Fetch regular category IDs dynamically
        category_response = supabase.table("categories").select("id").neq("id", 9).execute()
        regular_category_ids = [cat["id"] for cat in category_response.data]

        response = (
            supabase.table("budgets")
            .select("*")
            .eq("month", month)
            .eq("year", year)
            .in_("category_id", regular_category_ids)  # Fetch budgets for regular categories
            .execute()
        )

        log_message(f"Fetched {len(response.data)} regular budgets", "INFO", "/budgets/regular")
        return jsonify(response.data), 200

    except Exception as e:
        log_message(f"Error fetching regular budgets: {str(e)}", "ERROR", "/budgets/regular")
        return jsonify({"error": str(e)}), 500

# ✅ Fetch Reserve Budgets

@budgets_blueprint.route("/budgets/reserve", methods=["GET"])
def get_reserve_budgets():
    """Fetch reserve budgets by joining with categories on parent_id = 9."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Missing month or year parameters"}), 400

        response = supabase.rpc("fetch_reserve_budgets", {"p_month": month, "p_year": year}).execute()

        # Check if response contains an error key before accessing it
        if hasattr(response, "error") and response.error:
            log_message(f"Error fetching reserve budgets: {response.error}", "ERROR", "/budgets/reserve")
            return jsonify({"error": response.error}), 500

        # Debug log to inspect response format
        log_message(f"Reserve Budgets Response: {response}", "DEBUG", "/budgets/reserve")

        # Extract the actual data
        reserve_budgets = response.data if hasattr(response, "data") else []

        log_message(f"Fetched {len(reserve_budgets)} reserve budgets", "INFO", "/budgets/reserve")
        return jsonify(reserve_budgets), 200

    except Exception as e:
        log_message(f"Unexpected error fetching reserve budgets: {str(e)}", "ERROR", "/budgets/reserve")
        return jsonify({"error": str(e)}), 500

# ✅ Get budgets for a given month & year
@budgets_blueprint.route("/budgets", methods=["GET"])
def get_budgets():
    """Fetch budgets for a given month and year."""
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Missing month or year parameters"}), 400

        response = (
            supabase.table("budgets")
            .select("*")
            .eq("month", month)
            .eq("year", year)
            .execute()
        )

        log_message("Fetched budgets successfully", "INFO", "/budgets")
        return jsonify(response.data), 200

    except Exception as e:
        log_message(f"Error fetching budgets: {str(e)}", "ERROR", "/budgets")
        return jsonify({"error": str(e)}), 500


# ✅ Set or Update a budget item
@budgets_blueprint.route("/budgets", methods=["POST"])
def set_budget():
    """Insert or update a budget entry."""
    try:
        data = request.json
        required_fields = ["month", "year", "category_id", "budgeted_amount"]

        # Ensure required fields are present
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Check if a budget entry exists for the given month, year, and category
        existing_budget = (
            supabase.table("budgets")
            .select("id")
            .eq("month", data["month"])
            .eq("year", data["year"])
            .eq("category_id", data["category_id"])
            .execute()
        )

        if existing_budget.data:
            # Update existing budget entry
            budget_id = existing_budget.data[0]["id"]
            response = (
                supabase.table("budgets")
                .update({"budgeted_amount": data["budgeted_amount"]})
                .eq("id", budget_id)
                .execute()
            )
            log_message(f"Updated budget ID {budget_id}", "INFO", "/budgets")
        else:
            # Insert new budget entry
            response = supabase.table("budgets").insert(data).execute()
            log_message(f"Inserted new budget for category {data['category_id']}", "INFO", "/budgets")

        return jsonify(response.data), 200

    except Exception as e:
        log_message(f"Error setting budget: {str(e)}", "ERROR", "/budgets")
        return jsonify({"error": str(e)}), 500


# ✅ Delete a budget item
@budgets_blueprint.route("/budgets/<int:budget_id>", methods=["DELETE"])
def delete_budget(budget_id):
    """Delete a budget entry by ID."""
    try:
        response = (
            supabase.table("budgets")
            .delete()
            .eq("id", budget_id)
            .execute()
        )

        log_message(f"Deleted budget ID {budget_id}", "INFO", "/budgets")
        return jsonify({"message": "Budget deleted successfully"}), 200

    except Exception as e:
        log_message(f"Error deleting budget: {str(e)}", "ERROR", "/budgets")
        return jsonify({"error": str(e)}), 500