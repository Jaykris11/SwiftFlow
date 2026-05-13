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
        row = conn.execute('SELECT qty FROM inventory WHERE item = ?', (item,)).fetchone()
        if row:
            newqty = row['qty'] + qty
            conn.execute('UPDATE inventory SET qty = ?, cost = ?, price = ? WHERE item = ?', (newqty, cost, price, item))
            print(f"Updated {item} stock to {newqty}")
        else:
            conn.execute('INSERT INTO inventory (item, qty, cost, price) VALUES (?, ?, ?, ?)', (item, qty, cost, price))
            print(f"Added {item} to catalog")
        desc = f"Restock {qty}x {item}"
        conn.execute('INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)', (today(), desc, total))
        conn.commit()
        conn.close()
        print(f"Expense Logged: {total}")
    except ValueError:
        print("Invalid input")

def sell():
    print("\nLOG SALE")
    conn = connect()
    items = conn.execute('SELECT item, qty, price FROM inventory').fetchall()
    if not items:
        print("Inventory empty")
        conn.close()
        return
    print("Available Inventory:")
    for r in items:
        print(f"{r['item']} (Stock: {r['qty']} | Price: {r['price']})")
    choice = input("\nEnter item sold: ")
    row = conn.execute('SELECT * FROM inventory WHERE item = ?', (choice,)).fetchone()
    if not row:
        print("Item not found")
        conn.close()
        return
    try:
        qtysold = int(input("Quantity sold: "))
        totalcost = row['cost'] * qtysold
        totalrev = row['price'] * qtysold
        newstock = row['qty'] - qtysold
        conn.execute('INSERT INTO sales (date, item, qty, totalcost, totalrevenue) VALUES (?, ?, ?, ?, ?)', (today(), choice, qtysold, totalcost, totalrev))
        conn.execute('UPDATE inventory SET qty = ? WHERE item = ?', (newstock, choice))
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
    print("\nSALES")
    sales = conn.execute('SELECT * FROM sales ORDER BY timestamp DESC').fetchall()
    if not sales: 
        print("No sales")
    for s in sales:
        print(f"[{s['date']}] Sold {s['qty']}x {s['item']} | Rev: {s['totalrevenue']} | Cost: {s['totalcost']}")
    print("\nEXPENSES")
    expenses = conn.execute('SELECT * FROM expenses ORDER BY timestamp DESC').fetchall()
    if not expenses: 
        print("No expenses")
    for e in expenses:
        print(f"[{e['date']}] {e['description']} | Amount: {e['amount']}")
    conn.close()
    input("\nPress Enter to return")