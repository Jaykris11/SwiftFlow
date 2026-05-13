from database import connect
from datetime import datetime
import plotext as plt

def graph():
    print("\nSALES GRAPH")
    print("[1] Past 7 Days")
    print("[2] Past 30 Days")
    print("[3] Past 12 Months")
    choice = input("Select timeframe: ")
    
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    
    if choice == '1':
        query = "SELECT date, SUM(totalrevenue) as rev FROM sales WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY date ORDER BY date"
        title = "Revenue Past 7 Days"
    elif choice == '2':
        query = "SELECT date, SUM(totalrevenue) as rev FROM sales WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) GROUP BY date ORDER BY date"
        title = "Revenue Past 30 Days"
    elif choice == '3':
        query = "SELECT DATE_FORMAT(date, '%Y-%m') as date, SUM(totalrevenue) as rev FROM sales WHERE date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) GROUP BY DATE_FORMAT(date, '%Y-%m') ORDER BY date"
        title = "Revenue Past 12 Months"
    else:
        print("Invalid choice")
        conn.close()
        return
        
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No data for timeframe")
        return
        
    dates = [row['date'][-5:] if choice != '3' else row['date'] for row in rows]
    revenues = [float(row['rev']) for row in rows]
    
    plt.clf()
    plt.bar(dates, revenues, color="cyan")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Revenue")
    plt.theme("dark")
    plt.show()

def dashboard():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute('SELECT SUM(totalrevenue) FROM sales WHERE date = %s', (today,))
    salestoday = cursor.fetchone()[0] or 0.0
    
    cursor.execute('SELECT SUM(totalcost) FROM sales WHERE date = %s', (today,))
    costtoday = cursor.fetchone()[0] or 0.0
    
    cursor.execute('SELECT SUM(amount) FROM expenses WHERE date = %s', (today,))
    exptoday = cursor.fetchone()[0] or 0.0
    
    netprofit = float(salestoday) - (float(costtoday) + float(exptoday))
    
    cursor.execute('SELECT SUM(amount) FROM expenses')
    totexp = cursor.fetchone()[0] or 0.0
    
    cursor.execute('SELECT SUM(totalrevenue) FROM sales')
    totrev = cursor.fetchone()[0] or 0.0
    
    cursor.execute('SELECT SUM(totalcost) FROM sales')
    totcost = cursor.fetchone()[0] or 0.0
    
    overallprofit = float(totrev) - (float(totcost) + float(totexp))
    conn.close()
    
    print("\nFINANCIAL DASHBOARD")
    print("\nTODAYS STATEMENT")
    print(f"Gross Sales: {salestoday:.2f}")
    print(f"Product Cost: {costtoday:.2f}")
    print(f"Expenses: {exptoday:.2f}")
    print(f"Net Profit: {netprofit:.2f}")
    print("\nOVERALL BUSINESS HEALTH")
    print(f"Lifetime Revenue: {totrev:.2f}")
    print(f"Lifetime Profit: {overallprofit:.2f}")
    
    if totrev > 0:
        print(f"Overall Margin: {((totrev - totcost) / totrev) * 100:.1f}%")
        
    wantgraph = input("\nView Sales Graph? (y/n): ").strip().lower()
    if wantgraph in ['y', 'yes']:
        graph()
        
    wantadvice = input("\nView CFO advice? (y/n): ").strip().lower()
    if wantadvice in ['y', 'yes']:
        print("\nCFO SUGGESTIONS")
        if totrev > 0:
            margin = ((totrev - totcost) / totrev) * 100
            if margin < 30: 
                print("Margin Alert: Profit margins below 30 percent. Consider raising prices.")
            elif margin >= 50: 
                print("Excellent Margins: Keeping over 50 percent of revenue.")
            else: 
                print("Healthy Margins: Pricing is stable.")
        if totexp > totrev:
            print("Cash Flow Warning: Expenses higher than revenue.")
        elif exptoday > (salestoday * 0.5) and salestoday > 0:
            print("Expense Heavy: Todays expenses are greater than 50 percent of sales.")
            
    input("\nPress Enter to return")