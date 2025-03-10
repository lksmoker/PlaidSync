from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from supabase import create_client, Client
import os
import subprocess
import datetime

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")  # Fetch from environment variables
supabase_key = os.getenv("SUPABASE_KEY")  # Fetch from environment variables

# Check if environment variables are set
if not supabase_url or not supabase_key:
    print(
        "⚠️ Warning: SUPABASE_URL or SUPABASE_KEY environment variables not set."
    )
    print("Please set these in your Replit Secrets.")

# Initialize Supabase client
try:
    supabase = create_client(supabase_url, supabase_key)
except Exception as e:
    print(f"Error connecting to Supabase: {str(e)}")
    supabase = None


# Route to check server status
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "endpoints": {
            "GET /accounts": "Get all accounts",
            "GET /categories": "Get all categories in a nested structure",
            "POST /categories": "Add a new category",
            "PUT /categories/<id>": "Update a category",
            "DELETE /categories/<id>": "Delete a category",
            "GET /processed-transactions":
            "Get all categorized or ignored transactions",
            "GET /unprocessed-transactions":
            "Get all unprocessed transactions",
            "GET /transactions": "Get all transactions",
            "POST /update-transactions": "Update or insert transactions",
            "POST /confirm-duplicate":
            "Mark a transaction as confirmed duplicate or not",
            "GET /duplicate-pairs":
            "Get potential duplicate transactions as pairs",
            "GET /duplicate-review":
            "Interactive page to review duplicate transactions",
            "GET /duplicate-transactions":
            "Get all potential duplicate transactions",
            "GET /setup": "Setup page for managing categories",
            "GET /review": "Page for reviewing duplicate transactions",
            "POST /sync-plaid": "Runs Plaid_sync.py"
        }
    })

import uuid

