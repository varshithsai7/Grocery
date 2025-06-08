import sqlite3

def create_new_tables():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    # 📜 Sales Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            sale_date TEXT,
            total_amount REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    # 📦 Sales Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            price_per_unit REAL,
            total_price REAL,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Add this before creating tables in set_tables.py
    


    print("✅ New tables 'sales' and 'sales_items' created successfully!")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_new_tables()
