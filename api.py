from flask import Flask, jsonify, request
from flask_cors import CORS  
import sqlite3
from werkzeug.serving import WSGIRequestHandler
import ssl

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Database configuration
DATABASE = "transactions_dev.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "GET /unprocessed-transactions": "Get all unprocessed transactions",
            "GET /transactions": "Get all transactions",
            "GET /accounts": "Get all accounts",
            "POST /update-transactions": "Update transaction categories and ignored status"
        }
    })

@app.route('/unprocessed-transactions')
def unproc
