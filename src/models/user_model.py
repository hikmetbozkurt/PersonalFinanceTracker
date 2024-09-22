# user_model.py

import sqlite3
import bcrypt
import csv

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

def create_categories_table():
    """Create the categories table if it doesn't exist"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        UNIQUE(user_id, name),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    connection.commit()
    connection.close()

def create_tags_table():
    """Create the tags table if it doesn't exist"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        UNIQUE(user_id, name),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    connection.commit()
    connection.close()

def create_transaction_tags_table():
    """Create the transaction_tags table if it doesn't exist"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaction_tags (
        transaction_id INTEGER,
        tag_id INTEGER,
        FOREIGN KEY (transaction_id) REFERENCES transactions(id),
        FOREIGN KEY (tag_id) REFERENCES tags(id),
        PRIMARY KEY (transaction_id, tag_id)
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

def add_category(user_id, category_name):
    """Add a new category for the user"""
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO categories (user_id, name)
            VALUES (?, ?)
        """, (user_id, category_name))
        connection.commit()
    except sqlite3.IntegrityError:
        # Category already exists for this user
        return False
    finally:
        connection.close()

    return True

def get_categories(user_id):
    """Retrieve all categories for a specific user"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name FROM categories WHERE user_id = ?
    """, (user_id,))
    categories = [row[0] for row in cursor.fetchall()]

    connection.close()
    return categories

def add_tag(user_id, tag_name):
    """Add a new tag for the user"""
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO tags (user_id, name)
            VALUES (?, ?)
        """, (user_id, tag_name))
        connection.commit()
    except sqlite3.IntegrityError:
        # Tag already exists for this user
        pass  # Ignore if the tag already exists
    finally:
        connection.close()

def get_tag_id(user_id, tag_name):
    """Retrieve the tag ID for a given tag name and user"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id FROM tags WHERE user_id = ? AND name = ?
    """, (user_id, tag_name))
    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]
    else:
        return None

def add_tags_to_transaction(transaction_id, tags, user_id):
    """Associate tags with a transaction"""
    connection = connect_db()
    cursor = connection.cursor()

    try:
        for tag_name in tags:
            # Ensure the tag exists
            cursor.execute("""
                SELECT id FROM tags WHERE user_id = ? AND name = ?
            """, (user_id, tag_name))
            result = cursor.fetchone()
            if result:
                tag_id = result[0]
            else:
                # Tag does not exist, create it
                cursor.execute("""
                    INSERT INTO tags (user_id, name)
                    VALUES (?, ?)
                """, (user_id, tag_name))
                tag_id = cursor.lastrowid

            # Associate tag with transaction
            try:
                cursor.execute("""
                    INSERT INTO transaction_tags (transaction_id, tag_id)
                    VALUES (?, ?)
                """, (transaction_id, tag_id))
            except sqlite3.IntegrityError:
                # Association already exists
                pass

        connection.commit()
    finally:
        connection.close()

def add_transaction(user_id, amount, category, transaction_type, date, description):
    """Add a new transaction to the database"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions (user_id, amount, category, type, date, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, amount, category, transaction_type, date, description))

    transaction_id = cursor.lastrowid  # Get the ID of the inserted transaction

    connection.commit()
    connection.close()

    return transaction_id

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
            # Also delete related tags
            cursor.execute("DELETE FROM transaction_tags WHERE transaction_id = ?", (transaction_id,))
            connection.commit()
        print(f"Transaction {transaction_id} deleted successfully.")
    except Exception as e:
        print(f"An error occurred while deleting transaction: {e}")

def get_expenses_by_category(user_id):
    """Get expenses grouped by category for a specific user."""
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE user_id = ? AND type = 'expense'
        GROUP BY category
    """, (user_id,))
    result = cursor.fetchall()
    connection.close()
    return {category: total for category, total in result}

def export_transactions_to_csv(user_id, filename):
    """Export user's transactions to a CSV file."""
    transactions = get_transactions(user_id)

    if not transactions:
        return False  # No transactions to export

    fieldnames = ['ID', 'User ID', 'Price', 'Category', 'Type', 'Date', 'Description']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for transaction in transactions:
            writer.writerow(transaction)

    return True

def get_transactions_filtered(user_id, category=None, tags=[]):
    """Retrieve transactions filtered by category and tags"""
    connection = connect_db()
    cursor = connection.cursor()

    params = [user_id]
    query = """
        SELECT DISTINCT t.*
        FROM transactions t
    """

    joins = ""
    conditions = " WHERE t.user_id = ?"

    if tags:
        joins += """
            JOIN transaction_tags tt ON t.id = tt.transaction_id
            JOIN tags tg ON tt.tag_id = tg.id
        """
        conditions += " AND tg.name IN ({})".format(','.join('?' * len(tags)))
        params.extend(tags)

    if category:
        conditions += " AND t.category = ?"
        params.append(category)

    query += joins + conditions + " ORDER BY t.date DESC"

    cursor.execute(query, params)
    transactions = cursor.fetchall()

    connection.close()
    return transactions

def get_tags_for_transaction(transaction_id):
    """Retrieve tags associated with a transaction"""
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT tg.name
        FROM tags tg
        JOIN transaction_tags tt ON tg.id = tt.tag_id
        WHERE tt.transaction_id = ?
    """, (transaction_id,))
    tags = [row[0] for row in cursor.fetchall()]

    connection.close()
    return tags

def delete_category(user_id, category_name):
    connection = connect_db()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            DELETE FROM categories WHERE user_id = ? AND name = ?
        """, (user_id, category_name))
        connection.commit()
        return True
    except Exception as e:
        print(f"An error occurred while deleting category: {e}")
        return False
    finally:
        connection.close()

