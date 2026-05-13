import sqlite3

def connect():
    conn = sqlite3.connect('swiftflow.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup():
    conn = connect()
    conn.execute('CREATE TABLE IF NOT EXISTS inventory (item TEXT PRIMARY KEY, qty INTEGER, cost REAL, price REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, item TEXT, qty INTEGER, totalcost REAL, totalrevenue REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, description TEXT, amount REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()