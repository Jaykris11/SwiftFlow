from database import init_db
import tracker
import advisor
from art import tprint

def start_application():
    init_db() 
    
    while True:
        print("\n")
        tprint("SWIFTFLOW")
        print("BUSINESS MANAGER v8.0 (POS Edition)")
        print("[1] Manage Inventory (Add Stock & Pricing)")
        print("[2] Log a Sale (Deducts from Inventory)")
        print("[3] Log an Expense")
        print("[4] View Full Sales & Expenses Records")
        print("[5] Smart Advisor (Dashboard & Advice)")
        print("[6] Exit System")

        
        choice = input("\nSelect an action (1-6): ")
        
        if choice == '1': 
            tracker.manage_inventory()
        elif choice == '2': 
            tracker.log_sale()
        elif choice == '3': 
            tracker.log_expense()
        elif choice == '4': 
            tracker.view_records()
        elif choice == '5': 
            advisor.generate_financial_statement()
        elif choice == '6':
            print("Database secured. System offline.")
            break
        else: 
            print("Invalid input.")

if __name__ == "__main__":
    start_application()