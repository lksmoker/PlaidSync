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

# ✅ Fetch transactions from Plaid

def fetch_transactions():
    headers = {"Content-Type": "application/json"}
    start_date = (datetime.today() - timedelta(days=10)).strftime('%Y-%m-%d')
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

# ✅ Fetch account balances from Plaid
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

# ✅ Store account balances in Supabase
def store_account_balances(accounts):
    for account in accounts:
        response = supabase.table("accounts").upsert({
            "id": account["account_id"],
            "name": account["name"],
            "official_name": account.get("official_name", "Unknown"),
            "type": account["type"],
            "subtype": account["subtype"],
            "balance_available": account.get("balances", {}).get("available"),
            "balance_current": account.get("balances", {}).get("current"),
            "iso_currency_code": account.get("balances", {}).get("iso_currency_code", "USD")
        }).execute()

# ✅ Store transactions in Supabase
def store_transactions(transactions):
    for tx in transactions:
        # Ensure account_id exists in accounts before inserting transaction
        account_exists = supabase.table("accounts").select("id").eq("id", tx["account_id"]).execute()
        if not account_exists.data:
            print(f"⚠️ Skipping transaction {tx['transaction_id']} - Account {tx['account_id']} not found.")
            continue

        response = supabase.table("transactions").upsert({
            "transaction_id": tx["transaction_id"],
            "account_id": tx["account_id"],
            "amount": tx["amount"],
            "iso_currency_code": tx.get("iso_currency_code", "USD"),
            "date": tx["date"],
            "name": tx["name"],
            "merchant_name": tx.get("merchant_name"),
            "category": ", ".join(tx.get("category", [])),
            "plaid_category_id": tx.get("category_id"),
            "pending": tx["pending"],
            "location_address": tx["location"].get("address"),
            "location_city": tx["location"].get("city"),
            "location_region": tx["location"].get("region"),
            "location_postal_code": tx["location"].get("postal_code"),
            "location_country": tx["location"].get("country"),
            "user_category_id": None,  # Placeholder
            "ignored": False
        }).execute()

# ✅ Main function to fetch and store transactions & balances
def main():
    print("🔄 Fetching account balances from Plaid...")
    accounts = fetch_account_balances()
    if accounts:
        print(f"✅ Storing {len(accounts)} accounts in Supabase first...")
        store_account_balances(accounts)
        print("💾 Accounts stored successfully.")
    else:
        print("⚠️ No accounts retrieved.")

    print("🔄 Fetching transactions from Plaid...")
    transactions = fetch_transactions()
    if transactions:
        print(f"✅ Storing {len(transactions)} transactions in Supabase...")
        store_transactions(transactions)
        print("💾 Transactions stored successfully.")
    else:
        print("⚠️ No transactions retrieved.")

if __name__ == "__main__":
    main()
