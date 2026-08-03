import sqlite3

DB_NAME = "prices.db"

def create_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        name TEXT,
        price REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        price REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        query TEXT NOT NULL,
        UNIQUE(chat_id, query))""")

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        
    connection.commit()
    connection.close()

def save_price(product):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO price_history (product_id, name, price) VALUES (?,?,?)""", (product["id"], product["name"], product["price"]))
    connection.commit()
    connection.close()

def get_last_price(product_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""SELECT price from price_history WHERE product_id=? ORDER BY date DESC LIMIT 1 OFFSET 1""", (product_id,))

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]
    return None

def was_notification_sent(product_id, price):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    cursor.execute("""SELECT id from notifications WHERE product_id=? and price = ? """, (product_id, price))
    result = cursor.fetchone()
    
    connection.close()
    return result is not None


def save_notification(product_id, price):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO notifications (product_id, price) VALUES (?,?)""", (product_id, price))
    connection.commit()
    connection.close()

    
def add_query(chat_id, query):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""INSERT OR IGNORE INTO search_queries(chat_id, query) VALUES (?, ?)""", (chat_id, query))
    connection.commit()
    connection.close()

def get_queries(chat_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""SELECT query from search_queries WHERE chat_id = ?""", (chat_id,))

    rows = cursor.fetchall()

    connection.close()

    return [row[0] for row in rows]

def get_queries_with_id(chat_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""SELECT id, query from search_queries WHERE chat_id = ? ORDER BY id""", (chat_id,))

    rows = cursor.fetchall()

    connection.close()

    return rows

def delete_query(chat_id, query_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""DELETE FROM search_queries WHERE id = ? AND chat_id = ?""", (query_id, chat_id))

    deleted = cursor.rowcount
    connection.commit()
    connection.close()

    return deleted

def add_user(chat_id, username):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""INSERT OR IGNORE INTO users(chat_id, username) VALUES (?, ?)""", (chat_id, username))

    connection.commit()
    connection.close()

def user_exists(chat_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""SELECT id from users WHERE chat_id = ?""", (chat_id,))

    user = cursor.fetchone()

    connection.close()

    return user is not None

def get_users():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""SELECT chat_id from users """)

    users = cursor.fetchall()

    connection.close()

    return [user[0] for user in users]
