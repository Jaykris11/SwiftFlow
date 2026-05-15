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
    print("[1] All Records")
    print("[2] Search by Keyword")
    print("[3] Filter by Date")
    choice = input("Select view: ")
    
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    
    if choice == '1':
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
            
    elif choice == '2':
        term = input("Enter keyword: ")
        searchterm = f"%{term}%"
        
        print("\nSALES RESULTS")
        cursor.execute('SELECT * FROM sales WHERE item LIKE %s ORDER BY timestamp DESC', (searchterm,))
        sales = cursor.fetchall()
        if not sales: 
            print("No sales found")
        for s in sales:
            print(f"[{s['date']}] Sold {s['qty']}x {s['item']} | Rev: {s['totalrevenue']} | Cost: {s['totalcost']}")
            
        print("\nEXPENSE RESULTS")
        cursor.execute('SELECT * FROM expenses WHERE description LIKE %s ORDER BY timestamp DESC', (searchterm,))
        expenses = cursor.fetchall()
        if not expenses: 
            print("No expenses found")
        for e in expenses:
            print(f"[{e['date']}] {e['description']} | Amount: {e['amount']}")
            
    elif choice == '3':
        targetdate = input("Enter date (YYYY-MM-DD): ")
        
        print("\nSALES RESULTS")
        cursor.execute('SELECT * FROM sales WHERE date = %s ORDER BY timestamp DESC', (targetdate,))
        sales = cursor.fetchall()
        if not sales: 
            print("No sales found")
        for s in sales:
            print(f"[{s['date']}] Sold {s['qty']}x {s['item']} | Rev: {s['totalrevenue']} | Cost: {s['totalcost']}")
            
        print("\nEXPENSE RESULTS")
        cursor.execute('SELECT * FROM expenses WHERE date = %s ORDER BY timestamp DESC', (targetdate,))
        expenses = cursor.fetchall()
        if not expenses: 
            print("No expenses found")
        for e in expenses:
            print(f"[{e['date']}] {e['description']} | Amount: {e['amount']}")
            
    else:
        print("Invalid choice")
        
    conn.close()
    input("\nPress Enter to return")