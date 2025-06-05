import sqlite3

from admin_panel import admin_menu
from manager_panel import manager_menu
from cashier_panel import cashier_menu

def login():
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



if __name__ == "__main__":
    login()