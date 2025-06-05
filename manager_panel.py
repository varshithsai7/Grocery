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

def manager_menu():
    while True:
        print("\n📋 Manager Panel")
        print("1. View All Products")
        print("2. Check Low Stock Items")
        print("3. Check & Auto-Remove Expired Products")
        print("4. Logout")

        choice = input("Enter your choice: ")

        if choice == '1':
            view_products()
        elif choice == '2':
            check_low_stock()
        elif choice == '3':
            check_expiry_products()
        elif choice == '4':
            print("Logging out from Manager Panel...")
            break
        else:
            print("❌ Invalid choice, please try again.")

if __name__ == "__main__":
    manager_menu()
