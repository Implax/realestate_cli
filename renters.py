import datetime
from renter_profile import manage_profile


def renter_dashboard(cur, conn, renter_email):
    while True:
        print("\n--- Renter Dashboard ---")
        print("1. Search Properties")
        print("2. Book Property")
        print("3. View My Bookings")
        print("4. Cancel Booking")
        print("5. Manage Profile")
        print("6. Join Reward Program")
        print("7. View Reward Points")
        print("8. Logout")
        choice = input("> ")

        if choice == "1":
            search_properties(cur)
        elif choice == "2":
            book_property(cur, renter_email)
        elif choice == "3":
            view_my_bookings(cur, renter_email)
        elif choice == "4":
            cancel_booking(cur, renter_email)
        elif choice == "5":
            manage_profile(cur, conn, renter_email)
        elif choice == "6":
            join_reward_program(cur, renter_email)
        elif choice == "7":
            view_reward_points(cur, renter_email)
        elif choice == "8":
            break
        else:
            print("Invalid option.")


def search_properties(cur):
    print("\n=== Search Properties ===")
    city = input("City (optional): ")
    date = input("Available on date (YYYY-MM-DD): ")  # Optional, not used in logic yet
    bedrooms = input("Min number of bedrooms (optional): ")
    max_price = input("Max price (optional): ")
    property_type = input("Property type (Apartment, House, Commercial, etc.) (optional): ")
    order_by = input("Order by (price/bedrooms): ")

    query = """
        SELECT p.property_id, p.type, p.street_address, p.city, p.state, p.description,
               p.rental_price, p.availability,
               h.number_of_rooms AS house_rooms, h.square_footage AS house_sqft,
               a.number_of_rooms AS apt_rooms, a.square_footage AS apt_sqft, a.building_type,
               c.square_footage AS comm_sqft, c.business_type
        FROM Property p
        LEFT JOIN House h ON p.property_id = h.property_id
        LEFT JOIN Apartment a ON p.property_id = a.property_id
        LEFT JOIN Commercial_Building c ON p.property_id = c.property_id
        WHERE p.availability = TRUE
    """
    params = []

    if city:
        query += " AND p.city ILIKE %s"
        params.append(f"%{city}%")

    if bedrooms:
        query += " AND COALESCE(h.number_of_rooms, a.number_of_rooms) >= %s"
        params.append(bedrooms)

    if max_price:
        query += " AND p.rental_price <= %s"
        params.append(max_price)

    if property_type:
        query += " AND p.type ILIKE %s"
        params.append(f"%{property_type}%")

    if order_by == "price":
        query += " ORDER BY p.rental_price"
    elif order_by == "bedrooms":
        query += " ORDER BY COALESCE(h.number_of_rooms, a.number_of_rooms)"

    cur.execute(query, params)
    results = cur.fetchall()

    if results:
        print("\n=== Property Results ===")
        for row in results:
            print(f"ID: {row[0]} | Type: {row[1]} | {row[2]}, {row[3]}, {row[4]}")
            print(f"Description: {row[5]}")
            print(f"Price: ${row[6]} | Available: {'Yes' if row[7] else 'No'}")

            if row[1] == "House":
                print(f"Rooms: {row[8]} | Sqft: {row[9]}")
            elif row[1] == "Apartment":
                print(f"Rooms: {row[10]} | Sqft: {row[11]} | Building: {row[12]}")
            elif row[1] == "Commercial":
                print(f"Sqft: {row[13]} | Business Type: {row[14]}")

            print("-" * 60)
    else:
        print("No properties found matching your criteria.")

def book_property(cur, renter_email):
    print("\n=== Book a Property ===")
    property_id = input("Enter property ID: ")
    start = input("Start date (YYYY-MM-DD): ")
    end = input("End date (YYYY-MM-DD): ")

    cur.execute("SELECT card_number FROM Credit_Card WHERE renter_email = %s", (renter_email,))
    cards = cur.fetchall()

    if not cards:
        print("You must add a credit card first.")
        return

    print("Available Cards:")
    for i, card in enumerate(cards):
        print(f"{i + 1}. {card[0]}")
    card_number = cards[int(input("Choose a card: ")) - 1][0]

    cur.execute(
        "INSERT INTO Booking (booking_date, start_date, end_date, renter_email, property_id, card_number) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (datetime.date.today(), start, end, renter_email, property_id, card_number)
    )

    cur.execute("SELECT rental_price FROM Property WHERE property_id = %s", (property_id,))
    price = cur.fetchone()[0]

    cur.execute("SELECT * FROM Reward_Program WHERE renter_email = %s", (renter_email,))
    if cur.fetchone():
        cur.execute(
            "UPDATE Reward_Program SET reward_points = reward_points + %s WHERE renter_email = %s",
            (price, renter_email)
        )

    print("Booking confirmed!")


def view_my_bookings(cur, renter_email):
    print("\n=== My Bookings ===")
    cur.execute("""
        SELECT b.booking_id, p.street_address, b.start_date, b.end_date, b.card_number
        FROM Booking b
        JOIN Property p ON b.property_id = p.property_id
        WHERE b.renter_email = %s
    """, (renter_email,))
    rows = cur.fetchall()

    for row in rows:
        print(f"Booking ID: {row[0]} | {row[1]} | {row[2]} to {row[3]} | Card: {row[4]}")


def cancel_booking(cur, renter_email):
    print("\n=== Cancel Booking ===")
    booking_id = input("Enter booking ID to cancel: ")
    cur.execute("DELETE FROM Booking WHERE booking_id = %s AND renter_email = %s", (booking_id, renter_email))
    print("Booking canceled.")


def join_reward_program(cur, renter_email):
    cur.execute("SELECT * FROM Reward_Program WHERE renter_email = %s", (renter_email,))
    if cur.fetchone():
        print("You are already part of the reward program.")
    else:
        cur.execute("INSERT INTO Reward_Program (reward_points, renter_email) VALUES (0, %s)", (renter_email,))
        print("Welcome! You have successfully joined the reward program.")


def view_reward_points(cur, renter_email):
    cur.execute("SELECT reward_points FROM Reward_Program WHERE renter_email = %s", (renter_email,))
    row = cur.fetchone()
    if row:
        print(f"You have {row[0]} reward points.")
    else:
        print("You're not enrolled in the reward program.")
