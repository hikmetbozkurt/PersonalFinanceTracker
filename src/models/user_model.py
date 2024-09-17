import sqlite3
import bcrypt

# Database setup and connection
def connect_db():
    connection = sqlite3.connect("db/finance_tracker.db")
    return connection

def create_users_table():
    """Create the users table if it doesn't exist"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    connection.commit()
    connection.close()

def create_transactions_table():
    """Create the transactions table if it doesn't exist"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        type TEXT NOT NULL,  -- 'income' or 'expense'
        date TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    connection.commit()
    connection.close()

# Password handling functions (hashing, verification, etc.)
def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(stored_password, provided_password):
    """Verify the stored hashed password against the provided password"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def create_user(username, password):
    """Create a new user with a hashed password"""
    connection = connect_db()
    cursor = connection.cursor()

    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        connection.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        connection.close()

    return True

def authenticate_user(username, password):
    """Authenticate the user by comparing the hashed password"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    connection.close()

    if user:
        user_id, stored_password = user
        if verify_password(stored_password, password):
            return user_id  # Return the user_id upon successful authentication
    return None  # Return None if authentication fails


def add_transaction(user_id, amount, category, transaction_type, date, description):
    """Add a new transaction to the database"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions (user_id, amount, category, type, date, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, amount, category, transaction_type, date, description))

    connection.commit()
    connection.close()

def get_transactions(user_id):
    """Get all transactions for a specific user"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC
    """, (user_id,))
    transactions = cursor.fetchall()

    connection.close()
    return transactions

def get_financial_summary(user_id):
    """Get the total income and total expenses for the logged-in user"""
    try:
        # Use 'with' to ensure the connection is closed properly, even if an error occurs
        with connect_db() as connection:
            cursor = connection.cursor()

            # Calculate total income
            cursor.execute("""
                SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'income'
            """, (user_id,))
            total_income = cursor.fetchone()[0] or 0  # Use 0 if there are no income transactions

            # Calculate total expenses
            cursor.execute("""
                SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'expense'
            """, (user_id,))
            total_expenses = cursor.fetchone()[0] or 0  # Use 0 if there are no expense transactions

        # Return both values
        return total_income, total_expenses

    except Exception as e:
        print(f"An error occurred while fetching the financial summary: {e}")
        return 0, 0  # Return 0 for both income and expenses in case of an error

def delete_transaction(transaction_id):
    """Delete a transaction from the database by its transaction ID"""
    try:
        with connect_db() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            connection.commit()
        print(f"Transaction {transaction_id} deleted successfully.")
    except Exception as e:
        print(f"An error occurred while deleting transaction: {e}")

