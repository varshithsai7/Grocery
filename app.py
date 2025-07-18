from contextlib import contextmanager
import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import sqlite3
from auth import validate_user
from bs4 import BeautifulSoup
import requests, os, re
from PIL import Image
from io import BytesIO



app = Flask("MyGRow", static_url_path='/static')
import os
# app.secret_key = 'varsh'
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key')


# explicit closing
def close_open_connection(conn):
    try:
        conn.close()
    except:
        pass




@contextmanager
def get_db_connection():
    conn = sqlite3.connect("grocery.db", timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# savelast option
def save_last_action(product_id, action_type):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, stock, unit, expiry_date FROM products WHERE id = ?", (product_id,))
        prev = cursor.fetchone()
        if prev:
            cursor.execute("""
                INSERT INTO last_action (product_id, action, prev_name, prev_price, prev_stock, prev_unit, prev_expiry)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (product_id, action_type, *prev)
            )


# helper function for admin log action
# Audit Log Helper
def log_action(conn, action):
    if 'username' in session and 'role' in session:
        user = session['username']
        role = session['role']
    else:
        user = 'Unknown'
        role = 'Unknown'

    conn.execute(
        "INSERT INTO audit_log (action, user, role) VALUES (?, ?, ?)",
        (action, user, role)
    )




# Helper function to get all products from the database
def get_all_products():
    conn = sqlite3.connect('grocery.db')  # Assuming your DB is named grocery.db
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, price, unit, image_url FROM products")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    products = []
    for row in rows:
        products.append({
            'name': row[0],
            'description': row[1],
            'price_per_unit': row[2],
            'unit': row[3],
            'image_url': row[4]
        })
    return products

# Homepage route
@app.route('/')
def home():
    products = get_all_products()
    return render_template('home.html', products=products)  # Show homepage with product list

# Billing page route
@app.route('/bill')
def bill():
    return render_template('bill.html')

@app.route('/products')
def show_products():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, unit, image_url, category FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template("products.html", products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = validate_user(username, password)
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]

            if user[2] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[2] == 'manager':
                return redirect(url_for('manager_dashboard'))
            elif user[2] == 'cashier':
                return redirect(url_for('cashier_dashboard'))
        else:
            flash('❌ Invalid username or password')
            return redirect(url_for("login"))
    return render_template('home.html')



# admin user add delete 
# 👥 Admin View All Users
@app.route('/admin/users')
def view_users():
    if 'role' in session and session['role'] == 'admin':
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users")
            users = cursor.fetchall()
        return render_template('admin_users.html', users=users)
    return redirect('/login')


# ➕ Admin Add User
@app.route('/admin/add-user', methods=['GET', 'POST'])
def add_user():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']

            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                   (username, password, role))
                    conn.commit()

                    # 🌿 Log the action using the same connection
                    log_action(conn, f"Added user '{username}' with role '{role}'")
                    
                flash('✅ User added successfully!', 'success')
                return redirect('/admin/users')

            except sqlite3.IntegrityError:
                flash('❌ Username already exists.', 'danger')
                
        return render_template('admin_add_user.html')
    return redirect('/login')



# ✏️ Admin Edit User
@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'role' in session and session['role'] == 'admin':
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if request.method == 'POST':
                new_role = request.form['role']
                new_password = request.form['password']

                cursor.execute("UPDATE users SET password=?, role=? WHERE id=?",
                               (new_password, new_role, user_id))
                
                # 🔒 Commit first to save user update
                conn.commit()

                # 📜 Log using same connection
                log_action(conn, f"Updated user ID {user_id} to role '{new_role}' with password '{new_password}'")
                
                flash('✅ User updated successfully!', 'success')
                return redirect('/admin/users')

            cursor.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,))
            user = cursor.fetchone()
        return render_template('admin_edit_user.html', user=user)
    return redirect('/login')



# 🗑️ Admin Delete User
@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'role' in session and session['role'] == 'admin':
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
            user = cursor.fetchone()

            if user:
                username = user[0]
                cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
                
                # 🌼 Log using same connection
                log_action(conn, f"Deleted user '{username}'")

                conn.commit()

                flash(f'🗑️ User "{username}" deleted successfully!', 'success')
        return redirect('/admin/users')
    return redirect('/login')

# admin to get audit details
@app.route('/admin/audit-log')
def audit_log():
    if 'role' in session and session['role'] == 'admin':
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, action, user, role, timestamp FROM audit_log ORDER BY timestamp DESC")
            logs = cursor.fetchall()
        return render_template('admin_audit_log.html', logs=logs)
    return redirect('/login')




@app.route('/admin')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html')
    return redirect(url_for("login"))

@app.route('/cashier')
def cashier_dashboard():
    if 'role' in session and session['role'] == 'cashier':
        return render_template('cashier_dashboard.html')
    return redirect(url_for("login"))

@app.route('/manager')
def manager_dashboard():
    if 'role' in session and session['role'] == 'manager':
        return render_template('manager_dashboard.html')
    return redirect(url_for("login"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            unit = request.form['unit']
            stock = int(request.form['stock'])
            expiry_date = request.form['expiry_date']
            image_url = request.form['image_url']

            conn = sqlite3.connect('grocery.db')
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO products (name, description, price, unit, stock, expiry_date, image_url)
                              VALUES (?, ?, ?, ?, ?, ?, ?)""",
                           (name, description, price, unit, stock, expiry_date, image_url))
            conn.commit()
            conn.close()
            flash("✅ Product added successfully!", "success")
            return redirect('/admin')
        return render_template('add_product.html')
    return redirect('/login')


@app.route('/admin/products')
def admin_products():
    if 'role' in session and session['role'] == 'admin':
        conn = sqlite3.connect('grocery.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, unit, stock, expiry_date FROM products")
        rows = cursor.fetchall()
        conn.close()

        products = [{
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'unit': row[3],
            'stock': row[4],
            'expiry_date': row[5]
        } for row in rows]

        return render_template('admin_products.html', products=products)
    return redirect('/login')


@app.route('/admin/delete-product/<int:product_id>')
def delete_product(product_id):
    if 'role' in session and session['role'] == 'admin':
        conn = sqlite3.connect('grocery.db')
        cursor = conn.cursor()

        # Prevent deletion if sold before
        cursor.execute("SELECT COUNT(*) FROM sales_items WHERE product_id = ?", (product_id,))
        if cursor.fetchone()[0] > 0:
            flash("⚠️ Cannot delete product. It has been sold before.", "danger")
            conn.close()
            return redirect('/admin/products')

        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        flash("🗑️ Product deleted successfully!", "success")
        return redirect('/admin/products')
    return redirect('/login')

# delete sale item
@app.route('/admin/delete-sale/<int:sale_item_id>', methods=['POST'])
def delete_sale_entry(sale_item_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    # Delete the item from sales_items
    cursor.execute("DELETE FROM sales_items WHERE id = ?", (sale_item_id,))

    # Optional: Clean up any orphan sales with no items left
    cursor.execute("""
        DELETE FROM sales
        WHERE id NOT IN (SELECT sale_id FROM sales_items)
    """)

    conn.commit()
    conn.close()

    return redirect('/admin/sales-report')




@app.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'role' in session and session['role'] == 'admin':
        conn = sqlite3.connect('grocery.db')
        cursor = conn.cursor()

        if request.method == 'POST':
            name = request.form['name']
            price = float(request.form['price'])
            unit = request.form['unit']
            stock = int(request.form['stock'])
            expiry_date = request.form['expiry_date']

            cursor.execute("""
                UPDATE products SET name=?, price=?, unit=?, stock=?, expiry_date=?
                WHERE id=?
            """, (name, price, unit, stock, expiry_date, product_id))
            conn.commit()
            conn.close()
            flash("✅ Product updated successfully!", "success")
            return redirect('/admin/products')

        cursor.execute("SELECT id, name, price, unit, stock, expiry_date FROM products WHERE id=?", (product_id,))
        row = cursor.fetchone()
        conn.close()

        product = {
            'id': row[0], 'name': row[1], 'price': row[2],
            'unit': row[3], 'stock': row[4], 'expiry_date': row[5]
        }

        return render_template('edit_product.html', product=product)
    return redirect('/login')


@app.route('/admin/sales-report')
def view_sales_report():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    # Sales table for the full report
    cursor.execute("""
        SELECT si.id, p.name, si.quantity, p.price, (si.quantity * p.price), s.sale_date as total
        FROM sales_items si
        JOIN products p ON si.product_id = p.id
        JOIN sales s ON si.sale_id = s.id
    """)
    report = cursor.fetchall()

    # Separate chart data
    cursor.execute("""
        SELECT p.name, SUM(s.quantity) AS total_quantity, SUM(s.quantity * p.price) AS total_revenue
        FROM sales_items s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY total_quantity DESC

    """)
    chart_data = cursor.fetchall()

    # Prepare chart data lists
    product_names = [row[0] for row in chart_data]
    product_quantities = [row[1] for row in chart_data]
    product_revenues = [row[2] for row in chart_data]

    conn.close()

    return render_template("admin_sales_report.html",
                           report=report,
                           product_names=product_names,
                           product_quantities=product_quantities,
                           product_revenues=product_revenues)


# preview images
@app.route('/manager/fetch_preview_images/<int:product_id>')
def fetch_preview_images(product_id):
    headers = {"User-Agent": "Mozilla/5.0"}

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"images": []})

        product_name = row[0]

    query = '+'.join(product_name.split())
    url = f"https://www.google.com/search?q={query}&tbm=isch"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    images = soup.find_all("img")

    urls = []
    for img in images:
        src = img.get("src")
        if src and src.startswith("http"):
            urls.append(src)
        if len(urls) >= 5:
            break

    return jsonify({"images": urls})


## ✅ Route to View All Products for Minute Updates
@app.route('/manager/update_minute_details_select')
def update_minute_details_select():
    if 'role' not in session or session['role'] != 'manager':
        return redirect('/login')

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category FROM products")
        products = cursor.fetchall()

    return render_template('manager_update_select.html', products=products)

# ✅ Function to Fetch Image Without API from Google Images
def fetch_image_without_api(product_name, save_path):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = '+'.join(product_name.split())
    url = f"https://www.google.com/search?q={query}&tbm=isch"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    images = soup.find_all("img")
    for img in images:
        src = img.get("src")
        if src and src.startswith("http"):
            try:
                img_data = requests.get(src).content
                img_file = Image.open(BytesIO(img_data)).convert("RGB")
                img_file.save(save_path, format="JPEG")
                return True
            except:
                continue
    return False

# ✅ Route to Update Description, Category, and Image for Individual Product
@app.route('/manager/update_minute_details/<int:product_id>', methods=['GET', 'POST'])
def update_minute_details(product_id):
    if 'role' not in session or session['role'] != 'manager':
        return redirect('/login')

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        if not product:
            flash("❌ Product not found.", "danger")
            return redirect('/manager/dashboard')

        safe_name = product[1].lower().replace(' ', '_')
        local_filename = f"{safe_name}.jpeg"
        local_path = os.path.join('static', 'images', local_filename)
        local_url = f"/static/images/{local_filename}"

        if request.method == 'POST':
            update_fields = request.form.getlist('update_fields')
            image_mode = request.form.get('image_mode')
            image_url_input = request.form['image_url'].strip()
            new_description = request.form['description']
            new_category = request.form['category']

            try:
                if 'image' in update_fields:
                    if image_mode == "fetch_google":
                        # Now using preview-selected image URL from form
                        if image_url_input.startswith("http"):
                            response = requests.get(image_url_input)
                            img = Image.open(BytesIO(response.content)).convert("RGB")
                            img.save(local_path, format="JPEG")
                            image_url_input = local_url
                        else:
                            flash("❌ Invalid image URL selected.", "danger")
                    elif image_mode == "manual_url" and image_url_input.startswith("http"):
                        response = requests.get(image_url_input)
                        img = Image.open(BytesIO(response.content)).convert("RGB")
                        img.save(local_path, format="JPEG")
                        image_url_input = local_url
                    else:
                        image_url_input = product[7]

                    cursor.execute("UPDATE products SET image_url = ? WHERE id = ?", (image_url_input, product_id))

                if 'description' in update_fields:
                    cursor.execute("UPDATE products SET description = ? WHERE id = ?", (new_description, product_id))

                if 'category' in update_fields:
                    cursor.execute("UPDATE products SET category = ? WHERE id = ?", (new_category, product_id))

                conn.commit()
                flash("✅ Selected details updated successfully!", "success")
                return redirect(f'/manager/update_minute_details/{product_id}')

            except Exception as e:
                flash(f"❌ Update failed: {e}", "danger")

        return render_template('manager_updateminutedetails.html', product=product)

# manager features
@app.route('/manager/products')
def manager_view_products():
    if 'role' in session and session['role'] == 'manager':
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, price, stock, expiry_date, unit, image_url 
                FROM products
                ORDER BY name ASC
            """)
            products = cursor.fetchall()

        return render_template("manager_products.html", products=products)

    return redirect('/login')


@app.route('/manager/low-stock')
def manager_low_stock():
    if 'role' in session and session['role'] == 'manager':
        try:
            threshold = int(request.args.get('limit', 3))  # default is 3 if not specified
        except ValueError:
            threshold = 3  # fallback if someone passes a non-integer

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, stock, unit FROM products WHERE stock <= ?", (threshold,))
            low_stock_products = cursor.fetchall()

        return render_template("manager_low_stock.html", products=low_stock_products, threshold=threshold)

    return redirect('/login')

@app.route('/manager/expired-products')
def manager_expired_products():
    if 'role' in session and session['role'] == 'manager':
        today = datetime.date.today().isoformat()

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Step 1: Fetch expired products
            cursor.execute("""
                SELECT id, name, expiry_date 
                FROM products 
                WHERE expiry_date IS NOT NULL AND expiry_date < ?
            """, (today,))
            expired = cursor.fetchall()

            # Step 2: Delete and log
            for prod in expired:
                cursor.execute("DELETE FROM products WHERE id = ?", (prod[0],))
                log_manager_action("Deleted Expired Product", f"ID: {prod[0]}, Name: {prod[1]}, Expired: {prod[2]}", conn)

        flash(f"🗑️ {len(expired)} expired products deleted successfully!", "success")
        return render_template("manager_expired_products.html", expired_products=expired)

    return redirect('/login')



@app.route('/manager/undo', methods=['POST'])
def manager_undo():
    if 'role' in session and session['role'] != 'manager':
        return redirect('/login')

    with get_db_connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, product_id, action, prev_name, prev_price, prev_stock, prev_unit, prev_expiry
            FROM last_action
            ORDER BY id DESC LIMIT 1
        """)
        last = cursor.fetchone()

        if not last:
            flash("⚠️ No action to undo.", "warning")
            return redirect(url_for('manager_update_interface'))

        action_id, product_id, action, name, price, stock, unit, expiry = last

        try:
            if action == 'delete':
                cursor.execute("""
                    INSERT INTO products (id, name, price, stock, unit, expiry_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (product_id, name, price, stock, unit, expiry))
                log_manager_action("Undo Delete", f"Restored product '{name}' (ID: {product_id})", conn)

            elif action == 'update':
                cursor.execute("""
                    UPDATE products SET name=?, price=?, stock=?, unit=?, expiry_date=?
                    WHERE id=?
                """, (name, price, stock, unit, expiry, product_id))
                log_manager_action("Undo Update", f"Reverted product '{name}' (ID: {product_id})", conn)

            elif action == 'increment':
                cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (product_id,))
                log_manager_action("Undo Increment", f"Decreased stock of product ID {product_id}", conn)

            elif action == 'decrement':
                cursor.execute("UPDATE products SET stock = stock + 1 WHERE id = ?", (product_id,))
                log_manager_action("Undo Decrement", f"Increased stock of product ID {product_id}", conn)

            # Delete this action from the undo log
            cursor.execute("DELETE FROM last_action WHERE id = ?", (action_id,))
            conn.commit()
            flash("🧙 Undo successful. Product list updated!", "success")

        except Exception as e:
            flash(f"❌ Undo failed: {str(e)}", "danger")

    return redirect(url_for('manager_update_interface'))


@app.route('/manager/restock', methods=['GET', 'POST'])
def manager_restock():
    if 'role' in session and session['role'] == 'manager':
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if request.method == 'POST':
                product_id = request.form['product_id']
                quantity = int(request.form['quantity'])

                cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
                log_manager_action("Restocked Product", f"Product ID {product_id}, Quantity Added: {quantity}", conn)

                flash("✅ Stock updated successfully!", "success")
                return redirect('/manager/restock')

            cursor.execute("SELECT id, name, stock, unit FROM products")
            products = cursor.fetchall()

        return render_template("manager_restock.html", products=products)

    return redirect('/login')

@app.route('/manager/add_product', methods=['GET', 'POST'])
def manager_add_product():
    if 'role' in session and session['role'] == 'manager':
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            stock = int(request.form['stock'])
            unit = request.form['unit']
            expiry_date = request.form['expiry_date'] or None
            image_url = request.form['image_url']
            category = request.form['category']

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products (name, description, price, stock, unit, expiry_date, image_url, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, description, price, stock, unit, expiry_date, image_url, category))

                product_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO last_action (product_id, action, prev_name, prev_price, prev_stock, prev_unit, prev_expiry)
                    VALUES (?, 'delete', ?, ?, ?, ?, ?)
                """, (product_id, name, price, stock, unit, expiry_date))

                log_manager_action("Added Product", f"Name: {name}, Price: ₹{price}, Stock: {stock}", conn)

                flash("✅ Product added successfully!", "success")
                return redirect('/manager/add_product')

        return render_template("manager_add_product.html")

    return redirect('/login')



