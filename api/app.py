from flask import Flask
from supabase import create_client
import os

def create_app():
    app = Flask(__name__)

    # ✅ Initialize Supabase client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: Supabase credentials missing! Check environment variables.")
        supabase = None
    else:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase initialized successfully.")

    # ✅ Import blueprints AFTER initializing Supabase
    from routes.accounts import accounts_blueprint
    from routes.categories import categories_blueprint
    from routes.transactions import transactions_blueprint

    # ✅ Pass Supabase instance to each blueprint
    accounts_blueprint.supabase = supabase
    categories_blueprint.supabase = supabase
    transactions_blueprint.supabase = supabase

    # ✅ Register Blueprints
    app.register_blueprint(accounts_blueprint)
    app.register_blueprint(categories_blueprint)
    app.register_blueprint(transactions_blueprint)

    @app.route("/")
    def home():
        return {"status": "API is running"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=8000)
