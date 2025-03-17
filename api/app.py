import os
from flask import Flask, jsonify
from flask_cors import CORS
from supabase_client import supabase  # ✅ Import shared Supabase client

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}},
         supports_credentials=True, 
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "OPTIONS", "PATCH", "DELETE"])

    if supabase is None:
        print("❌ ERROR: Supabase client not initialized!")

    # ✅ Import blueprints AFTER Supabase is set
    from routes.accounts import accounts_blueprint
    from routes.categories import categories_blueprint
    from routes.transactions import transactions_blueprint
    from routes.logs import logs_blueprint
    from routes.budgets import budgets_blueprint  # ✅ Add Budgets Route
    from routes.summary import summary_blueprint  # ✅ Add Summary Route

    # ✅ Register Blueprints
    app.register_blueprint(accounts_blueprint)
    app.register_blueprint(categories_blueprint)
    app.register_blueprint(transactions_blueprint)
    app.register_blueprint(logs_blueprint)
    app.register_blueprint(budgets_blueprint)  # ✅ Register Budgets
    app.register_blueprint(summary_blueprint)  # ✅ Register Summary

    @app.route("/test-connection", methods=["GET"])
    def test_connection():
        return jsonify({"status": "API is running"}), 200

    @app.route("/")
    def home():
        return {"status": "API is running"}

    @app.route("/list-routes", methods=["GET"])
    def list_routes():
        return jsonify([str(rule) for rule in app.url_map.iter_rules()])

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))