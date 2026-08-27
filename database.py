import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "database/procurement.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    # Enable foreign key support
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():

    connection = get_db_connection()

    # -----------------------------
    # FARMERS TABLE
    # -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            email TEXT,
            address TEXT,
            farmer_id TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check existing farmer columns
    columns = connection.execute(
        "PRAGMA table_info(farmers)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    # Add password_hash if using an older database
    if "password_hash" not in column_names:

        connection.execute("""
            ALTER TABLE farmers
            ADD COLUMN password_hash TEXT
        """)


    # -----------------------------
    # PROCUREMENT SLOTS TABLE
    # -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS procurement_slots (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            slot_date TEXT NOT NULL,

            slot_time TEXT NOT NULL,

            capacity INTEGER NOT NULL DEFAULT 10,

            booked_count INTEGER NOT NULL DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(slot_date, slot_time)
        )
    """)


    # -----------------------------
    # BOOKINGS TABLE
    # -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            farmer_id INTEGER NOT NULL,

            slot_id INTEGER NOT NULL,

            booking_number INTEGER NOT NULL,

            status TEXT NOT NULL DEFAULT 'Booked',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (farmer_id)
                REFERENCES farmers(id),

            FOREIGN KEY (slot_id)
                REFERENCES procurement_slots(id),

            UNIQUE(farmer_id, slot_id)
        )
    """)

    
# -----------------------------
# PRODUCE TABLE
# -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS produce (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            farmer_id INTEGER NOT NULL,

            booking_id INTEGER,

            produce_name TEXT NOT NULL,

            quantity REAL NOT NULL,

            unit TEXT NOT NULL,

            expected_price REAL,

            status TEXT NOT NULL DEFAULT 'Submitted',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (farmer_id)
                REFERENCES farmers(id),

            FOREIGN KEY (booking_id)
                REFERENCES bookings(id)
       )
    """)

        # Add payment_status column if it does not already exist
    columns = connection.execute(
        "PRAGMA table_info(produce)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "payment_status" not in column_names:
        connection.execute("""
            ALTER TABLE produce
            ADD COLUMN payment_status TEXT NOT NULL DEFAULT 'Pending'
        """)

    connection.commit()


# -----------------------------
# ADMINS TABLE
# -----------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS admins (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    connection.close()

def create_sample_slots():

    connection = get_db_connection()

    sample_slots = [

        ("2026-08-27", "09:00 AM", 10),
        ("2026-08-27", "10:00 AM", 10),
        ("2026-08-27", "11:00 AM", 10),

        ("2026-08-28", "09:00 AM", 10),
        ("2026-08-28", "10:00 AM", 10),
        ("2026-08-28", "11:00 AM", 10),

        ("2026-08-29", "09:00 AM", 10),
        ("2026-08-29", "10:00 AM", 10),
        ("2026-08-29", "11:00 AM", 10)

    ]

    for slot_date, slot_time, capacity in sample_slots:

        connection.execute("""
            INSERT OR IGNORE INTO procurement_slots
            (slot_date, slot_time, capacity)
            VALUES (?, ?, ?)
        """, (
            slot_date,
            slot_time,
            capacity
        ))

    connection.commit()
    connection.close()

    print("Sample procurement slots created!")

def create_default_admin():

    connection = get_db_connection()

    existing_admin = connection.execute("""
        SELECT id
        FROM admins
        WHERE username = ?
    """, ("admin",)).fetchone()

    if existing_admin is None:

        password_hash = generate_password_hash("admin123")

        connection.execute("""
            INSERT INTO admins
            (username, password_hash)
            VALUES (?, ?)
        """, (
            "admin",
            password_hash
        ))

        connection.commit()

        print("Default admin account created.")

    else:

        print("Admin account already exists.")

    connection.close()

if __name__ == "__main__":

    create_tables()

    create_sample_slots()

    create_default_admin()

    print("Database setup completed successfully!")