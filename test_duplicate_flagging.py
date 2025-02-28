
import sqlite3
from get_transactions import flag_duplicate_transactions

# Database file
DATABASE_FILE = "transactions_dev.db"

def insert_duplicate_transaction():
    """Insert a duplicate of an existing transaction for testing."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # First, get an existing transaction
    cursor.execute("SELECT transaction_id, date, name, amount, iso_currency_code, account_id FROM transactions LIMIT 1")
    transaction = cursor.fetchone()
    
    if not transaction:
        print("❌ No transactions found in the database.")
        conn.close()
        return False
    
    # Create a new transaction ID for the duplicate
    new_transaction_id = transaction[0] + "_duplicate"
    date = transaction[1]
    name = transaction[2]
    amount = transaction[3]
    currency = transaction[4]
    account_id = transaction[5]
    
    # Insert the duplicate transaction
    try:
        cursor.execute("""
            INSERT INTO transactions 
            (transaction_id, date, name, amount, iso_currency_code, pending, user_category_id, ignored, account_id) 
            VALUES (?, ?, ?, ?, ?, 0, NULL, 0, ?)
        """, (new_transaction_id, date, name, amount, currency, account_id))
        
        conn.commit()
        
        print(f"✅ Inserted duplicate transaction:")
        print(f"Original Transaction ID: {transaction[0]}")
        print(f"Duplicate Transaction ID: {new_transaction_id}")
        print(f"Date: {date}, Amount: ${abs(amount)}, Name: {name}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error inserting duplicate: {e}")
        conn.close()
        return False

def test_duplicate_flagging():
    """Test the duplicate flagging functionality."""
    # Insert a duplicate transaction
    if not insert_duplicate_transaction():
        return
    
    print("\n===== RUNNING DUPLICATE DETECTION =====")
    # Run the flagging function
    num_pairs, num_flagged = flag_duplicate_transactions()
    
    if num_pairs == 0:
        print("❌ No duplicate transactions found, something went wrong.")
    else:
        print(f"✅ Found {num_pairs} potential duplicate pairs and flagged {num_flagged} transactions in database.")
        
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

if __name__ == "__main__":
    test_duplicate_flagging()
