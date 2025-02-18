import sqlite3
from plaid_sync import DATABASE_FILE  # Use the same database file

# Function to add a category
def add_category(category_name):
    """Adds a new category if it doesn't already exist."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        conn.commit()
        print(f"✅ Category '{category_name}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"⚠️ Category '{category_name}' already exists.")

    conn.close()

# Function to get all categories
def get_categories():
    """Retrieves all user-defined categories."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    conn.close()
    return categories

# Function to delete a category
def delete_category(category_id):
    """Deletes a category by its ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
    conn.commit()

    conn.close()
    print(f"✅ Category with ID {category_id} deleted successfully.")

# Function to assign a category to a transaction
def assign_category(transaction_id, category_id):
    """Assigns a user-defined category to a transaction."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE transactions SET user_category_id = ? WHERE transaction_id = ?
    """, (category_id, transaction_id))

    conn.commit()
    conn.close()
    print(f"✅ Transaction {transaction_id} categorized successfully.")
