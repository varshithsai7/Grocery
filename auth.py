import sqlite3

from admin_panel import admin_menu
from manager_panel import manager_menu
from cashier_panel import cashier_menu

def cli_login():
    conn=sqlite3.connect("grocery.db")
    cursor=conn.cursor()

    username=input("Enter username: ")
    password= input("Enter password: ")

    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        role = result[0]
        print(f"\n🌸 Welcome, {username}! You are logged in as {role}.\n")
        if role == "admin":
            admin_menu()  # Call admin menu after admin login
        elif role == "manager":
            manager_menu()
        elif role == "cashier":
            cashier_menu()
        else:
            print("Role not recognized. Contact system administrator.")
    else:
        print("\n❌ Invalid username or password. Please try again.\n")

    conn.close()

def cli_validate_user(username, password):
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


from flask import Blueprint, render_template, request, redirect, session, url_for


auth = Blueprint('auth', "varshith")

def validate_user(username, password):
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user  # (id, username, role) or None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = validate_user(username, password)

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]

            # Redirect based on role
            if user[2] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[2] == 'manager':
                return redirect(url_for('manager_dashboard'))
            elif user[2] == 'cashier':
                return redirect(url_for('cashier_dashboard'))
            else:
                return render_template('home.html', error="Unknown role!")
        else:
            return render_template('home.html', error="❌ Invalid username or password.")
    return render_template('home.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# if __name__ == "__main__":
#     login()