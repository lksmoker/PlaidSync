import sqlite3
from plaid_sync import DATABASE_FILE

def get_unprocessed_transactions():
    """Retrieve transactions that are not categorized and not ignored."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transaction_id, date, name, amount, iso_currency_code, pending
        FROM transactions
        WHERE user_category_id IS NULL 
        AND (ignored IS NULL OR ignored = 0)
        ORDER BY date DESC;
    """)

    transactions = cursor.fetchall()
    conn.close()

    return transactions

# Test the function
if __name__ == "__main__":
    transactions = get_unprocessed_transactions()
    for tx in transactions:
        print(tx)  # Prints transactions to check if it's working