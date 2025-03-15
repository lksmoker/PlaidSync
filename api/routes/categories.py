from flask import Blueprint, jsonify, request

def create_categories_blueprint(supabase):
    categories_blueprint = Blueprint("categories", __name__)

    @categories_blueprint.route("/categories", methods=["GET"])
    def get_categories():
        """Fetch all categories."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            response = supabase.table("categories").select("*").execute()
            return jsonify(response.data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @categories_blueprint.route("/categories", methods=["POST"])
    def add_category():
        """Add a new category."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            data = request.json
            response = supabase.table("categories").insert(data).execute()
            return jsonify(response.data), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @categories_blueprint.route("/categories/<int:category_id>", methods=["PUT"])
    def update_category(category_id):
        """Update a category."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            data = request.json
            response = supabase.table("categories").update(data).eq("id", category_id).execute()
            return jsonify(response.data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @categories_blueprint.route("/categories/<int:category_id>", methods=["DELETE"])
    def delete_category(category_id):
        """Delete a category."""
        if not supabase:
            return jsonify({"error": "Supabase client not initialized"}), 500

        try:
            response = supabase.table("categories").delete().eq("id", category_id).execute()
            return jsonify(response.data), 204
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return categories_blueprint