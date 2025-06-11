import sqlite3

def connect():
    conn = sqlite3.connect("grocery.db")  # creates the db file
    cursor = conn.cursor()

    # Create table: users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT ,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'cashier'))
        )
    """)

    # Create table: products (updated for homepage display)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            expiry_date TEXT,
            unit TEXT NOT NULL,
            image_url TEXT,
            category TEXT
        )
    """)

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

    # Create table: customers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            total_spent REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS last_action (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            action TEXT,
            prev_name TEXT,
            prev_price REAL,
            prev_stock INTEGER,
            prev_unit TEXT,
            prev_expiry TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );

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

def insert_sample_products():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count > 0:
        print("📦 Sample products already exist. Skipping insertion.")
        conn.close()
        return  


    products = [
        # Fruits
        ("Apple", "Fresh Kashmiri apples 🍎", 120.0, 50, "2025-12-31", "kg", "/static/images/apple.jpeg", "Fruits"),
        ("Banana", "Organic bananas 🍌", 40.0, 60, "2025-07-10", "dozen", "/static/images/banana.jpeg", "Fruits"),
        ("Mango", "Sweet Alphonso mangoes 🥭", 150.0, 40, "2025-06-30", "kg", "/static/images/mango.jpeg", "Fruits"),
        ("Orange", "Juicy Nagpur oranges 🍊", 60.0, 70, "2025-08-01", "kg", "/static/images/orange.jpeg", "Fruits"),
        ("Grapes", "Seedless green grapes 🍇", 90.0, 55, "2025-08-15", "kg", "/static/images/grapes.jpeg", "Fruits"),

        # Vegetables
        ("Onion", "Organic red onions 🧅", 40.0, 150, "2025-08-01", "kg", "/static/images/onion.jpeg", "Vegetables"),
        ("Tomato", "Fresh tomatoes 🍅", 35.0, 140, "2025-07-20", "kg", "/static/images/tomato.jpeg", "Vegetables"),
        ("Potato", "Desi aloo 🥔", 25.0, 200, "2025-10-10", "kg", "/static/images/potato.jpeg", "Vegetables"),
        ("Carrot", "Crunchy carrots 🥕", 50.0, 100, "2025-07-01", "kg", "/static/images/carrot.jpeg", "Vegetables"),
        ("Cabbage", "Green cabbage 🥬", 30.0, 80, "2025-06-25", "kg", "/static/images/cabbage.jpeg", "Vegetables"),

        # Grains & Pulses
        ("Tur Dal", "Protein-rich tur dal 🌾", 90.0, 200, "2026-03-10", "kg", "/static/images/turdal.jpeg", "Grains"),
        ("Rice", "Sona masoori rice 🍚", 60.0, 300, "2026-01-01", "kg", "/static/images/rice.jpeg", "Grains"),
        ("Wheat Flour", "Whole wheat atta 🌾", 45.0, 250, "2026-01-01", "kg", "/static/images/wheat.jpeg", "Grains"),
        ("Moong Dal", "Split yellow moong 🌼", 100.0, 180, "2026-02-20", "kg", "/static/images/moongdal.jpeg", "Grains"),
        ("Chana Dal", "Desi chana dal 💛", 85.0, 160, "2026-02-10", "kg", "/static/images/chanadal.jpeg", "Grains"),

        # Dairy
        ("Milk", "Pure cow milk 🥛", 55.0, 100, "2025-06-15", "litre", "/static/images/milk.jpeg", "Dairy"),
        ("Curd", "Homemade curd 🥣", 30.0, 60, "2025-06-16", "cup", "/static/images/curd.jpeg", "Dairy"),
        ("Butter", "Creamy yellow butter 🧈", 120.0, 40, "2025-09-01", "packet", "/static/images/butter.jpeg", "Dairy"),
        ("Ghee", "Desi cow ghee ✨", 550.0, 30, "2026-05-01", "litre", "/static/images/ghee.jpeg", "Dairy"),
        ("Paneer", "Fresh paneer 🍥", 240.0, 25, "2025-06-14", "kg", "/static/images/paneer.jpeg", "Dairy"),

        # Essentials
        ("Toothpaste", "Herbal freshness paste 🌿", 65.0, 80, "2027-01-01", "tube", "/static/images/toothpaste.jpeg", "Essentials"),
        ("Toothbrush", "Soft bristles brush 🪥", 20.0, 100, "2027-01-01", "piece", "/static/images/toothbrush.jpeg", "Essentials"),
        ("Soap", "Ayurvedic body soap 🧼", 35.0, 90, "2026-12-31", "bar", "/static/images/soap.jpeg", "Essentials"),
        ("Shampoo", "Natural hair shampoo 💆‍♀️", 75.0, 70, "2026-10-01", "bottle", "/static/images/shampoo.jpeg", "Essentials"),
        ("Handwash", "Anti-bacterial liquid 🧴", 60.0, 60, "2026-08-15", "bottle", "/static/images/handwash.jpeg", "Essentials"),

        # Snacks
        ("Biscuits", "Glucose biscuits 🍪", 20.0, 100, "2026-06-01", "packet", "/static/images/biscuits.jpeg", "Snacks"),
        ("Chips", "Potato chips pack 🥔", 25.0, 120, "2026-04-10", "packet", "/static/images/chips.jpeg", "Snacks"),
        ("Namkeen", "Spicy namkeen mix 🌶️", 40.0, 90, "2026-07-01", "packet", "/static/images/namkeen.jpeg", "Snacks"),
        ("Chocolate", "Milk chocolate 🍫", 30.0, 70, "2026-12-31", "bar", "/static/images/chocolate.jpeg", "Snacks"),
        ("Juice", "Mixed fruit juice 🧃", 45.0, 80, "2026-06-15", "box", "/static/images/juice.jpeg", "Snacks"),

        # Beverages
        ("Tea", "Premium Assam tea 🍵", 140.0, 100, "2027-01-01", "kg", "/static/images/tea.jpeg", "Beverages"),
        ("Coffee", "South Indian filter coffee ☕", 180.0, 60, "2026-12-01", "kg", "/static/images/coffee.jpeg", "Beverages"),
        ("Green Tea", "Tulsi green tea 🍃", 160.0, 50, "2026-11-01", "box", "/static/images/greentea.jpeg", "Beverages"),
        ("Soft Drink", "Chilled soda 🍹", 35.0, 90, "2025-12-01", "bottle", "/static/images/soda.jpeg", "Beverages"),
        ("Lassi", "Sweet Punjabi lassi 🧉", 25.0, 40, "2025-06-20", "glass", "/static/images/lassi.jpeg", "Beverages"),

        # Cleaning
        ("Detergent", "Clothes detergent powder 🧽", 95.0, 100, "2027-01-01", "packet", "/static/images/detergent.jpeg", "Cleaning"),
        ("Phenyl", "Floor cleaner liquid 🧼", 70.0, 50, "2026-10-10", "bottle", "/static/images/phenyl.jpeg", "Cleaning"),
        ("Dish Wash", "Lemon dish liquid 🍋", 45.0, 60, "2026-08-01", "bottle", "/static/images/dishwash.jpeg", "Cleaning"),
        ("Toilet Cleaner", "Disinfectant for toilets 🚽", 85.0, 40, "2026-09-01", "bottle", "/static/images/toiletcleaner.jpeg", "Cleaning"),
        ("Broom", "Coconut stick broom 🧹", 60.0, 70, "2028-01-01", "piece", "/static/images/broom.jpeg", "Cleaning"),

        # Stationery
        ("Notebook", "College ruled notebook 📓", 35.0, 120, "2029-01-01", "piece", "/static/images/notebook.jpeg", "Stationery"),
        ("Pen", "Blue ink pen ✒️", 10.0, 150, "2029-01-01", "piece", "/static/images/pen.jpeg", "Stationery"),
        ("Pencil", "Wooden pencil ✏️", 5.0, 200, "2029-01-01", "piece", "/static/images/pencil.jpeg", "Stationery"),
        ("Eraser", "Dust-free eraser 🧼", 4.0, 150, "2029-01-01", "piece", "/static/images/eraser.jpeg", "Stationery"),
        ("Sharpener", "Metal blade sharpener 🔪", 8.0, 100, "2029-01-01", "piece", "/static/images/sharpener.jpeg", "Stationery")
    ]

    for p in products:
        cursor.execute("""
            INSERT INTO products (name, description, price, stock, expiry_date, unit, image_url, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

    conn.commit()
    conn.close()
    print("🌼 Sample essentials added.")


def drop_all_tables():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    # List of tables to drop
    tables = ['users', 'products', 'sales', 'customers']

    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"🗑️ Dropped table: {table}")
        except Exception as e:
            print(f"⚠️ Error dropping table {table}: {e}")

    conn.commit()
    conn.close()
    print("✅ All selected tables dropped successfully.")


if __name__ == "__main__":
    connect()
    insert_def_admin()
    insert_sample_products()
    print("✅ Database and tables created successfully.")
    # drop_all_tables()
