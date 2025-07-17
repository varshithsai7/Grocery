# Grocery Management System

A web-based application for managing grocery store operations, including product management, billing, sales reports, and user roles (Admin, Manager, Cashier).

## Features
- **User Roles:** Admin, Manager, and Cashier panels with role-specific features
- **Product Management:** Add, edit, view, and restock products
- **Billing:** Generate and print bills for customers
- **Sales Reports:** View and export sales data
- **Audit Logs:** Track user actions and changes
- **Stock Alerts:** Low stock and expired product notifications

## Getting Started

### Prerequisites
- Python 3.8 or newer
- (Recommended) Virtual environment tool: `venv`

### Installation
1. **Clone or Download the Repository**
   - Place all files in a directory on your computer.

2. **Set Up a Virtual Environment (Optional but Recommended)**
   ```bash
   python -m venv venv
   # Activate the environment:
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**
   - The app uses SQLite (`grocery.db`).
   - If not present, run the provided script to set up tables:
     ```bash
     python set_tables.py
     ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   - The app will start on `http://127.0.0.1:5000/` by default.

6. **Access the App**
   - Open your browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Usage
- **Login:** Use the login page to access your role’s dashboard.
- **Admin Panel:** Manage users, view audit logs, and oversee products and sales.
- **Manager Panel:** Add/edit products, view low stock/expired items, and generate reports.
- **Cashier Panel:** Generate bills, view products, and see bill summaries.

## Troubleshooting
- **Blank Page/Error:**
  - Check the terminal for error messages.
  - Ensure all dependencies are installed.
  - If you commented out code, review the error and seek help with the specific message.
- **Database Issues:**
  - Make sure `grocery.db` exists and is not corrupted.
  - Re-run `set_tables.py` if needed.
- **Static Files Not Loading:**
  - Ensure the `static/` and `templates/` folders are present and not renamed.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
This project is for educational purposes. 