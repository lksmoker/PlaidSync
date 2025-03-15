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
    from routes.accounts import create_accounts_blueprint
    from routes.categories import create_categories_blueprint
    from routes.transactions import create_transactions_blueprint
    from routes.logs import create_logs_blueprint

    # ✅ Register Blueprints with Supabase Passed Explicitly
    app.register_blueprint(create_accounts_blueprint(supabase))
    app.register_blueprint(create_categories_blueprint(supabase))
    app.register_blueprint(create_transactions_blueprint(supabase))
    app.register_blueprint(create_logs_blueprint(supabase))

    @app.route("/")
    def home():
        return {"status": "API is running"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))