# update action for incrementing decrement in updation interface or modifications
@app.route('/manager/update_action', methods=['POST'])
def manager_update_action():
    try:
        product_id = int(request.form['product_id'])
        action = request.form['action'].lower()

        with sqlite3.connect("grocery.db", timeout=5) as conn:
            conn.execute("PRAGMA busy_timeout = 5000;")
            cursor = conn.cursor()

            cursor.execute("SELECT name, price, stock, unit, expiry_date FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()

            if not product:
                flash("Product not found!", "error")
                return redirect(url_for('manager_update_interface'))

            if action == 'increment':
                cursor.execute("UPDATE products SET stock = stock + 1 WHERE id = ?", (product_id,))
            elif action == 'decrement':
                cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0", (product_id,))
            elif action == 'delete':
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            else:
                flash("Invalid action received!", "error")
                return redirect(url_for('manager_update_interface'))

            # Log change
            cursor.execute("""
                INSERT INTO last_action (product_id, action, prev_name, prev_price, prev_stock, prev_unit, prev_expiry)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (product_id, action, *product)
            )

        flash('Action performed!', 'success')

    except sqlite3.OperationalError as e:
        flash("⚠️ Database is busy. Please wait and try again.", "error")
    except Exception as e:
        flash(f"Unexpected error: {str(e)}", "error")

    return redirect(url_for('manager_update_interface'))

# ------------------- Update Product -------------------
@app.route('/manager/update-product/<int:product_id>', methods=['GET', 'POST'])
def manager_update_product(product_id):
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        price = float(request.form.get('price') or 0)
        stock = int(request.form.get('stock') or 0)
        expiry_date = request.form.get('expiry_date') or None
        unit = request.form.get('unit', '')
        image_url = request.form.get('image_url', '')
        category = request.form.get('category', '')

        cursor.execute('''
            UPDATE products 
            SET name=?, description=?, price=?, stock=?, expiry_date=?, unit=?, image_url=?, category=?
            WHERE id=?
        ''', (name, description, price, stock, expiry_date, unit, image_url, category, product_id))

        conn.commit()
        conn.close()
        flash("✅ Product updated successfully!", "success")
        return redirect(url_for('manager_view_products'))

    cursor.execute("SELECT name, description, price, stock, expiry_date, unit, image_url, category FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        product = {
            "name": row[0] or '',
            "description": row[1] or '',
            "price": row[2] or 0,
            "stock": row[3] or 0,
            "expiry_date": row[4] or '',
            "unit": row[5] or '',
            "image_url": row[6] or '',
            "category": row[7] or ''
        }
        return render_template("manager_update_product.html", product=product)
    else:
        return "⚠️ Product not found", 404


@app.route('/manager/update_productinfo', methods=['POST'])
def manager_update_product_fields():
    product_id = request.form['product_id']
    name = request.form['name']
    price = request.form['price']
    stock = request.form['stock']
    unit = request.form['unit']
    expiry = request.form['expiry_date']

    conn = sqlite3.connect('grocery.db')
    cursor = conn.cursor()

    # Get current product data for logging
    cursor.execute("SELECT name, price, stock, unit, expiry_date FROM products WHERE id = ?", (product_id,))
    old_data = cursor.fetchone()

    # Log the update
    cursor.execute("""
    INSERT INTO last_action (product_id, action, prev_name, prev_price, prev_stock, prev_unit, prev_expiry)
    VALUES (?, 'update', ?, ?, ?, ?, ?)
""", (product_id, *old_data))

    if old_data:
    # Now update the product
        cursor.execute("""
            UPDATE products
            SET name = ?, price = ?, stock = ?, unit = ?, expiry_date = ?
            WHERE id = ?
        """, (name, price, stock, unit, expiry, product_id))

    conn.commit()
    conn.close()
    flash('Product details updated successfully!', 'success')
    return redirect(url_for('manager_update_interface'))



# modify interfave
@app.route('/manager/update-interface', methods=['GET', 'POST'])
def manager_update_interface():
    if 'role' in session and session['role'] == 'manager':
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if request.method == 'POST':
                action = request.form['action']
                product_id = int(request.form.get('product_id'))

                cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
                original = cursor.fetchone()

                if original:
                    # 🌟 Backup before any update/delete
                    cursor.execute("""
                        INSERT INTO last_action (product_id, action, name, price, stock, unit, expiry_date, description, image_url, category)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        product_id, action, original[1], original[2], original[3], original[4],
                        original[5], original[6], original[7], original[8]
                    ))

                    if action == 'increment':
                        cursor.execute("UPDATE products SET stock = stock + 1 WHERE id = ?", (product_id,))
                        log_manager_action("Incremented Stock", f"Product ID {product_id}", conn)
                    elif action == 'decrement':
                        cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (product_id,))
                        log_manager_action("Decremented Stock", f"Product ID {product_id}", conn)
                    elif action == 'delete':
                        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                        log_manager_action("Deleted Product", f"Product ID {product_id}", conn)

                flash("🔄 Update performed. Undo available!", "info")
                return redirect('/manager/update-interface')

            # GET: Show products
            cursor.execute("SELECT id, name, price, stock, unit, expiry_date, image_url FROM products")
            products = cursor.fetchall()
            return render_template('manager_update_interface.html', products=products)

    return redirect('/login')



