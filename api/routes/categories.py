        from flask import Blueprint, jsonify, request
        from supabase import create_client, Client
        import os

        # Create Blueprint
        categories_blueprint = Blueprint("categories", __name__)

        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE")

        if not supabase_url or not supabase_key:
            print("❌ ERROR: Missing Supabase URL or Service Role Key. Check your environment variables.")

        try:
            supabase: Client = create_client(supabase_url, supabase_key)
            print("✅ Supabase client initialized successfully.")
        except Exception as e:
            print(f"❌ Supabase initialization failed: {e}")
            supabase = None  # Prevent further errors

        # ✅ GET Categories
        @categories_blueprint.route("/categories", methods=["GET"])
        def get_categories():
            """Fetch all categories in a structured format."""
            try:
                if supabase is None:
                    return jsonify({"error": "Supabase client not initialized"}), 500

                response = supabase.table("categories").select("*").execute()
                categories = response.data or []

                if not categories:
                    return jsonify({"message": "No categories found."}), 200

                category_dict = {cat["id"]: {**cat, "subcategories": []} for cat in categories}

                # Separate categories into Regular and Reserve
                reserve_categories = []
                regular_categories = []

                for cat in categories:
                    if cat.get("parent_id") == 9 or cat["id"] == 9:
                        reserve_categories.append(category_dict[cat["id"]])
                    else:
                        regular_categories.append(category_dict[cat["id"]])

                # Assign subcategories to their parents
                for cat in categories:
                    if cat.get("parent_id") and cat["parent_id"] in category_dict:
                        category_dict[cat["parent_id"]]["subcategories"].append(category_dict[cat["id"]])

                # ✅ Log output to check if subcategories are assigned correctly
                print("🔍 Regular Categories:", regular_categories)
                print("🔍 Reserve Categories:", reserve_categories)

                return jsonify({"regular": regular_categories, "reserve": reserve_categories}), 200

            except Exception as e:
                print(f"❌ Error in get_categories: {e}")  # Log exact error
                return jsonify({"error": str(e)}), 500


        # ✅ POST - Add a new category
        @categories_blueprint.route("/categories", methods=["POST"])
        def add_category():
            """Add a new category."""
            try:
                if supabase is None:
                    return jsonify({"error": "Supabase client not initialized"}), 500

                data = request.json
                if not data or "name" not in data:
                    return jsonify({"error": "Missing required field: name"}), 400

                category = supabase.table("categories").insert({
                    "name": data["name"],
                    "parent_id": data.get("parent_id", None),
                }).execute()

                return jsonify(category.data), 201
            except Exception as e:
                print(f"❌ Error in add_category: {e}")
                return jsonify({"error": str(e)}), 500


        # ✅ PUT - Update a category
        @categories_blueprint.route("/categories/<int:id>", methods=["PUT"])
        def update_category(id):
            """Update a category."""
            try:
                if supabase is None:
                    return jsonify({"error": "Supabase client not initialized"}), 500

                data = request.json
                if not data or "name" not in data:
                    return jsonify({"error": "Missing required field: name"}), 400

                category = supabase.table("categories").update({
                    "name": data["name"],
                    "parent_id": data.get("parent_id", None),
                }).eq("id", id).execute()

                return jsonify(category.data), 200
            except Exception as e:
                print(f"❌ Error in update_category: {e}")
                return jsonify({"error": str(e)}), 500


        # ✅ DELETE - Delete a category
        @categories_blueprint.route("/categories/<int:id>", methods=["DELETE"])
        def delete_category(id):
            """Delete a category."""
            try:
                if supabase is None:
                    return jsonify({"error": "Supabase client not initialized"}), 500

                response = supabase.table("categories").delete().eq("id", id).execute()
                return jsonify(response.data), 204
            except Exception as e:
                print(f"❌ Error in delete_category: {e}")
                return jsonify({"error": str(e)}), 500