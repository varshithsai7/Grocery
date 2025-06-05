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

    # create sales table
    # Create table: sales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            total_price REAL NOT NULL,
            sale_date TEXT NOT NULL
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        total_spent REAL DEFAULT 0
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
    sample_users = [
        ('manager1', 'manager123', 'manager'),
        ('manager2', 'manager123', 'manager'),
        ('cashier1', 'cashier123', 'cashier'),
    ]

    for username, password, role in sample_users:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (username, password, role))
            print(f"✅ Default {role} user '{username}' added.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    connect()
    print("✅ Database and tables created successfully.")
    insert_def_admin()