# manager see last actions
@app.route('/manager/last_actions')
def manager_last_actions():
    if 'role' in session and session['role'] == 'manager':
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT product_id, action, prev_name, prev_price, prev_stock, prev_unit, prev_expiry, timestamp
                FROM last_action
                ORDER BY timestamp DESC
                LIMIT 20
            """)
            actions = cursor.fetchall()
        return render_template('manager_last_actions.html', actions=actions)
    return redirect(url_for('login'))




# ------------------- Search Products -------------------
@app.route('/manager/search-products', methods=['GET', 'POST'])
def manager_search_products():
    if 'role' in session and session['role'] == 'manager':
        products = []
        query = ""

        if request.method == 'POST':
            query = request.form['query'].strip()
            with get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if query.isdigit():
                    cursor.execute("SELECT * FROM products WHERE id = ?", (int(query),))
                else:
                    cursor.execute("SELECT * FROM products WHERE LOWER(name) LIKE ?", ('%' + query.lower() + '%',))

                products = cursor.fetchall()

                # 🖋️ Log search action
                log_manager_action("Searched Products", f"Search Query: '{query}'", conn)

        return render_template("manager_search_products.html", products=products, query=query)
    return redirect('/login')



# ------------------- View Sales Report -------------------
@app.route('/manager/sales_report')
def manager_sales_report():
    if 'role' in session and session['role'] == 'manager':
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 🧾 Overall Sales
            cursor.execute("""
                SELECT 
                    s.id AS sale_id, 
                    GROUP_CONCAT(si.product_name, ', ') AS product_names, 
                    SUM(si.quantity) AS total_quantity, 
                    s.total_amount, 
                    s.sale_date 
                FROM sales s 
                JOIN sales_items si ON s.id = si.sale_id 
                GROUP BY s.id 
                ORDER BY s.sale_date DESC
            """)
            sales = cursor.fetchall()

            # 📦 Aggregated Product-wise Sales
            cursor.execute("""
                SELECT 
                    si.product_name, 
                    SUM(si.quantity) AS total_quantity_sold, 
                    SUM(si.quantity * si.price_per_unit) AS total_sales_amount
                FROM sales_items si
                GROUP BY si.product_name
                ORDER BY total_sales_amount DESC
            """)
            product_sales = cursor.fetchall()

            log_manager_action("Viewed Sales Report", "Checked overall and product-wise sales", conn)

        return render_template("manager_sales_report.html", sales=sales, product_sales=product_sales)

    return redirect('/login')


# ------------------- Loyal Customers -------------------
@app.route('/manager/loyal_customers')
def manager_loyal_customers():
    if 'role' in session and session['role'] == 'manager':
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, phone, total_spent 
                FROM customers 
                WHERE total_spent >= 1000 
                ORDER BY total_spent DESC
            """)
            customers = cursor.fetchall()

            # 🌸 Log within same connection
            log_manager_action("Viewed Loyal Customers", "Viewed list of customers with total_spent >= ₹1000", conn)

        return render_template("manager_loyal_customers.html", customers=customers)
    return redirect('/login')



