import sqlite3

def connect():
    conn = sqlite3.connect("grocery.db")  # creates the db file
    cursor = conn.cursor()

    # Create table: users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Create table: products (with 'unit' added)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            expiry_date TEXT,
            unit TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# Add a default admin user
def insert_def_admin():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    # Check if admin exists
    cursor.execute("SELECT * FROM users WHERE role='admin'")
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('varshith', 'admin123', 'admin'))
        conn.commit()
        print("🌟 Default admin added.")
    else:
        print("👑 Admin already exists.")

    conn.close()

if __name__ == "__main__":
    connect()
    print("✅ Database and tables created successfully.")
    insert_def_admin()
