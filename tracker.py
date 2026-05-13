from database import connect
from datetime import datetime

def today(): 
    return datetime.now().strftime("%Y-%m-%d")

def restock():
    print("\nRESTOCK INVENTORY")
    item = input("Enter Item Name: ")
    try:
        qty = int(input("Quantity to Add: "))
        cost = float(input("Cost per unit: "))
        price = float(input("Selling Price per unit: "))
        total = qty * cost
        
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT qty FROM inventory WHERE item = %s', (item,))
        row = cursor.fetchone()
        
        if row:
            newqty = row['qty'] + qty
            cursor.execute('UPDATE inventory SET qty = %s, cost = %s, price = %s WHERE item = %s', (newqty, cost, price, item))
            print(f"Updated {item} stock to {newqty}")
        else:
            cursor.execute('INSERT INTO inventory (item, qty, cost, price) VALUES (%s, %s, %s, %s)', (item, qty, cost, price))
            print(f"Added {item} to catalog")
            
        desc = f"Restock {qty}x {item}"
        cursor.execute('INSERT INTO expenses (date, description, amount) VALUES (%s, %s, %s)', (today(), desc, total))
        conn.commit()
        conn.close()
        print(f"Expense Logged: {total}")
    except ValueError:
        print("Invalid input")

def sell():
    print("\nLOG SALE")
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT item, qty, price FROM inventory')
    items = cursor.fetchall()
    
    if not items:
        print("Inventory empty")
        conn.close()
        return
        
    print("Available Inventory:")
    for r in items:
        print(f"{r['item']} (Stock: {r['qty']} | Price: {r['price']})")
        
    choice = input("\nEnter item sold: ")
    cursor.execute('SELECT * FROM inventory WHERE item = %s', (choice,))
    row = cursor.fetchone()
    
    if not row:
        print("Item not found")
        conn.close()
        return
        
    try:
        qtysold = int(input("Quantity sold: "))
        totalcost = float(row['cost']) * qtysold
        totalrev = float(row['price']) * qtysold
        newstock = row['qty'] - qtysold
        
        cursor.execute('INSERT INTO sales (date, item, qty, totalcost, totalrevenue) VALUES (%s, %s, %s, %s, %s)', (today(), choice, qtysold, totalcost, totalrev))
        cursor.execute('UPDATE inventory SET qty = %s WHERE item = %s', (newstock, choice))
        conn.commit()
        
        print(f"Sale Logged {qtysold}x {choice} = {totalrev}")
        if newstock < 5:
            print(f"Low Stock Alert: {newstock} left")
    except ValueError:
        print("Invalid input")
    conn.close()

def history():
    print("\nFINANCIAL RECORDS")
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    
    print("\nSALES")
    cursor.execute('SELECT * FROM sales ORDER BY timestamp DESC')
    sales = cursor.fetchall()
    if not sales: 
        print("No sales")
    for s in sales:
        print(f"[{s['date']}] Sold {s['qty']}x {s['item']} | Rev: {s['totalrevenue']} | Cost: {s['totalcost']}")
        
    print("\nEXPENSES")
    cursor.execute('SELECT * FROM expenses ORDER BY timestamp DESC')
    expenses = cursor.fetchall()
    if not expenses: 
        print("No expenses")
    for e in expenses:
        print(f"[{e['date']}] {e['description']} | Amount: {e['amount']}")
        
    conn.close()
    input("\nPress Enter to return")