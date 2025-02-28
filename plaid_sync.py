import os
import requests
import sqlite3
from datetime import datetime, timedelta

# Load Plaid credentials securely from Replit Secrets
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Determine which database to use (development vs. production)
DATABASE_FILE = "transactions_dev.db" if os.getenv("ENV") == "development" else "transactions_prod.db"

# API endpoints
PLAID_TRANSACTIONS_URL = "https://sandbox.plaid.com/transactions/get"
PLAID_ACCOUNTS_URL = "https://sandbox.plaid.com/accounts/get"

# Function to set up the SQLite database
def setup_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Create transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT,
            amount REAL,
            iso_currency_code TEXT,
            date TEXT,
            name TEXT,
            merchant_name TEXT,
            category TEXT,
            category_id TEXT,
            pending BOOLEAN,
            location_address TEXT,
            location_city TEXT,
            location_region TEXT,
            location_postal_code TEXT,
            location_country TEXT,
            user_category_id INTEGER,
            ignored BOOLEAN DEFAULT 0  -- ✅ Ensure ignored column exists
        )
    """)

    # Create accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            name TEXT,
            official_name TEXT,
            type TEXT,
            subtype TEXT,
            balance_available REAL,
            balance_current REAL,
            iso_currency_code TEXT
        )
    """)

    # Create categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# ✅ Function to fetch transactions from Plaid (Only Last 10 Days)
def fetch_transactions():
    headers = {"Content-Type": "application/json"}

    # ✅ Dynamically set start and end dates (last 10 days)
    start_date = (datetime.today() - timedelta(days=10)).strftime('%Y-%m-%d')
    end_date = datetime.today().strftime('%Y-%m-%d')

    print(f"📅 Fetching transactions from {start_date} to {end_date}")

    payload = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "access_token": ACCESS_TOKEN,
        "start_date": start_date,
        "end_date": end_date,  # ✅ Fetches only last 10 days
        "options": {"count": 500}  # ✅ Fetch more transactions
    }

    response = requests.post(PLAID_TRANSACTIONS_URL, json=payload, headers=headers)

    if response.status_code == 200:
        transactions = response.json().get("transactions", [])
        print(f"✅ Fetched {len(transactions)} transactions.")
        return transactions
    else:
        print("❌ Error fetching transactions:", response.json())
        return []

# Function to store transactions in the database
def store_transactions(transactions):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    for tx in transactions:
        cursor.execute("""
            INSERT OR REPLACE INTO transactions (
                transaction_id, account_id, amount, iso_currency_code, date, 
                name, merchant_name, category, category_id, pending, 
                location_address, location_city, location_region, location_postal_code, location_country, ignored
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tx["transaction_id"], tx["account_id"], tx["amount"], tx.get("iso_currency_code", "USD"),
            tx["date"], tx["name"], tx.get("merchant_name"), " > ".join(tx.get("category", [])),
            tx.get("category_id"), int(tx["pending"]),  # ✅ Ensure BOOLEAN values are stored as 0/1
            tx["location"].get("address"), tx["location"].get("city"), tx["location"].get("region"),
            tx["location"].get("postal_code"), tx["location"].get("country"), 0  # ✅ Default ignored = 0
        ))

    conn.commit()
    conn.close()

# Function to fetch account balances from Plaid
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

# Function to store account balances in SQLite
def store_account_balances(accounts):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    for account in accounts:
        cursor.execute("""
            INSERT OR REPLACE INTO accounts (
                account_id, name, official_name, type, subtype, 
                balance_available, balance_current, iso_currency_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account["account_id"], account["name"], account.get("official_name", ""),
            account["type"], account["subtype"], account.get("balances", {}).get("available"),
            account.get("balances", {}).get("current"), account.get("balances", {}).get("iso_currency_code", "USD")
        ))

    conn.commit()
    conn.close()

# ✅ Main function to fetch and store transactions & balances
def main():
    print(f"📂 Using database: {DATABASE_FILE}")

    print("🛠 Setting up database...")
    setup_database()

    print("🔄 Fetching transactions from Plaid...")
    transactions = fetch_transactions()

    if transactions:
        print(f"✅ Fetched {len(transactions)} transactions. Storing in database...")
        store_transactions(transactions)
        print("💾 Transactions stored successfully.")
    else:
        print("⚠️ No transactions retrieved.")

    print("🔄 Fetching account balances from Plaid...")
    accounts = fetch_account_balances()

    if accounts:
        print(f"✅ Fetched {len(accounts)} accounts. Storing balances...")
        store_account_balances(accounts)
        print("💾 Account balances stored successfully.")
    else:
        print("⚠️ No accounts retrieved.")

if __name__ == "__main__":
    main()
