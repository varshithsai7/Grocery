import sqlite3
import datetime
from sales_report import view_sales_report


def view_products():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, price, stock, expiry_date FROM products")
    products = cursor.fetchall()

    if products:
        print("\n🧾 Product List:")
        for prod in products:
            print(f"ID: {prod[0]}, Name: {prod[1]}, Price: ₹{prod[2]}, Stock: {prod[3]}, Expiry: {prod[4]}")
    else:
        print("No products found.")

    conn.close()

def check_low_stock(threshold=3):
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, stock FROM products WHERE stock <= ?", (threshold,))
    products = cursor.fetchall()

    if products:
        print("\n⚠️ Low Stock Alert (≤ 3 units):")
        print("You need to reorder the following items:")
        for prod in products:
            print(f"🔄 {prod[1]} – Only {prod[2]} left ❗")
        print("📦 Action: Please restock these items soon.")
    else:
        print("✅ All products are above the safe stock level.")

    conn.close()

def check_expiry_products():
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, expiry_date FROM products WHERE expiry_date IS NOT NULL AND expiry_date < ?", (today,))
    expired = cursor.fetchall()

    if expired:
        print("\n🚫 Expired Products Found and Removed:")
        for prod in expired:
            print(f"❌ {prod[1]} (Expired on: {prod[2]}) - Removed")
            cursor.execute("DELETE FROM products WHERE id = ?", (prod[0],))
        conn.commit()
    else:
        print("✅ No expired products found.")

    conn.close()

def restock_product():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    # Show all products
    cursor.execute("SELECT id, name, stock, unit FROM products")
    products = cursor.fetchall()

    if not products:
        print("❌ No products found.")
        conn.close()
        return

    print("\n📦 Available Products:")
    for prod in products:
        print(f"ID: {prod[0]} | {prod[1]} | Stock: {prod[2]} {prod[3]}")

    # Show low stock products (optional highlight)
    print("\n⚠️ Low Stock Products (≤ 3 units):")
    low_stock_found = False
    for prod in products:
        if prod[2] <= 3:
            print(f"🔴 {prod[1]} (ID: {prod[0]}) – Only {prod[2]} {prod[3]} left")
            low_stock_found = True
    if not low_stock_found:
        print("✅ All stocks are currently above safe levels.")

    # Ask directly for restocking input
    try:
        product_id = int(input("\nEnter the ID of the product you want to restock: "))
        cursor.execute("SELECT name, stock, unit FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        if not product:
            print("❌ Product ID not found.")
            conn.close()
            return

        add_qty = int(input(f"Enter quantity to add (in {product[2]}): "))
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (add_qty, product_id))
        conn.commit()
        print(f"✅ Stock updated for {product[0]}. New quantity: {product[1] + add_qty} {product[2]}")

    except ValueError:
        print("⚠️ Invalid input. Please enter valid numbers.")

    conn.close()

def add_product():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    print("\n➕ Add New Product")
    name = input("Enter product name: ").strip()
    if not name:
        print("❌ Product name cannot be empty.")
        conn.close()
        return

    try:
        price = float(input("Enter product price (₹): "))
        if price < 0:
            raise ValueError
    except ValueError:
        print("❌ Invalid price entered.")
        conn.close()
        return

    try:
        stock = int(input("Enter initial stock quantity: "))
        if stock < 0:
            raise ValueError
    except ValueError:
        print("❌ Invalid stock quantity entered.")
        conn.close()
        return

    unit = input("Enter unit (e.g., pcs, kg, liters): ").strip()
    if not unit:
        unit = "pcs"  # default unit if none entered

    expiry_date = input("Enter expiry date (YYYY-MM-DD) or leave blank if none: ").strip()
    if expiry_date:
        try:
            expiry_obj = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
            if expiry_obj <= datetime.date.today():
                print("❌ Expiry date must be in the future.")
                conn.close()
                return
        except ValueError:
            print("❌ Invalid expiry date format.")
            conn.close()
            return
    else:
        expiry_date = None

    cursor.execute("""
        INSERT INTO products (name, price, stock, unit, expiry_date)
        VALUES (?, ?, ?, ?, ?)
    """, (name, price, stock, unit, expiry_date))
    conn.commit()
    print(f"✅ Product '{name}' added successfully.")
    conn.close()


