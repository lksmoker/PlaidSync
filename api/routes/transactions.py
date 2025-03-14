        from flask import Blueprint, jsonify, request
        from supabase import create_client
        import os
        import uuid

        # Create Blueprint for Transactions
        transactions_blueprint = Blueprint("transactions", __name__)

        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE")

        supabase = create_client(supabase_url, supabase_key)


        # ✅ Get All Transactions
        @transactions_blueprint.route('/transactions', methods=['GET'])
        def get_transactions():
            try:
                transactions = supabase.table('transactions').select('*').order('date', desc=True).execute()
                return jsonify(transactions.data), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500


        # ✅ Get Processed Transactions (categorized or ignored)
        @transactions_blueprint.route('/processed-transactions', methods=['GET'])
        def get_processed_transactions():
            try:
                transactions = (
                    supabase.table('transactions')
                    .select('*')
                    .or_('ignored.eq.true, user_category_id.not.is.null')
                    .execute()
                )
                return jsonify(transactions.data), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500


        # ✅ Get Unprocessed Transactions
        @transactions_blueprint.route('/unprocessed-transactions', methods=['GET'])
        def get_unprocessed_transactions():
            try:
                transactions = (
                    supabase.table('transactions')
                    .select('*')
                    .or_(
                        "ignored.is.null, ignored.neq.true, ignored.neq.split"
                    )  # Include NULL values explicitly
                    .is_("user_category_id", None)
                    .execute()
                )
                return jsonify(transactions.data), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500


        # ✅ Update Transactions
        @transactions_blueprint.route('/update-transactions', methods=['POST'])
        def update_transactions():
            try:
                data = request.json
                if not data:
                    return jsonify({"error": "No data provided"}), 400

                if isinstance(data, dict):
                    data = [data]  # Ensure list format

                results = []
                for transaction_data in data:
                    try:
                        transaction_id = str(transaction_data.get("transaction_id"))
                        category_id = transaction_data.get("user_category_id")
                        subcategory_id = transaction_data.get("user_subcategory_id")
                        ignored = transaction_data.get("ignored")  # Directly use ignored value

                        transaction_update = {
                            "user_category_id": int(category_id) if category_id is not None else None,
                            "user_subcategory_id": int(subcategory_id) if subcategory_id is not None else None,
                            "ignored": ignored  # Update ignored field
                        }

                        transaction = (
                            supabase.table("transactions")
                            .update(transaction_update)
                            .eq("transaction_id", transaction_id)  # Find transaction by ID
                            .execute()
                        )

                        results.append(transaction.data)

                    except Exception as e:
                        return jsonify({"error": f"Failed to update transaction: {str(e)}"}), 500

                return jsonify({"message": "Transactions updated successfully", "results": results}), 200

            except Exception as e:
                return jsonify({"error": f"API failure: {str(e)}"}), 500


        # ✅ Add a Manual Transaction
        @transactions_blueprint.route('/manual-add', methods=['POST'])
        def add_manual_transaction():
            try:
                data = request.json
                if not data:
                    return jsonify({"error": "No data provided"}), 400

                if isinstance(data, dict):
                    data = [data]  # Ensure list format

                results = []
                for transaction_data in data:
                    try:
                        transaction_id = str(uuid.uuid4())  # Generate a new unique ID
                        account_id = str(transaction_data.get("account_id", "cash"))
                        category_id = transaction_data.get("user_category_id")
                        subcategory_id = transaction_data.get("user_subcategory_id")
                        amount = float(transaction_data.get("amount", 0))
                        ignored = bool(transaction_data.get("ignored", False))
                        date = str(transaction_data.get("date"))
                        name = str(transaction_data.get("name"))

                        transaction_insert = {
                            "transaction_id": transaction_id,
                            "amount": amount,
                            "date": date,
                            "name": name,
                            "user_category_id": int(category_id) if category_id is not None else None,
                            "user_subcategory_id": int(subcategory_id) if subcategory_id is not None else None,
                            "account_id": account_id,
                            "ignored": ignored
                        }

                        transaction = supabase.table("transactions").insert(transaction_insert).execute()
                        results.append(transaction.data)

                    except Exception as e:
                        return jsonify({"error": f"Failed to insert transaction: {str(e)}"}), 500

                return jsonify({"message": "Transaction added successfully", "results": results}), 200

            except Exception as e:
                return jsonify({"error": f"API failure: {str(e)}"}), 500


        # ✅ Split a Transaction
        @transactions_blueprint.route('/split-transaction', methods=['POST'])
        def split_transaction():
            try:
                data = request.json
                transaction_id = data.get("transaction_id")
                splits = data.get("splits", [])

                if not transaction_id or not splits:
                    return jsonify({"error": "Missing transaction_id or splits data"}), 400

                response = supabase.table("transactions").select("*").eq("transaction_id", transaction_id).execute()
                if not response.data:
                    return jsonify({"error": "Original transaction not found"}), 404

                original_transaction = response.data[0]

                supabase.table("transactions").update({
                    "ignored": "split",
                    "user_category_id": None,
                    "user_subcategory_id": None
                }).eq("transaction_id", transaction_id).execute()

                new_splits = []
                for split in splits:
                    new_splits.append({
                        "transaction_id": str(uuid.uuid4()),
                        "parent_transaction_id": transaction_id,
                        "amount": split["amount"],
                        "user_category_id": split["category_id"],
                        "user_subcategory_id": split.get("subcategory_id"),
                        "date": original_transaction["date"],
                        "name": f"Split {original_transaction['name']} {original_transaction['date']}",
                        "account_id": original_transaction["account_id"],
                        "ignored": False
                    })

                supabase.table("transactions").insert(new_splits).execute()

                return jsonify({"message": "Transaction split successfully!"}), 200

            except Exception as e:
                return jsonify({"error": str(e)}), 500


        # ✅ Confirm a Transaction as a Duplicate
        @transactions_blueprint.route('/confirm-duplicate', methods=['POST'])
        def confirm_duplicate():
            try:
                data = request.json
                if not data or 'transaction_id' not in data or 'is_duplicate' not in data:
                    return jsonify({"error": "Missing required fields: transaction_id or is_duplicate"}), 400

                transaction_id = data['transaction_id']
                is_duplicate = data['is_duplicate']
                transaction = supabase.table('transactions').update({
                    'confirmed_duplicate': is_duplicate
                }).eq('transaction_id', transaction_id).execute()

                return jsonify({"success": True, "data": transaction.data}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500