from database import get_db
from datetime import datetime

def generate_financial_statement():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    
    # Gather Data
    sales_today = conn.execute('SELECT SUM(total_revenue) FROM sales WHERE date = ?', (today,)).fetchone()[0] or 0.0
    cost_today = conn.execute('SELECT SUM(total_cost) FROM sales WHERE date = ?', (today,)).fetchone()[0] or 0.0
    exp_today = conn.execute('SELECT SUM(amount) FROM expenses WHERE date = ?', (today,)).fetchone()[0] or 0.0
    net_profit = sales_today - (cost_today + exp_today)
    
    tot_exp = conn.execute('SELECT SUM(amount) FROM expenses').fetchone()[0] or 0.0
    tot_rev = conn.execute('SELECT SUM(total_revenue) FROM sales').fetchone()[0] or 0.0
    tot_cost = conn.execute('SELECT SUM(total_cost) FROM sales').fetchone()[0] or 0.0
    overall_profit = tot_rev - (tot_cost + tot_exp)
    

    print(" SMART ADVISOR: FINANCIAL DASHBOARD")
    
    print("\nTODAY'S STATEMENT")
    print(f"  + Gross Sales:  ₱{sales_today:.2f}")
    print(f"  - Product Cost: ₱{cost_today:.2f}")
    print(f"  - Expenses:     ₱{exp_today:.2f}")
    print(f"  = Net Profit:   ₱{net_profit:.2f}")

    print("\nOVERALL BUSINESS HEALTH")
    print(f"  Lifetime Revenue: ₱{tot_rev:.2f}")
    print(f"  Lifetime Profit:  ₱{overall_profit:.2f}")
    if tot_rev > 0:
        print(f"  Overall Margin:   {((tot_rev - tot_cost) / tot_rev) * 100:.1f}%")
    
   
    want_advice = input("\nWould you like financial advice based on your statements? (y/n): ").strip().lower()
    if want_advice in ['y', 'yes', 'yeah', 'yep']:
        print("\nCFO SUGGESTIONS & INSIGHTS")
        
       
        if tot_rev > 0:
            margin = ((tot_rev - tot_cost) / tot_rev) * 100
            if margin < 30:
                print("MARGIN ALERT: Your profit margins are below 30%. Consider raising your selling prices or finding cheaper ingredient suppliers.")
            elif margin >= 50:
                print("EXCELLENT MARGINS: You are keeping over 50% of your sales revenue. Your pricing strategy is perfect.")
            else:
                print("HEALTHY MARGINS: Your pricing is stable. Focus on increasing daily sales volume.")
                
       
        if tot_exp > tot_rev:
            print("CASH FLOW WARNING: Your overall expenses are higher than your revenue. Cut back on non-essential expenses immediately until sales pick up.")
        elif exp_today > (sales_today * 0.5) and sales_today > 0:
            print("DAILY EXPENSE HEAVY: Today's expenses ate up more than half your sales. Ensure these are bulk/restock expenses and not daily burn.")
            
       
        low_stock = conn.execute('SELECT item, qty FROM inventory WHERE qty < 10').fetchall()
        if low_stock:
            print("LOW STOCK WARNING: The following items are running out and need restocking soon:")
            for item in low_stock:
                print(f"{item['item']} (Only {item['qty']} left)")
        else:
            print("INVENTORY HEALTHY: You have plenty of stock for all items.")
            
    conn.close()
    input("\nPress Enter to return to the Main Menu...")

