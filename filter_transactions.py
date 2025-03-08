import json

# ✅ Load transactions from the saved file
with open("transactions.json", "r") as file:
    data = json.load(file)

# ✅ Extract only pending transactions
pending_transactions = [
    {"date": tx["date"], "name": tx["name"], "amount": tx["amount"], "pending": tx["pending"]}
    for tx in data.get("transactions", [])
    if tx.get("pending") is True
]

# ✅ Print results in a structured format
if pending_transactions:
    from ace_tools import display_dataframe_to_user
    import pandas as pd

    df = pd.DataFrame(pending_transactions)
    display_dataframe_to_user(name="Pending Transactions", dataframe=df)
else:
    print("No pending transactions found.")