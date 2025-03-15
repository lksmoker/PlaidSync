import os
from flask import Flask
from flask_cors import CORS
from supabase_client import supabase  # ✅ Import shared Supabase client

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    if supabase is None:
        print("❌ ERROR: Supabase client not initialized!")

    # ✅ Import blueprints AFTER Supabase is set
    from routes.accounts import accounts_blueprint
    from routes.categories import categories_blueprint
    from routes.transactions import transactions_blueprint
    from routes.logs import logs_blueprint

    # ✅ Register Blueprints
    app.register_blueprint(accounts_blueprint)
    app.register_blueprint(categories_blueprint)
    app.register_blueprint(transactions_blueprint)
    app.register_blueprint(logs_blueprint)

    @app.route("/")
    def home():
        return {"status": "API is running"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))