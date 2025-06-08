import sqlite3
from datetime import datetime

# Function to display all available products with their stock and price
def view_products():
    conn = sqlite3.connect("grocery.db")  # Connect to SQLite database
    cursor = conn.cursor()
    
    # Fetch product id, name, price, and stock from the products table
    cursor.execute("SELECT id, name, price, stock FROM products")
    products = cursor.fetchall()  # Get all products

    if products:
        print("\n🧾 Available Products:")
        # Print each product with details
        for p in products:
            print(f"ID: {p[0]} | Name: {p[1]} | ₹{p[2]} | Stock: {p[3]}")
    else:
        print("No products available.")
    conn.close()  # Close DB connection


# Function to handle billing process by adding products to the cart and calculating totals
def generate_bill():
    conn = sqlite3.connect("grocery.db")  # Connect to DB
    cursor = conn.cursor()

    # 📌 Show all available products before billing begins
    cursor.execute("SELECT id, name, price, stock FROM products")
    products = cursor.fetchall()

    if products:
        print("\n🛍️ Available Products Before Billing:")
        for p in products:
            print(f"ID: {p[0]} | Name: {p[1]} | ₹{p[2]} | Stock: {p[3]}")
    else:
        print("No products available.")
        conn.close()
        return 
    
    # customer id,name etc adding to table
    name = input("Enter customer's name: ")
    phone = input("Enter customer's phone number: ")

    # Check if customer exists
    cursor.execute("SELECT id, total_spent FROM customers WHERE phone = ?", (phone,))
    customer = cursor.fetchone()

    if not customer:
        cursor.execute("INSERT INTO customers (name, phone, total_spent) VALUES (?, ?, 0)", (name, phone))
        conn.commit()
        customer_id = cursor.lastrowid
    else:
        customer_id = customer[0]
        total_spent = customer[1]


    cart = []          # Empty cart to store purchased items
    total_amount = 0.0 # Initialize total amount to zero

    while True:
        product_id = input("\nEnter product ID to add (or 'done' to finish): ")
        if product_id.lower() == 'done':  # Exit billing loop when done
            break

        try:
            product_id = int(product_id)  # Convert input to int
            
            # Fetch product details by ID
            cursor.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()

            if not product:  # If product doesn't exist
                print("❌ Product not found.")
                continue

            quantity = int(input(f"Enter quantity for {product[1]}: "))  # Ask for quantity

            # Check if requested quantity is available in stock
            if quantity > product[3]:
                print("⚠️ Not enough stock available.")
                continue

            # Deduct quantity from stock in the database
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
            conn.commit()

            # Calculate total price for this item
            item_total = product[2] * quantity
            
            # add to sales table
            sale_date = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')


            

            # Add item info to the cart list
            cart.append((product[1], quantity, product[2], item_total))

            # Add item total to grand total amount
            total_amount += item_total

        
        except ValueError:
            # Handle non-integer inputs gracefully
            print("⚠️ Invalid input. Please enter valid numbers.")

        
         
    # Check if eligible for reward
    cursor.execute("SELECT total_spent FROM customers WHERE id = ?", (customer_id,))
    total = cursor.fetchone()[0]
    is_loyal = total >= 1000

    # After billing loop ends, print the final bill if cart is not empty
    if cart:
    
        sale_date = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')

        # Insert overall sale
        cursor.execute(
            "INSERT INTO sales (customer_id, sale_date, total_amount) VALUES (?, ?, ?)",
            (customer_id, sale_date, total_amount)
        )
        conn.commit()
        sale_id = cursor.lastrowid  # Get the ID of the inserted sale

        # Insert each item in sales_items table
        for item in cart:
            product_name, quantity, price_per_unit, total_price = item
            cursor.execute(
                "INSERT INTO sales_items (sale_id, product_name, quantity, price_per_unit, total_price) VALUES (?, ?, ?, ?, ?)",
                (sale_id, product_name, quantity, price_per_unit, total_price)
            )
        conn.commit()

        print("\n🧾 FINAL BILL:")
        print("-" * 40)
        print("{:<15} {:<10} {:<10} {:<10}".format("Item", "Qty", "Rate", "Total"))
        print("-" * 40)
        
        # Display each purchased item's details
        for item in cart:
            print("{:<15} {:<10} ₹{:<9} ₹{:<10}".format(item[0], item[1], item[2], item[3]))
        
        print("-" * 40)
        print(f"💰 Subtotal: ₹{total_amount:.2f}")

        if is_loyal:
            discount = total_amount * 0.20
            total_amount -= discount
            print(f"🎁 Loyal Customer Discount (20%): -₹{discount:.2f}")
            print(f"🛒 Final Amount to Pay: ₹{total_amount:.2f}")
        else:
            print(f"🛒 Total Amount to Pay: ₹{total_amount:.2f}")
        
        # update total spent to customers
        cursor.execute("UPDATE customers SET total_spent = total_spent + ? WHERE id = ?", (total_amount, customer_id))
        conn.commit()

    
        # Show date and time of billing
        print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 40)
    else:
        print("No items billed.")

    conn.close()  # Close DB connection


# Main menu function for cashier operations
def cashier_menu():
    while True:
        print("\n💼 Cashier Panel")
        print("1. View Available Products")
        print("2. Generate Customer Bill")
        print("3. Logout")

        choice = input("Enter your choice: ")

        # Call respective functions based on user's choice
        if choice == '1':
            view_products()
        elif choice == '2':
            generate_bill()
        elif choice == '3':
            print("Logging out from Cashier Panel...")
            break
        else:
            print("❌ Invalid choice. Try again.")

# Run the cashier menu only if this file is executed directly
if __name__ == "__main__":
    cashier_menu() 