import sqlite3
from datetime import datetime
import time

def view_products():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock FROM products")
    products = cursor.fetchall()

    if products:
        print("\n🧾 Available Products:")
        for p in products:
            print(f"ID: {p[0]} | Name: {p[1]} | ₹{p[2]} | Stock: {p[3]}")
    else:
        print("No products available.")
    conn.close()

def generate_bill():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, price, stock FROM products")
    products = cursor.fetchall()

    if not products:
        print("No products available.")
        conn.close()
        return

    print("\n🛍️ Available Products:")
    for p in products:
        print(f"ID: {p[0]} | Name: {p[1]} | ₹{p[2]} | Stock: {p[3]}")

    name = input("Enter customer's name: ")
    phone = input("Enter customer's phone number: ")

    # Check for existing customer
    cursor.execute("SELECT id, total_spent FROM customers WHERE phone = ?", (phone,))
    customer = cursor.fetchone()

    if not customer:
        cursor.execute("INSERT INTO customers (name, phone, total_spent) VALUES (?, ?, 0)", (name, phone))
        conn.commit()
        customer_id = cursor.lastrowid
        total_spent = 0
    else:
        customer_id = customer[0]
        total_spent = customer[1]

    cart = []
    total_amount = 0.0

    while True:
        product_id = input("\nEnter product ID (or 'done' to finish): ")
        if product_id.lower() == 'done':
            break

        try:
            product_id = int(product_id)
            cursor.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()

            if not product:
                print("❌ Product not found.")
                continue

            quantity = int(input(f"Enter quantity for {product[1]}: "))
            if quantity > product[3]:
                print("⚠️ Not enough stock.")
                continue

            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
            conn.commit()

            item_total = product[2] * quantity
            cart.append((product_id, product[1], quantity, product[2], item_total))
            total_amount += item_total

        except ValueError:
            print("⚠️ Invalid input. Please enter valid numbers.")

    is_loyal = total_spent >= 1000

    if cart:
        sale_date = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        cursor.execute(
            "INSERT INTO sales (customer_id, sale_date, total_amount) VALUES (?, ?, ?)",
            (customer_id, sale_date, total_amount)
        )
        conn.commit()
        sale_id = cursor.lastrowid

        for item in cart:
            product_id, name, quantity, price_per_unit, total_price = item
            cursor.execute(
                "INSERT INTO sales_items (sale_id, product_id, product_name, quantity, price_per_unit, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                (sale_id, product_id, name, quantity, price_per_unit, total_price)
            )
        conn.commit()

        print("\n🧾 FINAL BILL:")
        print("-" * 40)
        print("{:<15} {:<10} {:<10} {:<10}".format("Item", "Qty", "Rate", "Total"))
        print("-" * 40)
        for item in cart:
            print("{:<15} {:<10} ₹{:<9} ₹{:<10}".format(item[1], item[2], item[3], item[4]))
        print("-" * 40)
        print(f"💰 Subtotal: ₹{total_amount:.2f}")

        if is_loyal:
            discount = total_amount * 0.20
            total_amount -= discount
            print(f"🎁 Loyal Customer Discount (20%): -₹{discount:.2f}")
            print(f"🛒 Final Amount to Pay: ₹{total_amount:.2f}")
        else:
            print(f"🛒 Total Amount to Pay: ₹{total_amount:.2f}")

        cursor.execute("UPDATE customers SET total_spent = total_spent + ? WHERE id = ?", (total_amount, customer_id))
        conn.commit()
        print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 40)
    else:
        print("No items billed.")

    conn.close()

def cashier_menu():
    while True:
        print("\n💼 Cashier Panel")
        print("1. View Available Products")
        print("2. Generate Customer Bill")
        print("3. Logout")

        choice = input("Enter your choice: ")

        if choice == '1':
            view_products()
        elif choice == '2':
            generate_bill()
        elif choice == '3':
            print("Logging out from Cashier Panel...")
            break
        else:
            print("❌ Invalid choice. Try again.")
        time.sleep(1)

if __name__ == "__main__":
    cashier_menu()
