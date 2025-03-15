from flask import Blueprint, jsonify, request

def create_transactions_blueprint(supabase):
    transactions_blueprint = Blueprint("transactions", __name__)

    @transactions_blueprint.route("/transactions", methods=["GET"])
    def get_transactions():
        """Fetch all transactions."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            response = supabase.table("transactions").select("*").execute()
            return jsonify(response.data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @transactions_blueprint.route("/transactions", methods=["POST"])
    def add_transaction():
        """Add a new transaction."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            data = request.json
            response = supabase.table("transactions").insert(data).execute()
            return jsonify(response.data), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @transactions_blueprint.route("/transactions/<transaction_id>", methods=["PUT"])
    def update_transaction(transaction_id):
        """Update a transaction."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            data = request.json
            response = supabase.table("transactions").update(data).eq("transaction_id", transaction_id).execute()
            return jsonify(response.data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return transactions_blueprint