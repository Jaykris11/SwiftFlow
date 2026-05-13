import mysql.connector

def connect():
    tempdb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    tempcursor = tempdb.cursor()
    tempcursor.execute("CREATE DATABASE IF NOT EXISTS swiftflow")
    tempdb.close()
    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="swiftflow"
    )
    return conn

def setup():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS inventory (item VARCHAR(255) PRIMARY KEY, qty INT, cost DECIMAL(10,2), price DECIMAL(10,2))')
    cursor.execute('CREATE TABLE IF NOT EXISTS sales (id INT AUTO_INCREMENT PRIMARY KEY, date VARCHAR(255), item VARCHAR(255), qty INT, totalcost DECIMAL(10,2), totalrevenue DECIMAL(10,2), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute('CREATE TABLE IF NOT EXISTS expenses (id INT AUTO_INCREMENT PRIMARY KEY, date VARCHAR(255), description VARCHAR(255), amount DECIMAL(10,2), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()