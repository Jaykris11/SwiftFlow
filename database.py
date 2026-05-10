import sqlite3

def get_db():
    conn = sqlite3.connect('swiftflow.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    
    # Inventory now acts as your Product Catalog too
    conn.execute('''CREATE TABLE IF NOT EXISTS inventory 
                    (item TEXT PRIMARY KEY, qty INTEGER, cost REAL, price REAL)''')
    
    # Sales tracks how many were sold and auto-calculates totals
    conn.execute('''CREATE TABLE IF NOT EXISTS sales 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, item TEXT, 
                     qty INTEGER, total_cost REAL, total_revenue REAL, 
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                     
    conn.execute('''CREATE TABLE IF NOT EXISTS expenses 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, description TEXT, 
                     amount REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()