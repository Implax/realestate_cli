
import psycopg2
from getpass import getpass
from users import register_user
from agents import agent_dashboard
from renters import renter_dashboard

def connect_db():
    return psycopg2.connect(
        dbname="realestate_db",
        user="your_username",  # change this
        password=getpass("PostgreSQL password: "),
        host="localhost",
        port="5432"
    )

def main():
    conn = connect_db()
    cur = conn.cursor()

    while True:
        print("\n=== Real Estate CLI ===")
        print("1. Register")
        print("2. Login as Agent")
        print("3. Login as Renter")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            register_user(cur)
            conn.commit()
        elif choice == "2":
            email = input("Agent Email: ")
            agent_dashboard(cur, conn, email)
        elif choice == "3":
            email = input("Renter Email: ")
            renter_dashboard(cur, conn, email)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Try again.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
