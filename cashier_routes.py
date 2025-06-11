from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import sqlite3
from datetime import datetime

cashier_bp = Blueprint('cashier',"varshith", template_folder='templates')

def get_db_connection():
    conn = sqlite3.connect("grocery.db")
    conn.row_factory = sqlite3.Row
    return conn

@cashier_bp.route('/cashier')
def cashier_dashboard():
    if session.get("role") != "cashier":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))
    return render_template("cashier_dashboard.html")

@cashier_bp.route('/cashier/products')
def cashier_view_products():
    conn = get_db_connection()
    products = conn.execute("SELECT id, name, price, stock FROM products").fetchall()
    conn.close()
    return render_template("cashier_view_products.html", products=products)

@cashier_bp.route('/cashier/bill', methods=['GET', 'POST'])
def cashier_generate_bill():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        items = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')

        cursor.execute("SELECT id, total_spent FROM customers WHERE phone = ?", (phone,))
        customer = cursor.fetchone()

        if customer:
            customer_id, total_spent = customer
        else:
            cursor.execute("INSERT INTO customers (name, phone, total_spent) VALUES (?, ?, 0)", (name, phone))
            conn.commit()
            customer_id = cursor.lastrowid
            total_spent = 0

        cart = []
        total_amount = 0

        for i in range(len(items)):
            product_id = int(items[i])
            quantity = int(quantities[i])

            cursor.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()

            if product and quantity <= product[3]:
                cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
                conn.commit()

                total_price = product[2] * quantity
                cart.append((product_id, product[1], quantity, product[2], total_price))
                total_amount += total_price

        is_loyal = total_spent >= 1000
        discount = 0

        if is_loyal:
            discount = total_amount * 0.2
            total_amount -= discount

        sale_date = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        cursor.execute("INSERT INTO sales (customer_id, sale_date, total_amount) VALUES (?, ?, ?)",
                       (customer_id, sale_date, total_amount))
        conn.commit()
        sale_id = cursor.lastrowid

        for item in cart:
            cursor.execute("INSERT INTO sales_items (sale_id, product_id, product_name, quantity, price_per_unit, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                           (sale_id, item[0], item[1], item[2], item[3], item[4]))
        conn.commit()
        cursor.execute("UPDATE customers SET total_spent = total_spent + ? WHERE id = ?", (total_amount, customer_id))
        conn.commit()
        conn.close()

        return render_template("cashier_bill_result.html", cart=cart, subtotal=total_amount + discount, discount=discount, final_amount=total_amount)

    products = conn.execute("SELECT id, name, price, stock FROM products").fetchall()
    conn.close()
    return render_template("cashier_generate_bill.html", products=products)
