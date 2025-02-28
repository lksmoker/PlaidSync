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
        ORDER BY date DESC;
    """)

    transactions = cursor.fetchall()
    conn.close()

    return transactions

def find_duplicate_transactions():
    """Find potential duplicate transactions based on same date, amount, and account."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Query that finds transactions with the same date, amount, and account
    cursor.execute("""
        SELECT t1.transaction_id, t1.date, t1.name, t1.amount, t1.iso_currency_code, 
               t2.transaction_id as duplicate_id, t2.name as duplicate_name,
               t1.account_id as account_id
        FROM transactions t1
        JOIN transactions t2 ON t1.date = t2.date AND t1.amount = t2.amount AND t1.account_id = t2.account_id
        WHERE t1.transaction_id < t2.transaction_id  -- Avoid listing the same pair twice
        ORDER BY t1.date DESC, t1.amount;
    """)

    duplicates = cursor.fetchall()

    return duplicates

def flag_duplicate_transactions():
    """Find duplicates and update them with a flag in the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # First, make sure we have a potential_duplicate column
    try:
        cursor.execute("SELECT potential_duplicate FROM transactions LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE transactions ADD COLUMN potential_duplicate INTEGER DEFAULT 0")
        conn.commit()
    
    # Check for confirmed_duplicate column
    try:
        cursor.execute("SELECT confirmed_duplicate FROM transactions LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE transactions ADD COLUMN confirmed_duplicate INTEGER DEFAULT NULL")
        conn.commit()

    # Reset potential duplicate flags but preserve confirmed ones
    cursor.execute("""
        UPDATE transactions 
        SET potential_duplicate = CASE
            WHEN confirmed_duplicate = 1 THEN 1
            ELSE 0
        END
    """)

    # Find duplicates
    duplicates = find_duplicate_transactions()

    # Flag each transaction in duplicate pairs
    flagged_count = 0
    for dup in duplicates:
        tx_id1 = dup[0]
        tx_id2 = dup[5]

        cursor.execute("UPDATE transactions SET potential_duplicate = 1 WHERE transaction_id = ? OR transaction_id = ?", 
                      (tx_id1, tx_id2))
        flagged_count += 2  # Two transactions flagged per pair

    conn.commit()
    conn.close()

    return len(duplicates), flagged_count

# Test the function
if __name__ == "__main__":
    transactions = get_unprocessed_transactions()
    for tx in transactions:
        print(tx)  # Prints transactions to check if it's working

    # Test the duplicate detection and flagging
    print("\n===== POTENTIAL DUPLICATE TRANSACTIONS =====")
    num_pairs, num_flagged = flag_duplicate_transactions()

    if num_pairs == 0:
        print("No duplicate transactions found.")
    else:
        print(f"Found {num_pairs} potential duplicate pairs and flagged {num_flagged} transactions in database.")

        # Show the flagged transactions
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT transaction_id, date, name, amount, iso_currency_code
            FROM transactions
            WHERE potential_duplicate = 1
            ORDER BY date DESC, amount
        """)
        flagged_transactions = cursor.fetchall()
        conn.close()

        print("\n===== FLAGGED TRANSACTIONS =====")
        for tx in flagged_transactions:
            print(f"Date: {tx[1]}, Amount: ${abs(tx[3])}, Name: {tx[2]}, ID: {tx[0]}")

        # Show some detailed duplicate pairs
        print("\n===== DUPLICATE PAIR DETAILS =====")
        duplicates = find_duplicate_transactions()
        for i, dup in enumerate(duplicates[:3]):  # Show first 3 pairs only
            print(f"Pair {i+1}:")
            print(f"  Date: {dup[1]}, Amount: ${abs(dup[3])}, Account: {dup[7]}")
            print(f"  Transaction 1: {dup[2]} (ID: {dup[0]})")
            print(f"  Transaction 2: {dup[6]} (ID: {dup[5]})")
            print("-" * 50)