import sqlite3
from sales_report import view_sales_report


def admin_menu():
    while True:
        print("\n🛍️ Admin Panel - Product Management")
        print("1. Add Product")
        print("2. View Products")
        print("3. Update Product")
        print("4. Delete Product")
        print("5. View Sales Report")
        print("6. Logout")
        choice = input("Enter your choice: ")
        if choice == '1':
            add_product()
        elif choice == '2':
            view_products()
        elif choice == '3':
            update_product()
        elif choice == '4':
            delete_product()
        elif choice=='5':
            view_sales_report()
        elif choice == '6':
            print("Logging out from Admin Panel...")
            break
        else:
            print("Invalid choice, please try again.")

def add_product():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    name = input("Enter product name: ")
    price = float(input("Enter price: "))
    unit = input("Enter unit (e.g., kg, litre, packet, dozen): ")
    stock = int(input(f"Enter total stock quantity (in {unit}): "))
    expiry_date = input("Enter expiry date (YYYY-MM-DD) or leave blank: ")

    cursor.execute("INSERT INTO products (name, price, stock, expiry_date, unit) VALUES (?, ?, ?, ?, ?)",
                   (name, price, stock, expiry_date if expiry_date else None, unit))
    conn.commit()
    conn.close()
    print(f"✅ Product '{name}' added successfully at ₹{price}/{unit}!")

def view_products():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, price, stock, expiry_date, unit FROM products")
    products = cursor.fetchall()

    if products:
        print("\n📦 --- Product List ---")
        for prod in products:
            print(f"ID: {prod[0]}, Name: {prod[1]}, Price: ₹{prod[2]}/{prod[5]}, Stock: {prod[3]}, Expiry: {prod[4]}")
    else:
        print("No products found.")

    conn.close()

def update_product():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    product_id = input("Enter product ID to update: ")

    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()

    if product:
        print(f"📝 Current details: Name: {product[1]}, Price: ₹{product[2]}/{product[5]}, Stock: {product[3]}, Expiry: {product[4]}")

        name = input("Enter new name (leave blank to keep current): ") or product[1]
        price_input = input("Enter new price (leave blank to keep current): ")
        price = float(price_input) if price_input else product[2]

        unit = input("Enter new unit (leave blank to keep current): ") or product[5]

        stock_input = input("Enter new stock (leave blank to keep current): ")
        stock = int(stock_input) if stock_input else product[3]

        expiry_date = input("Enter new expiry date (YYYY-MM-DD) or leave blank to keep current: ") or product[4]

        cursor.execute("""
            UPDATE products
            SET name=?, price=?, unit=?, stock=?, expiry_date=?
            WHERE id=?
        """, (name, price, unit, stock, expiry_date, product_id))

        conn.commit()
        print("✅ Product updated successfully!")
    else:
        print("❌ Product not found.")

    conn.close()

def delete_product():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    product_id = input("Enter product ID to delete: ")

    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()

    if product:
        confirm = input(f"Are you sure you want to delete '{product[1]}'? (y/n): ").lower()
        if confirm == 'y':
            cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            print("🗑️ Product deleted successfully.")
        else:
            print("Deletion cancelled.")
    else:
        print("❌ Product not found.")

    conn.close()
