# realestate_cli/renter_profile.py
import psycopg2 

from datetime import datetime

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
def manage_profile(cur, conn, email):
    while True:
        print("\n--- Manage Address and Payment ---")
        print("1. Add Address")
        print("2. Delete Address")
        print("3. Add Credit Card")
        print("4. Delete Credit Card")
        print("5. Back to Renter Menu")
        choice = input("Choose an option: ")

        if choice == "1":
            add_address(cur, email)
            conn.commit()
        elif choice == "2":
            delete_address(cur, email)
            conn.commit()
        elif choice == "3":
            add_credit_card(cur, email)
            conn.commit()
        elif choice == "4":
            delete_credit_card(cur, email)
            conn.commit()
        elif choice == "5":
            break
        else:
            print("Invalid choice.")

def add_address(cur, email):
    print("\n=== Add Address ===")
    street = input("Street: ")
    city = input("City: ")
    state = input("State: ")
    cur.execute("""
        INSERT INTO Address (street, city, state)
        VALUES (%s, %s, %s) RETURNING address_id
    """, (street, city, state))
    address_id = cur.fetchone()[0]
    cur.execute("INSERT INTO User_Address (user_email, address_id) VALUES (%s, %s)", (email, address_id))
    print(f"Address added with ID: {address_id}")

def delete_address(cur, email):
    print("\n=== Delete Address ===")
    cur.execute("""
        SELECT a.address_id, a.street, a.city, a.state FROM Address a
        JOIN User_Address ua ON a.address_id = ua.address_id
        WHERE ua.user_email = %s
    """, (email,))
    addresses = cur.fetchall()

    if not addresses:
        print("No addresses to delete.")
        return

    for a in addresses:
        print(f"{a[0]}: {a[1]}, {a[2]}, {a[3]}")
    aid = input("Address ID to delete: ")

    # Check for credit card dependency
    cur.execute("SELECT 1 FROM Credit_Card WHERE address_id = %s", (aid,))
    if cur.fetchone():
        print("❌ Cannot delete address: it is linked to a credit card.")
        return

    cur.execute("DELETE FROM User_Address WHERE user_email = %s AND address_id = %s", (email, aid))
    cur.execute("DELETE FROM Address WHERE address_id = %s", (aid,))
    print("Address deleted.")

def add_credit_card(cur, email):
    print("\n=== Add Credit Card ===")
    card_number = input("Card Number (16 digits): ")
    expiry = input("Enter expiry date (YYYY-MM-DD): ")
    if not is_valid_date(expiry):
        print("Invalid date format. Please enter a valid date (YYYY-MM-DD).")
        return
    cvv = input("CVV (3-4 digits): ")

    

    # Select one of user's addresses
    cur.execute("""
        SELECT a.address_id, a.street, a.city FROM Address a
        JOIN User_Address ua ON a.address_id = ua.address_id
        WHERE ua.user_email = %s
    """, (email,))
    addresses = cur.fetchall()

    if not addresses:
        print("You must add an address first.")
        return

    for a in addresses:
        print(f"{a[0]}: {a[1]}, {a[2]}")
    addr_id = input("Billing Address ID: ")

    cur.execute("""
        INSERT INTO Credit_Card (card_number, expiry_date, cvv, renter_email, address_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (card_number, expiry, cvv, email, addr_id))
    print("Credit card added.")

def delete_credit_card(cur, email):
    print("\n=== Delete Credit Card ===")
    cur.execute("SELECT card_number FROM Credit_Card WHERE renter_email = %s", (email,))
    cards = cur.fetchall()

    if not cards:
        print("No cards to delete.")
        return

    for c in cards:
        print(f"Card: {c[0]}")
    card = input("Enter card number to delete: ")
    cur.execute("DELETE FROM Credit_Card WHERE renter_email = %s AND card_number = %s", (email, card))
    print("Credit card deleted.")
