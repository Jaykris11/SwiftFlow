from database import get_db
from datetime import datetime

def get_today(): return datetime.now().strftime("%Y-%m-%d")

def manage_inventory():
    print("\nMANAGE INVENTORY")
    item = input("Enter Item Name (e.g., Halo-Halo): ")
    try:
        qty = int(input("Quantity to Add to Stock: "))
        cost = float(input("Cost to Make 1 unit (PHP): "))
        price = float(input("Selling Price for 1 unit (PHP): "))
        
        conn = get_db()
        row = conn.execute('SELECT qty FROM inventory WHERE item = ?', (item,)).fetchone()
        
        if row:
            new_qty = row['qty'] + qty
            conn.execute('UPDATE inventory SET qty = ?, cost = ?, price = ? WHERE item = ?', 
                         (new_qty, cost, price, item))
            print(f"✅ Updated {item}: Stock is now {new_qty}. Cost: ₱{cost}, Price: ₱{price}")
        else:
            conn.execute('INSERT INTO inventory (item, qty, cost, price) VALUES (?, ?, ?, ?)', 
                         (item, qty, cost, price))
            print(f"✅ Added {item} to catalog. Stock: {qty}. Cost: ₱{cost}, Price: ₱{price}")
            
        conn.commit()
        conn.close()
    except ValueError:
        print("Invalid input. Please use numbers for quantity and prices.")

def log_sale():
    print("\nLOG A SALE")
    conn = get_db()
    items = conn.execute('SELECT item, qty, price FROM inventory').fetchall()
    
    if not items:
        print("Your inventory is empty. Please add items in Manage Inventory first.")
        conn.close()
        return
        
    print("Available Inventory:")
    for r in items:
        print(f" - {r['item']} (Stock: {r['qty']} | Price: ₱{r['price']})")
        
    item_choice = input("\nEnter the exact name of the item sold: ")
    
    # Check if item exists in inventory
    row = conn.execute('SELECT * FROM inventory WHERE item = ?', (item_choice,)).fetchone()
    if not row:
        print(f"'{item_choice}' not found in inventory. Check your spelling.")
        conn.close()
        return
        
    try:
        qty_sold = int(input(f"How many '{item_choice}' were sold?: "))
        if qty_sold > row['qty']:
            print(f"⚠️ Warning: You only have {row['qty']} in stock! Logging anyway, but check your inventory.")
            
        total_cost = row['cost'] * qty_sold
        total_revenue = row['price'] * qty_sold
        new_stock = row['qty'] - qty_sold
        
        # Log the sale
        conn.execute('INSERT INTO sales (date, item, qty, total_cost, total_revenue) VALUES (?, ?, ?, ?, ?)', 
                     (get_today(), item_choice, qty_sold, total_cost, total_revenue))
        # Deduct from inventory
        conn.execute('UPDATE inventory SET qty = ? WHERE item = ?', (new_stock, item_choice))
        
        conn.commit()
        print(f"Sale Logged: {qty_sold}x {item_choice} = ₱{total_revenue} Total Revenue.")
        print(f"Remaining stock for {item_choice}: {new_stock}")
    except ValueError:
        print("Invalid input. Quantity must be a whole number.")
    conn.close()

def log_expense():
    print("\nLOG AN EXPENSE")
    try:
        desc = input("Expense Description (e.g., Ice delivery, Rent): ")
        amt = float(input("Amount (PHP): "))
        conn = get_db()
        conn.execute('INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)', (get_today(), desc, amt))
        conn.commit()
        conn.close()
        print(f"Expense Logged successfully: Paid ₱{amt} for '{desc}'.")
    except ValueError:
        print("Invalid input. Amount must be a number.")

def view_records():
    print("\nFINANCIAL RECORDS")
    conn = get_db()
    
    print("\nALL SALES")
    sales = conn.execute('SELECT * FROM sales ORDER BY timestamp DESC').fetchall()
    if not sales: print("No sales logged yet.")
    for s in sales:
        print(f"[{s['date']}] Sold {s['qty']}x {s['item']} | Revenue: ₱{s['total_revenue']} | Cost: ₱{s['total_cost']}")
        
    print("\nALL EXPENSES")
    expenses = conn.execute('SELECT * FROM expenses ORDER BY timestamp DESC').fetchall()
    if not expenses: print("No expenses logged yet.")
    for e in expenses:
        print(f"[{e['date']}] {e['description']} | Amount: ₱{e['amount']}")
        
    conn.close()
    input("\nPress Enter to return to Main Menu...")