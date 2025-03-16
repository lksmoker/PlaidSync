from flask import Blueprint, jsonify, request
from supabase_client import supabase

categories_blueprint = Blueprint("categories", __name__)

@categories_blueprint.route("/categories", methods=["GET"])
def get_categories():
    """Fetch all categories."""
    try:
        response = supabase.table("categories").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_blueprint.route("/categories", methods=["POST"])
def add_category():
    """Add a new category."""
    try:
        data = request.json
        response = supabase.table("categories").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_blueprint.route("/categories/<int:id>", methods=["PUT"])
def update_category(id):
    """Update a category."""
    try:
        data = request.json
        response = supabase.table("categories").update(data).eq("id", id).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_blueprint.route("/categories/<int:id>", methods=["DELETE"])
def delete_category(id):
    """Delete a category."""
    try:
        response = supabase.table("categories").delete().eq("id", id).execute()
        return jsonify(response.data), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_blueprint.route("/categories/main", methods=["GET"])
def get_main_categories():
    """Fetch only main categories (categories without a parent_id)."""
    try:
        response = supabase.table("categories").select("*").is_("parent_id", None).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_blueprint.route("/categories/sub/<int:main_category_id>", methods=["GET"])
def get_subcategories(main_category_id):
    """Fetch subcategories for a given main category."""
    try:
        response = supabase.table("categories").select("*").eq("parent_id", main_category_id).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
