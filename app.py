from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from auth import validate_user


app = Flask("MyGRow", static_url_path='/static')
app.secret_key = 'varsh'

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
        role = validate_user(username, password)
        if role:
            session['username'] = username
            session['role'] = role
            if role == 'admin':
                return redirect(url_for('admin_home'))
            elif role == 'manager':
                return redirect(url_for('manager_home'))
            elif role == 'cashier':
                return redirect(url_for('cashier_home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')



@app.route('/admin')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html')
    return redirect('/login')

@app.route('/cashier')
def cashier_dashboard():
    if 'role' in session and session['role'] == 'cashier':
        return render_template('cashier_dashboard.html')
    return redirect('/login')

@app.route('/manager')
def manager_dashboard():
    if 'role' in session and session['role'] == 'manager':
        return render_template('manager_dashboard.html')
    return redirect('/login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

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




# Keep this always 💖
if __name__ == '__main__':
    app.run(debug=True)
