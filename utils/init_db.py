import sqlite3
import os
import uuid
import datetime
from werkzeug.security import generate_password_hash

# Database file path
DATABASE = 'instance/revobank.db'

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

# Remove existing database file if it exists
if os.path.exists(DATABASE):
    os.remove(DATABASE)

# Create and connect to the database
conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Read and execute schema.sql
with open('schema.sql', 'r') as f:
    cursor.executescript(f.read())

# Create sample users
users = [
    {
        'id': str(uuid.uuid4()),
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': generate_password_hash('password123'),
        'phone': '+1234567890',
        'is_admin': True,
        'created_at': datetime.datetime.now()
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'Jane Smith',
        'email': 'jane@example.com',
        'password':  generate_password_hash('password456'),
        'phone': '+0987654321',
        'is_admin': False,
        'created_at': datetime.datetime.now()
    }
]

# Insert users
for user in users:
    cursor.execute(
        "INSERT INTO users (id, name, email, password, phone, is_admin, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user['id'], user['name'], user['email'], user['password'], user['phone'], user['is_admin'], user['created_at'])
    )

# Create sample accounts
accounts = []
for user in users:
    # Checking account
    checking_id = str(uuid.uuid4())
    accounts.append({
        'id': checking_id,
        'user_id': user['id'],
        'account_name': 'Primary Checking',
        'account_type': 'checking',
        'currency': 'USD',
        'balance': 5000.00,
        'created_at': datetime.datetime.now()
    })
    
    # Savings account
    savings_id = str(uuid.uuid4())
    accounts.append({
        'id': savings_id,
        'user_id': user['id'],
        'account_name': 'Savings',
        'account_type': 'savings',
        'currency': 'USD',
        'balance': 10000.00,
        'created_at': datetime.datetime.now()
    })

# Insert accounts
for account in accounts:
    cursor.execute(
        """INSERT INTO accounts 
           (id, user_id, account_name, account_type, currency, balance, created_at) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (account['id'], account['user_id'], account['account_name'], account['account_type'], 
         account['currency'], account['balance'], account['created_at'])
    )

# Create sample transactions for each account
for account in accounts:
    # Deposit transaction
    deposit_id = str(uuid.uuid4())
    cursor.execute(
        """INSERT INTO transactions 
           (id, account_id, transaction_type, amount, description, transaction_date) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (deposit_id, account['id'], 'deposit', 1000.00, 'Initial deposit', 
         datetime.datetime.now() - datetime.timedelta(days=30))
    )
    # Withdrawal transaction
    withdrawal_id = str(uuid.uuid4())
    cursor.execute(
        """INSERT INTO transactions 
           (id, account_id, transaction_type, amount, description, transaction_date) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (withdrawal_id, account['id'], 'withdrawal', 200.00, 'ATM withdrawal', 
         datetime.datetime.now() - datetime.timedelta(days=15))
    )

# For the first user, add a transfer between checking and savings
if len(accounts) >= 2:
    # Transfer from checking to savings
    source_id = accounts[0]['id']
    dest_id = accounts[1]['id']
    # Source transaction
    source_transaction_id = str(uuid.uuid4())
    dest_transaction_id = str(uuid.uuid4())
    # Add source transaction
    cursor.execute(
        """INSERT INTO transactions 
           (id, account_id, transaction_type, amount, description, transaction_date, linked_transaction_id) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (source_transaction_id, source_id, 'transfer', 500.00, 'Transfer to savings', 
         datetime.datetime.now() - datetime.timedelta(days=7), dest_transaction_id)
    )
    # Add destination transaction
    cursor.execute(
        """INSERT INTO transactions 
           (id, account_id, transaction_type, amount, description, transaction_date, linked_transaction_id) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (dest_transaction_id, dest_id, 'deposit', 500.00, 'Transfer from checking', 
         datetime.datetime.now() - datetime.timedelta(days=7), source_transaction_id)
    )

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database initialized successfully with sample data!")
print(f"Database file created at: {os.path.abspath(DATABASE)}")
print("\nSample user credentials:")
for user in users:
    print(f"Email: {user['email']}, user_id: {user['id']}")
for account in accounts:
    print(f"id: {account['id']}, user_id: {account['user_id']}, Balance: {account['balance']}")
    