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


            cursor.execute(
                "INSERT INTO sales (product_id, product_name, quantity, price_per_unit, total_price, sale_date) VALUES (?, ?, ?, ?, ?, ?)",
                (product[0], product[1], quantity, product[2], item_total, sale_date)
            )
            conn.commit()

            # Add item info to the cart list
            cart.append((product[1], quantity, product[2], item_total))

            # Add item total to grand total amount
            total_amount += item_total

        except ValueError:
            # Handle non-integer inputs gracefully
            print("⚠️ Invalid input. Please enter valid numbers.")

    # After billing loop ends, print the final bill if cart is not empty
    if cart:
        print("\n🧾 FINAL BILL:")
        print("-" * 40)
        print("{:<15} {:<10} {:<10} {:<10}".format("Item", "Qty", "Rate", "Total"))
        print("-" * 40)
        
        # Display each purchased item's details
        for item in cart:
            print("{:<15} {:<10} ₹{:<9} ₹{:<10}".format(item[0], item[1], item[2], item[3]))
        
        print("-" * 40)
        print(f"💰 Grand Total: ₹{total_amount:.2f}")
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
