import os
import requests
from supabase import create_client
from datetime import datetime, timedelta

# ✅ Load Plaid & Supabase credentials from environment variables
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PLAID_ENV = "https://sandbox.plaid.com"  # Change to production if needed

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Plaid API endpoints
PLAID_TRANSACTIONS_URL = f"{PLAID_ENV}/transactions/get"
PLAID_ACCOUNTS_URL = f"{PLAID_ENV}/accounts/get"


# -------------------------------------------
# ✅ Fetch Transactions from Plaid
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
        "options": {
            "count": 500
        }
    }

    response = requests.post(PLAID_TRANSACTIONS_URL,
                             json=payload,
                             headers=headers)

    if response.status_code == 200:
        transactions = response.json().get("transactions", [])
        print(f"✅ Fetched {len(transactions)} transactions.")
        return transactions
    else:
        print("❌ Error fetching transactions:", response.json())
        return []


# -------------------------------------------
# ✅ Fetch & Store Accounts from Plaid
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
            account_id = account.get("account_id")
            if not account_id:
                print(
                    f"⚠️ Missing account_id for account {account.get('name', 'Unknown')}, skipping."
                )
                continue

            # ✅ Prepare account data
            account_data = {
                "account_id":
                account_id,
                "name":
                account["name"],
                "official_name":
                account.get("official_name", "Unknown"),
                "type":
                account["type"],
                "subtype":
                account["subtype"],
                "balance_available":
                account.get("balances", {}).get("available"),
                "balance_current":
                account.get("balances", {}).get("current"),
                "iso_currency_code":
                account.get("balances", {}).get("iso_currency_code", "USD")
            }

            # ✅ Upsert the account (Insert or Update)
            supabase.table("accounts").upsert(account_data).execute()
            print(f"✅ Stored account: {account['name']}")

        except Exception as e:
            print(
                f"❌ Error storing account {account.get('name', 'Unknown')}: {str(e)}"
            )


# -------------------------------------------
# ✅ Store Transactions in Supabase
# -------------------------------------------
def store_transactions(transactions):
    inserted_count, updated_count = 0, 0

    for tx in transactions:
        try:
            account_id = tx.get("account_id", None)  # Allow NULL account_id
            transaction_date = tx.get("date") or tx.get("authorized_date")  # Ensure date is set
            transaction_name = tx.get("name", "Unknown")  # Ensure name is set
            merchant_name = tx.get("merchant_name", "N/A")  # Ensure merchant_name is set

            # ✅ Debugging Log: Show transaction data before inserting/updating
            print(f"\n🔄 Processing transaction: {tx}")

            # ✅ Prepare transaction data
            tx_data = {
                "transaction_id": tx["transaction_id"],
                "account_id": account_id,
                "amount": tx["amount"],
                "iso_currency_code": tx.get("iso_currency_code", "USD"),
                "merchant_name": merchant_name,
                "name": transaction_name,
                "date": transaction_date,
                "category": ", ".join(tx.get("category", [])) if tx.get("category") else "Uncategorized",
                "plaid_category_id": tx.get("category_id"),
                "pending": tx["pending"],
                "location_address": tx["location"].get("address"),
                "location_city": tx["location"].get("city"),
                "location_region": tx["location"].get("region"),
                "location_postal_code": tx["location"].get("postal_code"),
                "location_country": tx.get("location", {}).get("country"),
                "payment_channel": tx.get("payment_channel"),
                "payment_method": tx.get("payment_meta", {}).get("payment_method"),
                "website": tx.get("website"),
            }

            # ✅ Debugging Log: Show the final transaction data before inserting/updating
            print(f"📝 Prepared transaction data for DB: {tx_data}")

            # ✅ FORCE UPDATE: Insert or update all transactions (no skipping)
            response = supabase.table("transactions").upsert(tx_data).execute()

            if response.data:
                updated_count += 1
                print(f"✅ Inserted/Updated transaction: {tx['transaction_id']}")
            else:
                print(f"❌ FAILED: No response from Supabase for {tx['transaction_id']}")

        except Exception as e:
            print(f"❌ Error storing transaction {tx.get('transaction_id', 'Unknown')}: {str(e)}")

    print(f"\n📊 Transaction sync summary: {updated_count} transactions updated.")


# -------------------------------------------
# ✅ Main Function to Sync Plaid Data
# -------------------------------------------
def main():
    try:
        print("🔄 Fetching accounts from Plaid...")
        accounts = fetch_account_balances()
        if accounts:
            store_account_balances(accounts)
            print("💾 Account synchronization complete.")
        else:
            print("⚠️ No accounts retrieved. Transactions may fail.")

        print("\n🔄 Fetching transactions from Plaid...")
        transactions = fetch_transactions()
        if transactions:
            store_transactions(transactions)
            print("💾 Transaction synchronization complete.")
        else:
            print("⚠️ No transactions retrieved.")

        print("\n🏁 Plaid synchronization completed successfully!")

    except Exception as e:
        print(f"❌ Error in Plaid sync: {str(e)}")
        import traceback
        traceback.print_exc()


# ✅ Run only if executed directly
if __name__ == "__main__":
    main()