def update_product():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    try:
        product_id = int(input("\nEnter the ID of the product you want to update: "))
    except ValueError:
        print("❌ Invalid product ID.")
        conn.close()
        return

    cursor.execute("SELECT name, price, stock, unit, expiry_date FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        print("❌ Product not found.")
        conn.close()
        return

    print(f"\nUpdating Product: {product[0]}")
    print("Press enter to keep the current value.")

    # Get new values or keep old
    new_name = input(f"New name [{product[0]}]: ").strip() or product[0]

    price_input = input(f"New price (₹) [{product[1]}]: ").strip()
    if price_input:
        try:
            new_price = float(price_input)
            if new_price < 0:
                raise ValueError
        except ValueError:
            print("❌ Invalid price entered.")
            conn.close()
            return
    else:
        new_price = product[1]

    stock_input = input(f"New stock quantity [{product[2]}]: ").strip()
    if stock_input:
        try:
            new_stock = int(stock_input)
            if new_stock < 0:
                raise ValueError
        except ValueError:
            print("❌ Invalid stock quantity.")
            conn.close()
            return
    else:
        new_stock = product[2]

    new_unit = input(f"New unit [{product[3]}]: ").strip() or product[3]

    expiry_input = input(f"New expiry date (YYYY-MM-DD) [{product[4]}]: ").strip()
    if expiry_input:
        try:
            expiry_obj = datetime.datetime.strptime(expiry_input, "%Y-%m-%d").date()
            if expiry_obj <= datetime.date.today():
                print("❌ Expiry date must be in the future.")
                conn.close()
                return
            new_expiry = expiry_input
        except ValueError:
            print("❌ Invalid expiry date format.")
            conn.close()
            return
    else:
        new_expiry = product[4]

    cursor.execute("""
        UPDATE products
        SET name = ?, price = ?, stock = ?, unit = ?, expiry_date = ?
        WHERE id = ?
    """, (new_name, new_price, new_stock, new_unit, new_expiry, product_id))
    conn.commit()
    print(f"✅ Product '{new_name}' updated successfully.")
    conn.close()

def search_products():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    query = input("\nEnter product name or ID to search: ").strip()
    if query.isdigit():
        cursor.execute("SELECT id, name, price, stock, expiry_date, unit FROM products WHERE id = ?", (int(query),))
    else:
        cursor.execute("SELECT id, name, price, stock, expiry_date, unit FROM products WHERE name LIKE ?", ('%' + query + '%',))

    results = cursor.fetchall()
    if results:
        print("\n🔍 Search Results:")
        for prod in results:
            print(f"ID: {prod[0]}, Name: {prod[1]}, Price: ₹{prod[2]}, Stock: {prod[3]} {prod[5]}, Expiry: {prod[4]}")
    else:
        print("No matching products found.")

    conn.close()


def loyal_customers_report(min_spent=1000):
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, phone, total_spent FROM customers WHERE total_spent >= ? ORDER BY total_spent DESC", (min_spent,))
    customers = cursor.fetchall()

    if customers:
        print(f"\n🎖️ Loyal Customers (Spent ≥ ₹{min_spent}):")
        print("-" * 40)
        print("{:<20} {:<15} {:<10}".format("Name", "Phone", "Total Spent"))
        print("-" * 40)
        for cust in customers:
            print(f"{cust[0]:<20} {cust[1]:<15} ₹{cust[2]:<10.2f}")
        print("-" * 40)
    else:
        print(f"No customers found with spending ≥ ₹{min_spent}.")

    conn.close()

def backup_database():
    import shutil
    import os

    src = "grocery.db"
    backup_folder = "backup"
    os.makedirs(backup_folder, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_folder, f"grocery_backup_{timestamp}.db")

    try:
        shutil.copy2(src, backup_file)
        print(f"✅ Database backup successful: {backup_file}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def manager_audit_log(action, details):
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manager_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            details TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("INSERT INTO manager_audit (action, details, timestamp) VALUES (?, ?, ?)", (action, details, timestamp))
    conn.commit()
    conn.close()


def view_audit_log():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, action, details, timestamp FROM manager_audit ORDER BY timestamp DESC")
    logs = cursor.fetchall()

    if logs:
        print("\n📜 Manager Audit Log:")
        print("-" * 60)
        for log in logs:
            print(f"[{log[3]}] ID:{log[0]} - {log[1]} - {log[2]}")
        print("-" * 60)
    else:
        print("No audit logs found.")

    conn.close()



def manager_menu():
    while True:
        print("\n📋 Manager Panel")
        print("1. View All Products")
        print("2. Check Low Stock Items")
        print("3. Check & Auto-Remove Expired Products")
        print("4. Restock Low Quantity Products")
        print("5. Add New Product")
        print("6. Update Product Details")
        print("7. Search Products")
        print("8. View Sales Report")
        print("9. Loyal Customers Report")
        print("10. Backup Database")
        print("11. View Audit Log")
        print("12. Logout")

        choice = input("Enter your choice: ")

        if choice == '1':
            view_products()
        elif choice == '2':
            check_low_stock()
        elif choice == '3':
            check_expiry_products()
        elif choice == '4':
            restock_product()
        elif choice == '5':
            add_product()
            manager_audit_log("Add", "Added new product")
        elif choice == '6':
            update_product()
            manager_audit_log("Update", "Updated product details")
        elif choice == '7':
            search_products()
            manager_audit_log("Search", "Searched products")
        elif choice == '8':
            view_sales_report()
            manager_audit_log("View", "Viewed sales report")
        elif choice == '9':
            loyal_customers_report()
            manager_audit_log("View", "Viewed loyal customers report")
        elif choice == '10':
            backup_database()
            manager_audit_log("Backup", "Backed up database")
        elif choice == '11':
            view_audit_log()
        elif choice == '12':
            print("Logging out from Manager Panel...")
            break
        else:
            print("❌ Invalid choice, please try again.")

if __name__ == "__main__":
    manager_menu()
