import sqlite3

def view_sales_report():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    while True:
        print("\n📊 Sales Report Viewer")
        print("1. View All Sales")
        print("2. View Sales by Date")
        print("3. View Total Revenue")
        print("4. Back")

        choice = input("Enter your choice: ")

        if choice == '1':
            cursor.execute("SELECT sale_date, product_name, quantity, price_per_unit, total_price FROM sales ORDER BY sale_date DESC")
            sales = cursor.fetchall()
            print("\n🧾 All Sales Records:")
            for sale in sales:
                print(f"📅 {sale[0]} | 🛒 {sale[1]} | Qty: {sale[2]} | ₹{sale[3]}/unit | Total: ₹{sale[4]}")

        elif choice == '2':
            date = input("Enter date (YYYY-MM-DD): ")
            cursor.execute("SELECT product_name, quantity, total_price FROM sales WHERE sale_date = ?", (date,))
            sales = cursor.fetchall()
            if sales:
                print(f"\n🗓️ Sales on {date}:")
                for sale in sales:
                    print(f"🛒 {sale[0]} | Qty: {sale[1]} | Total: ₹{sale[2]}")
            else:
                print("No sales on that date.")

        elif choice == '3':
            cursor.execute("SELECT SUM(total_price) FROM sales")
            total = cursor.fetchone()[0]
            print(f"\n💰 Total Revenue So Far: ₹{total:.2f}" if total else "No sales data yet.")

        elif choice == '4':
            break

        else:
            print("❌ Invalid choice.")

    conn.close()
