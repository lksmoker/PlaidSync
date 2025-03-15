from flask import Blueprint, request, jsonify
from datetime import datetime

def create_logs_blueprint(supabase):
    logs_blueprint = Blueprint('logs', __name__)

    @logs_blueprint.route('/logs', methods=['GET'])
    def get_logs():
        """Fetch logs."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            response = supabase.table("logs").select("*").order("created_at", desc=True).limit(50).execute()
            return jsonify(response.data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return logs_blueprint