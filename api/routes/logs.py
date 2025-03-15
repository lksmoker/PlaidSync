from flask import Blueprint, jsonify, request
from supabase_client import supabase
import uuid
from datetime import datetime

logs_blueprint = Blueprint("logs", __name__)

@logs_blueprint.route("/logs", methods=["GET"])
def get_logs():
    """Fetch logs."""
    try:
        response = supabase.table("logs").select("*").order("created_at", desc=True).limit(50).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@logs_blueprint.route("/logs", methods=["POST"])
def insert_log():
    """Insert a log entry."""
    try:
        data = request.json
        new_log = {
            "id": str(uuid.uuid4()),
            "message": data.get("message"),
            "severity": data.get("severity", "INFO"),
            "created_at": datetime.utcnow().isoformat()
        }
        response = supabase.table("logs").insert(new_log).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500