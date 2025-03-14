from flask import Flask
from flask_cors import CORS
from routes.logs import logs_blueprint
from routes.transactions import transactions_blueprint
from routes.budgets import budgets_blueprint
from routes.categories import categories_blueprint
from routes.duplicates import duplicates_blueprint
from routes.accounts import accounts_blueprint
from routes.setup import setup_blueprint

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register Blueprints
app.register_blueprint(logs_blueprint)
app.register_blueprint(transactions_blueprint)
app.register_blueprint(budgets_blueprint)
app.register_blueprint(categories_blueprint)
app.register_blueprint(duplicates_blueprint)
app.register_blueprint(accounts_blueprint)
app.register_blueprint(setup_blueprint)

@app.route('/')
def home():
    return {"status": "API is running"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)