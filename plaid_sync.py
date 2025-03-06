import os
import requests
from supabase import create_client
from datetime import datetime, timedelta

# ✅ Load Plaid credentials
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PLAID_ENV = "https://sandbox.plaid.com"  # Change to production if needed

# ✅ Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Plaid API endpoints
PLAID_TRANSACTIONS_URL = f"{PLAID_ENV}/transactions/get"
PLAID_ACCOUNTS_URL = f"{PLAID_ENV}/accounts/get"

# -------------------------------------------
# ✅ Fetch transactions from Plaid
# -------------------------------------------
def fetch_transactions():
    headers = {"Content-Type": "application/json"}
    start_date = (datetime.today() - timedelta(days=60)).strftime('%Y-%m-%d')
    end_date = datetime.today().strftime('%Y-%m-%d')

    payload = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "access_token": ACCESS_TOKEN,
        "start_date": start_date,
        "end_date": end_date,
        "options": {"count": 500}  # Fetch up to 500 transactions
    }

    response = requests.post(PLAID_TRANSACTIONS_URL, json=payload, headers=headers)

    if response.status_code == 200:
        transactions = response.json().get("transactions", [])
        print(f"✅ Fetched {len(transactions)} transactions.")
        return transactions
    else:
        print("❌ Error fetching transactions:", response.json())
        return []

# -------------------------------------------
# ✅ Fetch and store account balances
# -------------------------------------------
def fetch_account_balances():
    headers = {"Content-Type": "application/json"}
    payload = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "access_token": ACCESS_TOKEN
    }
    response = requests.post(PLAID_ACCOUNTS_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("accounts", [])
    else:
        print("❌ Error fetching account balances:", response.json())
        return []

def store_account_balances(accounts):
    for account in accounts:
        try:
            existing = supabase.table("accounts").select("*").eq("id", account["account_id"]).execute()

            account_data = {
                "id": account["account_id"],
                "name": account["name"],
                "official_name": account.get("official_name", "Unknown"),
                "type": account["type"],
                "subtype": account["subtype"],
                "balance_available": account.get("balances", {}).get("available"),
                "balance_current": account.get("balances", {}).get("current"),
                "iso_currency_code": account.get("balances", {}).get("iso_currency_code", "USD")
            }

            if existing.data:
                supabase.table("accounts").update(account_data).eq("id", account["account_id"]).execute()
                print(f"✅ Updated account: {account['name']}")
            else:
                supabase.table("accounts").insert(account_data).execute()
                print(f"✅ Inserted new account: {account['name']}")

        except Exception as e:
            print(f"❌ Error storing account {account.get('name', 'Unknown')}: {str(e)}")

# -------------------------------------------
# ✅ Store transactions in Supabase while preserving user edits
# -------------------------------------------
def store_transactions(transactions):
    inserted_count, updated_count, skipped_count = 0, 0, 0

    for tx in transactions:
        try:
            # ✅ Ensure account exists
            account_exists = supabase.table("accounts").select("id").eq("id", tx["account_id"]).execute()
            if not account_exists.data:
                print(f"⚠️ Skipping transaction {tx['transaction_id']} - Account {tx['account_id']} not found.")
                skipped_count += 1
                continue

            # ✅ Check if transaction exists
            existing_tx = supabase.table("transactions").select("pending", "name", "date").eq("transaction_id", tx["transaction_id"]).execute()

            # ✅ Determine if transaction is pending or posted
            is_pending = tx["pending"]  # True = Pending, False = Posted

            # ✅ Prepare transaction data
            tx_data = {
                "transaction_id": tx["transaction_id"],
                "account_id": tx["account_id"],
                "amount": tx["amount"],
                "iso_currency_code": tx.get("iso_currency_code", "USD"),
                "merchant_name": tx.get("merchant_name"),
                "category": ", ".join(tx.get("category", [])),
                "plaid_category_id": tx.get("category_id"),
                "pending": is_pending,  # ✅ Store correct pending status
                "location_address": tx["location"].get("address"),
                "location_city": tx["location"].get("city"),
                "location_region": tx["location"].get("region"),
                "location_postal_code": tx["location"].get("postal_code"),
                "location_country": tx["location"].get("country"),
            }

            if existing_tx.data:
                existing_data = existing_tx.data[0]

                # ✅ If transaction is still pending, allow full update
                if existing_data["pending"]:  # Was pending in DB
                    supabase.table("transactions").update(tx_data).eq("transaction_id", tx["transaction_id"]).execute()
                    updated_count += 1

                # ✅ If transaction was pending but is now posted, only update `pending` field
                elif existing_data["pending"] and not is_pending:  # Moving from pending → posted
                    supabase.table("transactions").update({"pending": False}).eq("transaction_id", tx["transaction_id"]).execute()
                    updated_count += 1

                # ✅ If transaction is already posted, do not update name or date
                else:
                    print(f"🚫 Skipping update for already posted transaction: {tx['transaction_id']}")
                    skipped_count += 1

        except Exception as e:
            print(f"❌ Error storing transaction {tx.get('transaction_id', 'Unknown')}: {str(e)}")
            skipped_count += 1

    print(f"📊 Transaction sync summary: {inserted_count} inserted, {updated_count} updated, {skipped_count} skipped")

# -------------------------------------------
# ✅ Main function to fetch and store transactions & balances
# -------------------------------------------
def main():
    try:
        print("🔄 Fetching account balances from Plaid...")
        accounts = fetch_account_balances()
        if accounts:
            print(f"✅ Fetched {len(accounts)} accounts from Plaid.")
            store_account_balances(accounts)
            print("💾 Account synchronization complete.")

        print("\n🔄 Fetching transactions from Plaid...")
        transactions = fetch_transactions()
        if transactions:
            print(f"✅ Fetched {len(transactions)} transactions from Plaid.")
            store_transactions(transactions)
            print("💾 Transaction synchronization complete.")

        print("\n🏁 Plaid synchronization process completed successfully!")

    except Exception as e:
        print(f"❌ Error in Plaid synchronization process: {str(e)}")
        import traceback
        traceback.print_exc()

# ✅ Ensure this runs only when executed directly
if __name__ == "__main__":
    main()
