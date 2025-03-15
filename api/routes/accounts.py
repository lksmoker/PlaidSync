from flask import Blueprint, jsonify, request

def create_accounts_blueprint(supabase):
    accounts_blueprint = Blueprint("accounts", __name__)

    @accounts_blueprint.route("/accounts", methods=["GET"])
    def get_accounts():
        """Fetch all accounts."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            response = supabase.table("accounts").select("*").execute()
            return jsonify(response.data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @accounts_blueprint.route("/accounts", methods=["POST"])
    def add_account():
        """Add a new account."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            data = request.json
            response = supabase.table("accounts").insert(data).execute()
            return jsonify(response.data), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @accounts_blueprint.route("/accounts/<account_id>", methods=["PUT"])
    def update_account(account_id):
        """Update an account."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            data = request.json
            response = supabase.table("accounts").update(data).eq("account_id", account_id).execute()
            return jsonify(response.data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @accounts_blueprint.route("/accounts/<account_id>", methods=["DELETE"])
    def delete_account(account_id):
        """Delete an account."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            response = supabase.table("accounts").delete().eq("account_id", account_id).execute()
            return jsonify(response.data), 204
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return accounts_blueprint