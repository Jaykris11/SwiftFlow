from database import connect
from datetime import datetime

def today(): 
    return datetime.now().strftime("%Y-%m-%d")

def restock():
    print("\nINVENTORY MANAGEMENT (STRICT DEPLETION)")
    print("[1] Add / Restock Item")
    print("[2] View Current Stock")
    print("[3] Edit Existing Stock")
    choice = input("Select action: ")
    
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    
    if choice == '1':
        item = input("Enter Item Name: ")
        
        cursor.execute('SELECT SUM(qty) as total_stock FROM inventory WHERE item = %s', (item,))
        stock_row = cursor.fetchone()
        
        if stock_row and stock_row['total_stock'] is not None and stock_row['total_stock'] > 0:
            print(f"\nRestock Denied: '{item}' still has {stock_row['total_stock']} units remaining in inventory.")
            print("Current stock must be completely empty (0) before you can add or restock this item.")
            conn.close()
            return
            
        try:
            qty = int(input("Quantity to Add: "))
            cost = float(input("Cost per unit: "))
            price = float(input("Selling Price per unit: "))
            total = qty * cost
            
            cursor.execute('SELECT id, qty FROM inventory WHERE item = %s AND cost = %s AND price = %s', (item, cost, price))
            row = cursor.fetchone()
            
            if row:
                newqty = row['qty'] + qty
                cursor.execute('UPDATE inventory SET qty = %s WHERE id = %s', (newqty, row['id']))
                print(f"Added to existing matching batch. Total batch stock: {newqty}")
            else:
                cursor.execute('INSERT INTO inventory (item, qty, cost, price) VALUES (%s, %s, %s, %s)', (item, qty, cost, price))
                print(f"Created new distinct batch for {item} at cost {cost:.2f}")
                
            desc = f"Restock {qty}x {item} (Batch Cost: {cost:.2f})"
            cursor.execute('INSERT INTO expenses (date, description, amount) VALUES (%s, %s, %s)', (today(), desc, total))
            conn.commit()
            print(f"Expense Logged: {total}")
        except ValueError:
            print("Invalid input")
            
    elif choice == '2':
        print("\nCURRENT INVENTORY BY BATCH:")
        cursor.execute('SELECT * FROM inventory WHERE qty > 0 ORDER BY item, id ASC')
        items = cursor.fetchall()
        if not items:
            print("Inventory is empty.")
        for r in items:
            print(f"Batch ID: {r['id']} | Item: {r['item']} | Stock: {r['qty']} | Cost: {r['cost']} | Price: {r['price']}")
            
    elif choice == '3':
        try:
            batch_id = int(input("Enter Batch ID to edit: "))
            cursor.execute('SELECT * FROM inventory WHERE id = %s', (batch_id,))
            row = cursor.fetchone()
            
            if row:
                if row['qty'] > 0:
                    print(f"\nEdit Denied: Strict Depletion rule is active.")
                    print(f"Batch {row['id']} ('{row['item']}') currently has {row['qty']} active units.")
                    print("You cannot alter the quantity, cost, or price of an active batch. It must be fully depleted first.")
                    conn.close()
                    return

                print(f"Editing {row['item']} (Batch {row['id']}) -> Qty: {row['qty']}, Cost: {row['cost']}, Price: {row['price']}")
                newqty = int(input("Enter new Quantity: "))
                newcost = float(input("Enter new Cost: "))
                newprice = float(input("Enter new Price: "))
                
                cursor.execute('UPDATE inventory SET qty = %s, cost = %s, price = %s WHERE id = %s', (newqty, newcost, newprice, batch_id))
                conn.commit()
                print("Batch successfully updated.")
            else:
                print("Batch ID not found.")
        except ValueError:
            print("Invalid input format.")
            
    else:
        print("Invalid choice")
        
    conn.close()

def log_sale():
    print("\nLOG MANUAL SALE (FIFO METHOD)")
    item = input("Enter Item Name: ")
    try:
        qty_to_sell = int(input("Quantity Sold: "))
        if qty_to_sell <= 0:
            print("Quantity must be greater than zero.")
            return
            
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT SUM(qty) as total_stock FROM inventory WHERE item = %s', (item,))
        stock_check = cursor.fetchone()
        
        if not stock_check or not stock_check['total_stock'] or stock_check['total_stock'] < qty_to_sell:
            print(f"Insufficient total stock available for {item}.")
            conn.close()
            return
            
        cursor.execute('SELECT * FROM inventory WHERE item = %s AND qty > 0 ORDER BY id ASC', (item,))
        batches = cursor.fetchall()
        
        total_cost = 0.0
        total_rev = 0.0
        remaining_to_sell = qty_to_sell
        
        for batch in batches:
            if remaining_to_sell <= 0:
                break
                
            if batch['qty'] >= remaining_to_sell:
                take = remaining_to_sell
                new_batch_qty = batch['qty'] - take
                cursor.execute('UPDATE inventory SET qty = %s WHERE id = %s', (new_batch_qty, batch['id']))
                
                total_cost += take * float(batch['cost'])
                total_rev += take * float(batch['price'])
                remaining_to_sell = 0
            else:
                take = batch['qty']
                cursor.execute('UPDATE inventory SET qty = 0 WHERE id = %s', (batch['id']))
                
                total_cost += take * float(batch['cost'])
                total_rev += take * float(batch['price'])
                remaining_to_sell -= take
                
        cursor.execute('INSERT INTO sales (date, item, qty, totalcost, totalrevenue) VALUES (%s, %s, %s, %s, %s)', (today(), item, qty_to_sell, total_cost, total_rev))
        print(f"Successfully logged sale of {qty_to_sell}x {item}.")
        
        cursor.execute('SELECT SUM(qty) as final_stock FROM inventory WHERE item = %s', (item,))
        alert_check = cursor.fetchone()
        if alert_check and alert_check['final_stock'] < 5:
            print(f"Low Stock Alert: Total remaining {item} stock is {alert_check['final_stock']}")
            
        conn.commit()
        conn.close()
    except ValueError:
        print("Invalid input format.")

def history():
    print("\nFINANCIAL RECORDS")
    print("[1] All Records")
    print("[2] Search by Keyword")
    print("[3] Filter by Timeframe")
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
        print("\nSELECT TIMEFRAME")
        print("[1] Past 7 Days (Week)")
        print("[2] Past 30 Days (Month)")
        print("[3] Past 12 Months (Year)")
        time_choice = input("Select timeframe: ")
        
        if time_choice == '1':
            date_query = ">= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        elif time_choice == '2':
            date_query = ">= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        elif time_choice == '3':
            date_query = ">= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"
        else:
            print("Invalid choice")
            conn.close()
            return
        
        print("\nSALES RESULTS")
        cursor.execute(f'SELECT * FROM sales WHERE date {date_query} ORDER BY timestamp DESC')
        sales = cursor.fetchall()
        if not sales: 
            print("No sales found in timeframe")
        for s in sales: 
            print(f"[{s['date']}] Sold {s['qty']}x {s['item']} | Rev: {s['totalrevenue']} | Cost: {s['totalcost']}")
            
        print("\nEXPENSE RESULTS")
        cursor.execute(f'SELECT * FROM expenses WHERE date {date_query} ORDER BY timestamp DESC')
        expenses = cursor.fetchall()
        if not expenses: 
            print("No expenses found in timeframe")
        for e in expenses: 
            print(f"[{e['date']}] {e['description']} | Amount: {e['amount']}")
            
    else:
        print("Invalid choice")
        
    conn.close()
    input("\nPress Enter to return")