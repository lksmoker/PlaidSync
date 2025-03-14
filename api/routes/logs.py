from flask import Blueprint, request, jsonify
from supabase_client import supabase
import uuid
from datetime import datetime

logs_blueprint = Blueprint('logs', __name__)

@logs_blueprint.route('/logs', methods=['POST'])
def insert_log():
    """Inserts a log entry into the logs table."""
    try:
        data = request.json
        new_log = {
            "id": str(uuid.uuid4()),
            "severity": data.get("severity", "INFO"),
            "message": data["message"],
            "service": data["service"],
            "page": data.get("page"),
            "endpoint": data.get("endpoint"),
            "user_id": data.get("user_id"),
            "ip_address": request.remote_addr,
            "request_data": data.get("request_data"),
            "response_data": data.get("response_data"),
            "stack_trace": data.get("stack_trace"),
            "created_at": datetime.utcnow().isoformat()
        }

        response = supabase.table("logs").insert(new_log).execute()
        return jsonify({"message": "Log added successfully!", "data": response.data}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@logs_blueprint.route('/logs', methods=['GET'])
def get_logs():
    """Fetches logs with optional filters."""
    try:
        query = supabase.table("logs").select("*")

        if severity := request.args.get("severity"):
            query = query.eq("severity", severity)
        if service := request.args.get("service"):
            query = query.eq("service", service)
        if page := request.args.get("page"):
            query = query.eq("page", page)
        if endpoint := request.args.get("endpoint"):
            query = query.eq("endpoint", endpoint)
        if start_date := request.args.get("start_date"):
            query = query.gte("created_at", start_date)
        if end_date := request.args.get("end_date"):
            query = query.lte("created_at", end_date)

        query = query.order("created_at", desc=True).limit(50)
        response = query.execute()

        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500