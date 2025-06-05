import sqlite3
import datetime

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

def manager_menu():
    while True:
        print("\n📋 Manager Panel")
        print("1. View All Products")
        print("2. Check Low Stock Items")
        print("3. Check & Auto-Remove Expired Products")
        print("4. Restock Low Quantity Products")
        print("5. Logout")

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
            print("Logging out from Manager Panel...")
            break
        else:
            print("❌ Invalid choice, please try again.")

if __name__ == "__main__":
    manager_menu()
