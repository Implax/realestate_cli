# realestate_cli/users.py

def register_user(cur):
    print("\n=== Register New User ===")
    email = input("Email: ").strip()
    name = input("Full Name: ").strip()
    role = input("Register as (agent/renter): ").strip().lower()

    try:
        # Insert into Users
        cur.execute("INSERT INTO Users (email_address, name) VALUES (%s, %s)", (email, name))

        if role == "agent":
            job = input("Job Title: ").strip()
            agency = input("Agency: ").strip()
            contact = input("Contact Info: ").strip()
            cur.execute("""
                INSERT INTO Agents (job_title, agency, contact_info, user_email)
                VALUES (%s, %s, %s, %s)
            """, (job, agency, contact, email))
        elif role == "renter":
            move_in = input("Move-in Date (YYYY-MM-DD): ").strip()
            location = input("Preferred Location: ").strip()
            budget = input("Budget: ").strip()
            cur.execute("""
                INSERT INTO Renters (move_in_date, preferred_location, budget, user_email)
                VALUES (%s, %s, %s, %s)
            """, (move_in, location, budget, email))
        else:
            print("Invalid role specified. Only 'agent' or 'renter' are allowed.")
            return

        print("User registered successfully!")

    except Exception as e:
        print(f"Error during registration: {e}")
