# realestate_cli/agents.py

def agent_dashboard(cur, conn, email):
    while True:
        print("\n--- Agent Dashboard ---")
        print("1. Add Property")
        print("2. Edit Property")
        print("3. Delete Property")
        print("4. View Bookings for My Properties")
        print("5. Back to Main Menu")
        choice = input("Select an option: ")

        if choice == "1":
            add_property(cur, email)
            conn.commit()
        elif choice == "2":
            edit_property(cur)
            conn.commit()
        elif choice == "3":
            delete_property(cur)
            conn.commit()
        elif choice == "4":
            view_bookings_by_agent(cur, email)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")

def add_property(cur, agent_email):
    print("\n=== Add New Property ===")
    type = input("Property Type (House/Apartment/Commercial): ").strip()
    street = input("Street Address: ")
    city = input("City: ")
    state = input("State: ")
    desc = input("Description: ")
    price = float(input("Rental Price: "))
    available = input("Available (true/false): ").strip().lower() == "true"

    cur.execute("""
        INSERT INTO Property (type, street_address, city, state, description, rental_price, availability)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING property_id
    """, (type, street, city, state, desc, price, available))

    pid = cur.fetchone()[0]
    if type.lower() == "house":
        rooms = int(input("Number of Rooms: "))
        sqft = float(input("Square Footage: "))
        cur.execute("INSERT INTO House (property_id, number_of_rooms, square_footage) VALUES (%s, %s, %s)", (pid, rooms, sqft))
    elif type.lower() == "apartment":
        rooms = int(input("Number of Rooms: "))
        sqft = float(input("Square Footage: "))
        btype = input("Building Type: ")
        cur.execute("INSERT INTO Apartment (property_id, number_of_rooms, square_footage, building_type) VALUES (%s, %s, %s, %s)", (pid, rooms, sqft, btype))
    elif type.lower() == "commercial":
        sqft = float(input("Square Footage: "))
        btype = input("Business Type: ")
        cur.execute("INSERT INTO Commercial_Building (property_id, square_footage, business_type) VALUES (%s, %s, %s)", (pid, sqft, btype))

    print(f"Property added with ID: {pid}")

def edit_property(cur):
    print("\n=== Edit Property ===")
    pid = input("Property ID to edit: ")
    field = input("Field to update (e.g. rental_price, availability): ")
    value = input("New value: ")
    cur.execute(f"UPDATE Property SET {field} = %s WHERE property_id = %s", (value, pid))
    print("Property updated.")

def delete_property(cur):
    print("\n=== Delete Property ===")
    pid = input("Property ID to delete: ")
    cur.execute("DELETE FROM Property WHERE property_id = %s", (pid,))
    print("Property deleted.")

def view_bookings_by_agent(cur, email):
    print("\n=== Bookings for Agent's Properties ===")
    cur.execute("""
        SELECT b.booking_id, p.street_address, b.start_date, b.end_date, b.card_number, b.renter_email
        FROM Booking b
        JOIN Property p ON b.property_id = p.property_id
        JOIN Agents a ON a.user_email = %s
        WHERE p.property_id IN (
            SELECT property_id FROM Property
        )
    """, (email,))

    bookings = cur.fetchall()
    for b in bookings:
        print(f"Booking ID: {b[0]}, Property: {b[1]}, Dates: {b[2]} to {b[3]}, Card: {b[4]}, Renter: {b[5]}")