@app.route('/split-transaction', methods=['POST'])
def split_transaction():
        try:
            data = request.json
            transaction_id = data.get("transaction_id")
            splits = data.get("splits", [])

            if not transaction_id or not splits:
                return jsonify({"error": "Missing transaction_id or splits data"}), 400

            # ✅ Mark the original transaction as "split"
            supabase.table("transactions").update({"ignored": "split"}).eq("transaction_id", transaction_id).execute()

            # ✅ Insert split transactions (ensuring ignored is FALSE)
            new_splits = []
            for split in splits:
                new_splits.append({
                    "transaction_id": str(uuid.uuid4()),  # Generate new unique ID
                    "parent_transaction_id": transaction_id,  # Link to original
                    "amount": split["amount"],
                    "user_category_id": split["category_id"],
                    "user_subcategory_id": split.get("subcategory_id"),
                    "date": datetime.now().strftime("%Y-%m-%d"),  # Use current date
                    "name": f"Split from {transaction_id}",
                    "ignored": False,  # ✅ Ensure split transactions are active
                })

            supabase.table("transactions").insert(new_splits).execute()

            return jsonify({"message": "Transaction split successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
@app.route('/sync-plaid', methods=['POST'])
def sync_plaid():
    """Trigger plaid_sync.py manually."""
    try:
        result = subprocess.run(["python3", "plaid_sync.py"],
                                capture_output=True,
                                text=True)

        if result.returncode == 0:
            return jsonify({
                "message": "Plaid sync successful",
                "output": result.stdout
            }), 200
        else:
            return jsonify({
                "error": "Plaid sync failed",
                "output": result.stderr
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/setup')
def setup_page():
    """Render the setup page for managing categories."""
    return render_template('setup.html')


@app.route('/review')
def review_page():
    """Render the duplicate review page."""
    return render_template('duplicate_review.html')


@app.route('/accounts', methods=['GET'])
def get_accounts():
    """Fetch all accounts from Supabase."""
    try:
        print("🔍 Fetching accounts from Supabase...")
        response = supabase.table("accounts").select("*").execute()
        print(f"📊 Query result: {response.data}")

        if response.data:
            # Use 'account_id' instead of 'id'
            accounts = [{
                "account_id": acc["account_id"],  # ✅ Fix here
                **acc
            } for acc in response.data]
            return jsonify(accounts), 200
        else:
            print("⚠️ No accounts found in Supabase.")
            return jsonify({"message": "No accounts found"}), 404
    except Exception as e:
        print(f"❌ Error fetching accounts: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test-connection', methods=['GET'])
def test_connection():
    try:
        # Attempt a basic query to check the connection
        response = supabase.table('transactions').select('*').limit(
            1).execute()
        return jsonify({
            "message": "Connection successful",
            "data": response.data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ping', methods=['GET'])
def ping():
    """Simple endpoint to test if the API is running correctly."""
    return jsonify({"status": "ok", "message": "API is running"})


# Route to get all categories
@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500
        categories = supabase.table('categories').select('*').execute()
        return jsonify(categories.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to get all transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        transactions = supabase.table('transactions').select('*').order(
            'date', desc=True).execute()
        return jsonify(transactions.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to get all processed (categorized/ignored) transactions
@app.route('/processed-transactions', methods=['GET'])
def get_processed_transactions():
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        # Get transactions that are either ignored OR have a user_category_id set
        transactions = supabase.table('transactions').select('*').or_(
            'ignored.eq.true,user_category_id.not.is.null').execute()
        return jsonify(transactions.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to get all unprocessed transactions
@app.route('/unprocessed-transactions', methods=['GET'])
def get_unprocessed_transactions():
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        transactions = supabase.table('transactions').select('*').eq(
            'ignored', False).is_('user_category_id', None).execute()
        return jsonify(transactions.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to add a new category
@app.route('/categories', methods=['POST'])
def add_category():
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Missing required field: name"}), 400

        category = supabase.table('categories').insert({
            'name':
            data['name'],
            'parent_id':
            data.get('parent_id', None)
        }).execute()
        return jsonify(category.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to update a category
@app.route('/categories/<int:id>', methods=['PUT'])
def update_category(id):
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Missing required field: name"}), 400

        category = supabase.table('categories').update({
            'name':
            data['name'],
            'parent_id':
            data.get('parent_id', None)
        }).eq('id', id).execute()
        return jsonify(category.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to delete a category
@app.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        response = supabase.table('categories').delete().eq('id', id).execute()
        return jsonify(response.data), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to confirm a transaction as a duplicate or not
@app.route('/confirm-duplicate', methods=['POST'])
def confirm_duplicate():
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        data = request.json
        if not data or 'transaction_id' not in data or 'is_duplicate' not in data:
            return jsonify({
                "error":
                "Missing required fields: transaction_id or is_duplicate"
            }), 400

        transaction_id = data['transaction_id']
        is_duplicate = data['is_duplicate']  # True or False
        transaction = supabase.table('transactions').update({
            'confirmed_duplicate':
            is_duplicate
        }).eq('id', transaction_id).execute()
        return jsonify({"success": True, "data": transaction.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

        # Route to update or insert transactions

@app.route('/update-transactions', methods=['POST'])
def update_transactions():
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        data = request.json
        if not data:
            print("❌ No data received in request.")  # 🔥 Debugging log
            return jsonify({"error": "No data provided"}), 400

        print("🔍 Received transaction update request:", data)  # ✅ Log received data

        results = []
        for transaction_data in data:
            try:
                transaction_id = transaction_data.get("transaction_id")
                if not transaction_id:
                    print("⚠️ Missing transaction_id:", transaction_data)
                    continue  # Skip this transaction

                print("🛠 Processing transaction:", transaction_data)  # ✅ Log each transaction

                # Only include fields that are provided in the update request
                transaction_update = {}
                if "date" in transaction_data:
                    transaction_update["date"] = transaction_data["date"]
                if "name" in transaction_data:
                    transaction_update["name"] = transaction_data["name"]
                if "user_category_id" in transaction_data:
                    transaction_update["user_category_id"] = int(transaction_data["user_category_id"]) if transaction_data["user_category_id"] is not None else None
                if "user_subcategory_id" in transaction_data:
                    transaction_update["user_subcategory_id"] = int(transaction_data["user_subcategory_id"]) if transaction_data["user_subcategory_id"] is not None else None
                if "ignored" in transaction_data:
                    transaction_update["ignored"] = bool(transaction_data["ignored"])

                if not transaction_update:
                    print(f"⚠️ No valid fields to update for transaction {transaction_id}")
                    continue  # Skip empty updates

                print("📝 Sending to Supabase:", transaction_update)  # ✅ Log before sending to Supabase
                transaction = (
                    supabase
                    .table('transactions')
                    .update(transaction_update)
                    .eq('transaction_id', transaction_id)  # 🔥 Correct filtering method
                    .execute()
                )

                results.append(transaction.data)

            except Exception as e:
                print("❌ Error updating transaction:", e)  # 🔥 Log specific error
                return jsonify({"error": f"Failed to update transaction: {str(e)}"}), 500

        return jsonify({"message": "Transactions updated successfully", "results": results}), 200

    except Exception as e:
        print("❌ General API error:", e)  # 🔥 Log general error
        return jsonify({"error": f"API failure: {str(e)}"}), 500


# Route to get potential duplicate transaction pairs
@app.route('/duplicate-pairs', methods=['GET'])
def get_duplicate_pairs():
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        # Get transactions flagged as potential duplicates
        duplicates = supabase.table('transactions').select('*').eq(
            'potential_duplicate', True).execute()

        if not duplicates.data:
            return jsonify([]), 200

        # Format the data into pairs
        pairs = []
        for i in range(0, len(duplicates.data), 2):
            if i + 1 < len(duplicates.data):
                pairs.append({
                    'date':
                    duplicates.data[i]['date'],
                    'amount':
                    duplicates.data[i]['amount'],
                    'account_id':
                    duplicates.data[i].get('account_id', ''),
                    'transaction1':
                    duplicates.data[i],
                    'transaction2':
                    duplicates.data[i + 1]
                })

        return jsonify(pairs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to get all potential duplicate transactions
@app.route('/duplicate-transactions', methods=['GET'])
def get_duplicate_transactions():
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        duplicates = supabase.table('transactions').select('*').eq(
            'confirmed_duplicate', None).execute()
        return jsonify(duplicates.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to review duplicate transactions (interactive)
@app.route('/duplicate-review', methods=['GET'])
def duplicate_review():
    try:
        # Renders the HTML template from templates/duplicate_review.html
        return render_template('duplicate_review.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Start the app
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
