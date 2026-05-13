from database import setup
import tracker
import advisor

def run():
    setup() 
    while True:
        print("SWIFTFLOW BUSINESS MANAGER")
        print("[1] Restock Inventory")
        print("[2] Log Sale")
        print("[3] View Records")
        print("[4] Smart Advisor")
        print("[5] Exit")
        choice = input("\nSelect action: ")
        if choice == '1': 
            tracker.restock()
        elif choice == '2': 
            tracker.sell()
        elif choice == '3': 
            tracker.history()
        elif choice == '4': 
            advisor.dashboard()
        elif choice == '5':
            print("Database secured. System offline.")
            break
        else: 
            print("Invalid input")

if __name__ == "__main__":
    run()