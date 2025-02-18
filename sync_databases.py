import sqlite3

# File paths for production and development databases
PROD_DB = "transactions_prod.db"
DEV_DB = "transactions_dev.db"

def sync_transactions():
    """Sync transactions from production to development database."""
    print("🔄 Starting database sync...")

    # Connect to the development database
    dev_conn = sqlite3.connect(DEV_DB)
    dev_cursor = dev_conn.cursor()

    # Attach the production database
    dev_cursor.execute(f"ATTACH DATABASE '{PROD_DB}' AS prod;")

    # Copy only new transactions (skip existing ones)
    dev_cursor.execute("""
        INSERT INTO transactions
        SELECT * FROM prod.transactions
        WHERE transaction_id NOT IN (SELECT transaction_id FROM transactions);
    """)

    dev_conn.commit()
    dev_conn.close()

    print("✅ Sync complete! Development database is now up to date.")

if __name__ == "__main__":
    sync_transactions()