# ------------------- Backup Database -------------------
@app.route('/manager/backup')
def manager_backup():
    if 'role' in session and session['role'] == 'manager':
        import shutil, os, datetime
        os.makedirs("backup", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backup/grocery_backup_{timestamp}.db"
        shutil.copy2("grocery.db", backup_path)
        log_manager_action("Database Backup", f"Backup saved at {backup_path}")
        return f"✅ Backup created at: {backup_path}"
    return redirect('/login')


# ------------------- View Audit Log -------------------
@app.route('/manager/audit_log')
def manager_audit_log():
    if 'role' in session and session['role'] == 'manager':
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM manager_audit ORDER BY timestamp DESC")
                logs = cursor.fetchall()
            return render_template("manager_audit_log.html", logs=logs)
        except Exception as e:
            print("Error fetching manager audit logs:", e)
            flash("⚠️ Could not load audit logs at the moment.", "danger")
            return redirect('/manager')
    return redirect('/login')

# managerlogactions
def log_manager_action(action, details="", conn=None):
    if 'username' in session:
        user = session['username']
    else:
        user = 'Unknown'

    if conn:
        conn.execute(
            "INSERT INTO manager_audit (action, details, user) VALUES (?, ?, ?)",
            (action, details, user)
        )
    else:
        with get_db_connection() as inner_conn:
            inner_conn.execute(
                "INSERT INTO manager_audit (action, details, user) VALUES (?, ?, ?)",
                (action, details, user)
            )


# cashier
@app.route('/cashier/view_products')
def cashier_view_products():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock,image_url FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('cashier_view_products.html', products=products)

@app.route('/cashier/generate_bill', methods=['GET', 'POST'])
def cashier_generate_bill():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    # Fetch product id and name for the right panel
    cursor.execute("SELECT id, name FROM products")
    product_list = cursor.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')

        conn = sqlite3.connect("grocery.db")
        cursor = conn.cursor()

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
        subtotal = 0.0

        for i in range(len(product_ids)):
            try:
                pid = int(product_ids[i])
                qty = int(quantities[i])
                cursor.execute("SELECT name, price, stock FROM products WHERE id = ?", (pid,))
                product = cursor.fetchone()

                if product and qty <= product[2]:
                    item_total = product[1] * qty
                    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, pid))
                    conn.commit()
                    cart.append({
                        'name': product[0],
                        'quantity': qty,
                        'price_per_unit': product[1],
                        'total_price': item_total
                    })
                    subtotal += item_total
            except Exception:
                continue

        is_loyal = total_spent >= 1000
        discount = subtotal * 0.20 if is_loyal else 0
        final_amount = subtotal - discount

        sale_date = datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        cursor.execute(
            "INSERT INTO sales (customer_id, sale_date, total_amount,name) VALUES (?, ?,?, ?)",
            (customer_id, sale_date, final_amount,name)
        )
        conn.commit()
        sale_id = cursor.lastrowid

        for item in cart:
            cursor.execute(
                "INSERT INTO sales_items (sale_id, product_id, product_name, quantity, price_per_unit, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                (sale_id, pid, item['name'], item['quantity'], item['price_per_unit'], item['total_price'])
            )

        cursor.execute("UPDATE customers SET total_spent = total_spent + ? WHERE id = ?", (final_amount, customer_id))
        conn.commit()
        conn.close()

        return render_template('cashier_bill_summary.html', cart=cart, subtotal=subtotal, discount=discount if is_loyal else 0, final_amount=final_amount, time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    return render_template('cashier_generate_bill.html', products=product_list)




# Keep this always 💖
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True,threaded=False)
# render will use gunicorn to run it
