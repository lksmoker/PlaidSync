
import sqlite3
import uuid
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
    
    # Create a completely unique transaction ID
    new_transaction_id = f"test_dup_{str(uuid.uuid4())}"
    date = transaction[1]
    name = transaction[2]
    amount = transaction[3]
    currency = transaction[4]
    account_id = transaction[5]
    
    # First, check if our test transaction already exists to avoid multiple test runs
    cursor.execute("DELETE FROM transactions WHERE transaction_id LIKE 'test_dup_%'")
    conn.commit()
    
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
        print(f"Account ID: {account_id}")
        
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
            SELECT transaction_id, date, name, amount, iso_currency_code, account_id
            FROM transactions
            WHERE potential_duplicate = 1
            ORDER BY date DESC, amount
        """)
        flagged_transactions = cursor.fetchall()
        
        print("\n===== FLAGGED TRANSACTIONS =====")
        for tx in flagged_transactions:
            print(f"Date: {tx[1]}, Amount: ${abs(tx[3])}, Name: {tx[2]}, ID: {tx[0]}, Account: {tx[5]}")
            
        # Show duplicate pairs
        cursor.execute("""
            SELECT t1.transaction_id, t1.date, t1.name, t1.amount, 
                   t2.transaction_id, t2.name, t1.account_id
            FROM transactions t1
            JOIN transactions t2 ON t1.date = t2.date AND t1.amount = t2.amount AND t1.account_id = t2.account_id
            WHERE t1.transaction_id < t2.transaction_id
            AND t1.potential_duplicate = 1 AND t2.potential_duplicate = 1
        """)
        pairs = cursor.fetchall()
        
        print("\n===== DUPLICATE PAIRS =====")
        for i, pair in enumerate(pairs):
            print(f"Pair {i+1}:")
            print(f"  Date: {pair[1]}, Amount: ${abs(pair[3])}, Account: {pair[6]}")
            print(f"  Transaction 1: {pair[2]} (ID: {pair[0]})")
            print(f"  Transaction 2: {pair[5]} (ID: {pair[4]})")
            print("-" * 50)
            
        conn.close()

if __name__ == "__main__":
    test_duplicate_flagging()
