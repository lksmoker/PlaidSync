from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from supabase import create_client, Client
import os
import subprocess
from datetime import datetime  # ✅ Correct import

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Supabase client
# Initialize Supabase client with Service Role Key
supabase_url = os.getenv("SUPABASE_URL")  # Fetch from environment variables
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE")  # ✅ Use the service role key

# Check if environment variables are set
if not supabase_url or not supabase_key:
    print(
        "⚠️ Warning: SUPABASE_URL or SUPABASE_SERVICE_ROLE environment variables not set."
    )
    print("Please set these in your Render Secrets.")

# Initialize Supabase client
try:
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Successfully connected to Supabase with Service Role Key.")
except Exception as e:
    print(f"❌ Error connecting to Supabase: {str(e)}")
    supabase = None
from datetime import datetime

logs = []  # Temporary in-memory storage (Optional: Use Supabase instead)

@app.route('/logs', methods=['POST'])
def capture_logs():
    """Receives logs from the frontend and stores them in memory or Supabase."""
    data = request.json
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "message": data.get("message", "No message provided"),
        "data": data.get("data")
    }

    logs.append(log_entry)  # Store logs (Optional: Push to Supabase)

    # Print to Render logs
    print(f"🔍 LOG: {log_entry['timestamp']} | {log_entry['message']} | {log_entry['data']}")

    return jsonify({"status": "logged"}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    """Returns stored logs for the frontend logs page."""
    return jsonify(logs), 200

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


from datetime import datetime
import uuid


@app.route('/budgets', methods=['GET'])
def get_budgets():
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if month is None or year is None:
            return jsonify({"error": "Month and year are required"}), 400

        # Get Regular Budget Categories (parent_id != 9)
        regular_budgets = (
            supabase.table("budgets").select(
                "*, categories(parent_id, name)")  # ✅ Join with categories
            .eq("month", month).eq("year",
                                   year).neq("categories.parent_id",
                                             9)  # ✅ Exclude Reserve categories
            .execute())

        # Get Reserve Budgets (parent_id = 9)
        reserve_budgets = (
            supabase.table("budgets").select(
                "*, categories(parent_id, name)").eq("month", month).eq(
                    "year", year).eq("categories.parent_id",
                                     9)  # ✅ Only Reserve categories
            .execute())

        return jsonify({
            "regular_budgets": regular_budgets.data,
            "reserve_budgets": reserve_budgets.data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/split-transaction', methods=['POST'])
def split_transaction():
    try:
        data = request.json
        transaction_id = data.get("transaction_id")
        splits = data.get("splits", [])

        if not transaction_id or not splits:
            return jsonify({"error":
                            "Missing transaction_id or splits data"}), 400

        # ✅ Fetch the original transaction
        response = supabase.table("transactions").select("*").eq(
            "transaction_id", transaction_id).execute()
        if not response.data:
            return jsonify({"error": "Original transaction not found"}), 404

        original_transaction = response.data[
            0]  # ✅ Now we have the original transaction

        # ✅ Mark the original transaction as "split" and clear its categories
        supabase.table("transactions").update({
            "ignored": "split",
            "user_category_id": None,
            "user_subcategory_id": None
        }).eq("transaction_id", transaction_id).execute()

        # ✅ Insert split transactions (ensuring ignored is FALSE)
        new_splits = []
        for split in splits:
            new_splits.append({
                "transaction_id":
                str(uuid.uuid4()),  # Generate new unique ID
                "parent_transaction_id":
                transaction_id,  # Link to original
                "amount":
                split["amount"],
                "user_category_id":
                split["category_id"],
                "user_subcategory_id":
                split.get("subcategory_id"),
                "date":
                original_transaction[
                    "date"],  # ✅ Use original transaction date
                "name":
                f"Split {original_transaction['name']} {original_transaction['date']}",
                "account_id":
                original_transaction["account_id"],  # ✅ Copy account_id
                "ignored":
                False,  # ✅ Ensure split transactions are active
            })

        supabase.table("transactions").insert(new_splits).execute()

        return jsonify({"message": "Transaction split successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/setup')
def setup_page():
    """Render the setup page for managing categories."""
    return render_template('setup.html')


@app.route('/manual-add', methods=['POST'])
def add_manual_transaction():  # ✅ Renamed function
    try:
        if supabase is None:
            return jsonify({"error": "Supabase client not initialized"}), 500

        data = request.json
        print("🔍 Received data:", data)  # ✅ Log request payload

        if not data:
            return jsonify({"error": "No data provided"}), 400

        if isinstance(data, dict):
            data = [data]  # Ensure list format

        results = []
        for transaction_data in data:
            try:
                transaction_id = str(
                    transaction_data.get("transaction_id"))  # ✅ Ensure string
                account_id = str(transaction_data.get(
                    "account_id", "cash"))  # ✅ Ensure string
                category_id = transaction_data.get("user_category_id")
                subcategory_id = transaction_data.get("user_subcategory_id")
                amount = float(transaction_data.get("amount",
                                                    0))  # ✅ Ensure float
                ignored = bool(transaction_data.get(
                    "ignored", False))  # ✅ Convert to boolean
                date = str(transaction_data.get("date"))  # ✅ Ensure string
                name = str(transaction_data.get("name"))  # ✅ Ensure string

                print(
                    f"🛠 Processing: transaction_id={transaction_id}, amount={amount}, category_id={category_id}, subcategory_id={subcategory_id}, account_id={account_id}, ignored={ignored}"
                )

                transaction_insert = {
                    "transaction_id":
                    transaction_id,
                    "amount":
                    amount,
                    "date":
                    date,
                    "name":
                    name,
                    "user_category_id":
                    int(category_id)
                    if category_id is not None else None,  # ✅ Ensure integer
                    "user_subcategory_id":
                    int(subcategory_id) if subcategory_id is not None else
                    None,  # ✅ Ensure integer
                    "account_id":
                    account_id,
                    "ignored":
                    ignored  # ✅ Boolean instead of string
                }

                print("📤 Sending to Supabase:",
                      transaction_insert)  # ✅ Log before insert

                transaction = (supabase.table("transactions").insert(
                    transaction_insert).execute())

                print("✅ Insert response:", transaction.data)  # ✅ Log success

                results.append(transaction.data)

            except Exception as e:
                print("❌ ERROR inserting transaction:",
                      str(e))  # 🔥 Log exact error
                return jsonify(
                    {"error": f"Failed to insert transaction: {str(e)}"}), 500

        return jsonify({
            "message": "Transaction added successfully",
            "results": results
        }), 200

    except Exception as e:
        print("❌ GENERAL API ERROR:", str(e))
        return jsonify({"error": f"API failure: {str(e)}"}), 500


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
            accounts = [
                {
                    "account_id": acc["account_id"],  # ✅ Fix here
                    **acc
                } for acc in response.data
            ]
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

        # Fetch all categories
        response = supabase.table('categories').select("*").execute()
        categories = response.data or []

        # Build a dictionary of categories for easy lookup
        category_dict = {
            cat["id"]: {
                **cat, "subcategories": []
            }
            for cat in categories
        }

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
            if cat.get("parent_id"):
                parent = category_dict.get(cat["parent_id"])
                if parent:
                    parent["subcategories"].append(category_dict[cat["id"]])

        # Filter only top-level categories for Regular (non-Reserve)
        structured_regular = [
            cat for cat in regular_categories if not cat.get("parent_id")
        ]

        # Reserve category structure (only the Reserve category and its subcategories)
        structured_reserve = [
            cat for cat in reserve_categories if cat["id"] == 9
        ]

        return jsonify({
            "regular": structured_regular,
            "reserve": structured_reserve
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/budget-categories', methods=['GET'])
def get_budget_categories():
    try:
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        if not month or not year:
            return jsonify({"error": "Month and year required"}), 400

        # Get all category IDs that are in the budget table
        budgeted_categories = (
            supabase.table("budgets").select("category_id").eq(
                "month", month).eq("year", year).execute())

        category_ids = [b["category_id"] for b in budgeted_categories.data]

        # Fetch only those categories
        response = supabase.table("categories").select("*").in_(
            "id", category_ids).execute()
        return jsonify(response.data), 200

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

        transactions = (
            supabase.table("transactions").select("*").or_(
                "ignored.is.null, ignored.neq.true, ignored.neq.split"
            )  # ✅ Include NULL values explicitly
            .is_("user_category_id", None).execute())

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
        print("🔍 Received data:", data)  # ✅ Log request payload

        if not data:
            return jsonify({"error": "No data provided"}), 400

        if isinstance(data, dict):
            data = [data]  # Ensure list format

        results = []
        for transaction_data in data:
            try:
                transaction_id = str(
                    transaction_data.get("transaction_id"))  # ✅ Ensure string
                category_id = transaction_data.get("user_category_id")
                subcategory_id = transaction_data.get("user_subcategory_id")
                ignored = transaction_data.get(
                    "ignored")  # ✅ Directly use ignored value

                print(
                    f"🛠 Updating: transaction_id={transaction_id}, category_id={category_id}, subcategory_id={subcategory_id}, ignored={ignored}"
                )

                # ✅ Use .update() instead of .insert()
                transaction_update = {
                    "user_category_id":
                    int(category_id) if category_id is not None else None,
                    "user_subcategory_id":
                    int(subcategory_id)
                    if subcategory_id is not None else None,
                    "ignored":
                    ignored  # ✅ Update ignored field
                }

                print("📤 Sending update to Supabase:",
                      transaction_update)  # ✅ Log before update

                transaction = (
                    supabase.table(
                        "transactions").update(transaction_update).eq(
                            "transaction_id",
                            transaction_id)  # ✅ Find transaction by ID
                    .execute())

                print("✅ Update response:", transaction.data)  # ✅ Log success

                results.append(transaction.data)

            except Exception as e:
                print("❌ ERROR updating transaction:",
                      str(e))  # 🔥 Log exact error
                return jsonify(
                    {"error": f"Failed to update transaction: {str(e)}"}), 500

        return jsonify({
            "message": "Transactions updated successfully",
            "results": results
        }), 200

    except Exception as e:
        print("❌ GENERAL API ERROR:", str(e))
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
