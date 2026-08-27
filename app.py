from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_tables, get_db_connection

app = Flask(__name__)

app.secret_key = "smart-farmer-secret-key"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Get form values FIRST
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        farmer_id = request.form.get("farmer_id", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Check required fields
        if not name or not phone or not farmer_id or not password:
            flash("Please fill in all required fields.", "error")
            return render_template("register.html")

        # Check password confirmation
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        connection = get_db_connection()

        # Check duplicate phone number
        existing_phone = connection.execute(
            "SELECT id FROM farmers WHERE phone = ?",
            (phone,)
        ).fetchone()

        if existing_phone:
            connection.close()
            flash("This phone number is already registered.", "error")
            return render_template("register.html")

        # Check duplicate Farmer ID
        existing_farmer = connection.execute(
            "SELECT id FROM farmers WHERE farmer_id = ?",
            (farmer_id,)
        ).fetchone()

        if existing_farmer:
            connection.close()
            flash("This Farmer ID is already registered.", "error")
            return render_template("register.html")

        # Securely hash the password
        password_hash = generate_password_hash(password)

        # Save farmer
        connection.execute("""
            INSERT INTO farmers
            (name, phone, email, address, farmer_id, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            phone,
            email,
            address,
            farmer_id,
            password_hash
        ))

        connection.commit()
        connection.close()

        flash(
            "Registration successful! Welcome to Smart Farmer.",
            "success"
        )

        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        farmer_id = request.form.get("farmer_id", "").strip()
        password = request.form.get("password", "")

        if not farmer_id or not password:
            flash("Please enter your Farmer ID and password.", "error")
            return render_template("login.html")

        connection = get_db_connection()

        farmer = connection.execute(
            "SELECT * FROM farmers WHERE farmer_id = ?",
            (farmer_id,)
        ).fetchone()

        connection.close()

        # Farmer ID doesn't exist
        if farmer is None:
            flash("Invalid Farmer ID or password.", "error")
            return render_template("login.html")

        # Check password
        if not farmer["password_hash"] or not check_password_hash(
            farmer["password_hash"],
            password
        ):
            flash("Invalid Farmer ID or password.", "error")
            return render_template("login.html")

        # Store farmer information in session
        session["farmer_id"] = farmer["farmer_id"]
        session["farmer_name"] = farmer["name"]

        flash("Login successful!", "success")

        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "farmer_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    connection = get_db_connection()

    # Find the logged-in farmer
    farmer = connection.execute("""
        SELECT id
        FROM farmers
        WHERE farmer_id = ?
    """, (
        session["farmer_id"],
    )).fetchone()

    if farmer is None:

        connection.close()

        flash(
            "Farmer account could not be found.",
            "error"
        )

        return redirect(url_for("login"))

    # Count pending payments
    pending_payments = connection.execute("""
        SELECT COUNT(*) AS count
        FROM produce
        WHERE farmer_id = ?
        AND payment_status = 'Pending'
    """, (
        farmer["id"],
    )).fetchone()["count"]

    # Count completed payments
    paid_payments = connection.execute("""
        SELECT COUNT(*) AS count
        FROM produce
        WHERE farmer_id = ?
        AND payment_status = 'Paid'
    """, (
        farmer["id"],
    )).fetchone()["count"]

    connection.close()

    return render_template(
        "dashboard.html",

        farmer_name=session["farmer_name"],

        farmer_id=session["farmer_id"],

        pending_payments=pending_payments,

        paid_payments=paid_payments
    )

@app.route("/book-slot", methods=["GET", "POST"])
def book_slot():

    # Make sure farmer is logged in
    if "farmer_id" not in session:

        flash("Please login first.", "error")

        return redirect(url_for("login"))


    connection = get_db_connection()


    # -----------------------------
    # GET REQUEST
    # -----------------------------

    if request.method == "GET":

        slots = connection.execute("""
            SELECT *
            FROM procurement_slots
            WHERE booked_count < capacity
            ORDER BY slot_date, slot_time
        """).fetchall()

        connection.close()

        return render_template(
            "book_slot.html",
            slots=slots
        )


    # -----------------------------
    # POST REQUEST
    # -----------------------------

    slot_id = request.form.get("slot_id")


    if not slot_id:

        connection.close()

        flash("Please select a procurement slot.", "error")

        return redirect(url_for("book_slot"))


    # Find the selected slot
    slot = connection.execute("""
        SELECT *
        FROM procurement_slots
        WHERE id = ?
    """, (slot_id,)).fetchone()


    if slot is None:

        connection.close()

        flash("Selected slot does not exist.", "error")

        return redirect(url_for("book_slot"))


    # Check whether the slot is full
    if slot["booked_count"] >= slot["capacity"]:

        connection.close()

        flash("Sorry, this slot is already full.", "error")

        return redirect(url_for("book_slot"))


    # Get logged-in farmer's database ID
    farmer = connection.execute("""
        SELECT id
        FROM farmers
        WHERE farmer_id = ?
    """, (
        session["farmer_id"],
    )).fetchone()


    if farmer is None:

        connection.close()

        flash("Farmer account could not be found.", "error")

        return redirect(url_for("login"))


    # Check whether this farmer already booked this slot
    existing_booking = connection.execute("""
        SELECT id
        FROM bookings
        WHERE farmer_id = ?
        AND slot_id = ?
    """, (
        farmer["id"],
        slot_id
    )).fetchone()


    if existing_booking:

        connection.close()

        flash(
            "You have already booked this procurement slot.",
            "error"
        )

        return redirect(url_for("book_slot"))


    # Generate booking number
    booking_count = connection.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE slot_id = ?
    """, (
        slot_id,
    )).fetchone()[0]


    booking_number = booking_count + 1


    # Create booking
    connection.execute("""
        INSERT INTO bookings
        (farmer_id, slot_id, booking_number, status)
        VALUES (?, ?, ?, 'Booked')
    """, (
        farmer["id"],
        slot_id,
        booking_number
    ))


    # Increase booked count
    connection.execute("""
        UPDATE procurement_slots
        SET booked_count = booked_count + 1
        WHERE id = ?
    """, (
        slot_id,
    ))


    connection.commit()
    connection.close()


    flash(
        f"Slot booked successfully! Your queue number is {booking_number}.",
        "success"
    )

    return redirect(url_for("dashboard"))

@app.route("/my-queue")
def my_queue():

    # Make sure farmer is logged in
    if "farmer_id" not in session:

        flash("Please login first.", "error")

        return redirect(url_for("login"))

    connection = get_db_connection()

    # Get all bookings made by the logged-in farmer
    bookings = connection.execute("""
        SELECT
            bookings.id,
            bookings.booking_number,
            bookings.status,
            bookings.created_at,
            procurement_slots.slot_date,
            procurement_slots.slot_time
        FROM bookings

        JOIN farmers
            ON bookings.farmer_id = farmers.id

        JOIN procurement_slots
            ON bookings.slot_id = procurement_slots.id

        WHERE farmers.farmer_id = ?

        ORDER BY
            procurement_slots.slot_date,
            procurement_slots.slot_time
    """, (
        session["farmer_id"],
    )).fetchall()

    connection.close()

    return render_template(
        "my_queue.html",
        bookings=bookings
    )

@app.route("/add-produce", methods=["GET", "POST"])
def add_produce():

    if "farmer_id" not in session:

        flash("Please login first.", "error")

        return redirect(url_for("login"))

    connection = get_db_connection()

    farmer = connection.execute("""
        SELECT id
        FROM farmers
        WHERE farmer_id = ?
    """, (
        session["farmer_id"],
    )).fetchone()

    if farmer is None:

        connection.close()

        flash("Farmer account could not be found.", "error")

        return redirect(url_for("login"))

    # -----------------------------
    # GET REQUEST
    # -----------------------------

    if request.method == "GET":

        bookings = connection.execute("""
            SELECT
                bookings.id,
                bookings.booking_number,
                procurement_slots.slot_date,
                procurement_slots.slot_time

            FROM bookings

            JOIN procurement_slots
                ON bookings.slot_id = procurement_slots.id

            WHERE bookings.farmer_id = ?

            AND bookings.status = 'Booked'

            ORDER BY
                procurement_slots.slot_date,
                procurement_slots.slot_time
        """, (
            farmer["id"],
        )).fetchall()

        connection.close()

        return render_template(
            "add_produce.html",
            bookings=bookings
        )

    # -----------------------------
    # POST REQUEST
    # -----------------------------

    booking_id = request.form.get("booking_id")

    produce_name = request.form.get(
        "produce_name",
        ""
    ).strip()

    quantity_text = request.form.get(
        "quantity",
        ""
    ).strip()

    unit = request.form.get(
        "unit",
        ""
    ).strip()

    expected_price_text = request.form.get(
        "expected_price",
        ""
    ).strip()


    # Required fields

    if not booking_id or not produce_name or not quantity_text or not unit:

        connection.close()

        flash(
            "Please fill in all required fields.",
            "error"
        )

        return redirect(url_for("add_produce"))


    # Convert quantity

    try:

        quantity = float(quantity_text)

        if quantity <= 0:

            raise ValueError

    except ValueError:

        connection.close()

        flash(
            "Please enter a valid quantity.",
            "error"
        )

        return redirect(url_for("add_produce"))


    # Convert expected price if provided

    expected_price = None

    if expected_price_text:

        try:

            expected_price = float(
                expected_price_text
            )

            if expected_price < 0:

                raise ValueError

        except ValueError:

            connection.close()

            flash(
                "Please enter a valid expected price.",
                "error"
            )

            return redirect(url_for("add_produce"))


    # Make sure booking belongs to this farmer

    booking = connection.execute("""
        SELECT id
        FROM bookings

        WHERE id = ?

        AND farmer_id = ?

        AND status = 'Booked'
    """, (
        booking_id,
        farmer["id"]
    )).fetchone()


    if booking is None:

        connection.close()

        flash(
            "Invalid procurement booking selected.",
            "error"
        )

        return redirect(url_for("add_produce"))


    # Save produce

    connection.execute("""
        INSERT INTO produce
        (
            farmer_id,
            booking_id,
            produce_name,
            quantity,
            unit,
            expected_price,
            status
        )

        VALUES (?, ?, ?, ?, ?, ?, 'Submitted')
    """, (
        farmer["id"],
        booking_id,
        produce_name,
        quantity,
        unit,
        expected_price
    ))


    connection.commit()

    connection.close()


    flash(
        "Produce details submitted successfully!",
        "success"
    )

    return redirect(url_for("my_produce"))


@app.route("/my-produce")
def my_produce():

    if "farmer_id" not in session:

        flash("Please login first.", "error")

        return redirect(url_for("login"))

    connection = get_db_connection()

    farmer = connection.execute("""
        SELECT id
        FROM farmers
        WHERE farmer_id = ?
    """, (
        session["farmer_id"],
    )).fetchone()

    if farmer is None:

        connection.close()

        flash("Farmer account could not be found.", "error")

        return redirect(url_for("login"))

    produce_list = connection.execute("""
    SELECT
        produce.id,
        produce.produce_name,
        produce.quantity,
        produce.unit,
        produce.expected_price,
        produce.status,
        produce.payment_status,
        produce.created_at,
        bookings.booking_number
    FROM produce

        LEFT JOIN bookings
            ON produce.booking_id = bookings.id

        WHERE produce.farmer_id = ?

        ORDER BY produce.created_at DESC
    """, (
        farmer["id"],
    )).fetchall()

    connection.close()

    return render_template(
        "my_produce.html",
        produce_list=produce_list
    )

@app.route("/admin/dashboard")
def admin_dashboard():

    # Make sure admin is logged in
    if "admin_id" not in session:

        flash(
            "Please login as administrator.",
            "error"
        )

        return redirect(
            url_for("admin_login")
        )


    connection = get_db_connection()


    # -----------------------------
    # TOTAL FARMERS
    # -----------------------------

    total_farmers = connection.execute("""
        SELECT COUNT(*) AS count
        FROM farmers
    """).fetchone()["count"]


    # -----------------------------
    # TOTAL BOOKINGS
    # -----------------------------

    total_bookings = connection.execute("""
        SELECT COUNT(*) AS count
        FROM bookings
    """).fetchone()["count"]


    # -----------------------------
    # TOTAL PRODUCE SUBMISSIONS
    # -----------------------------

    total_produce = connection.execute("""
        SELECT COUNT(*) AS count
        FROM produce
    """).fetchone()["count"]


    # -----------------------------
    # TOTAL PROCUREMENT SLOTS
    # -----------------------------

    total_slots = connection.execute("""
        SELECT COUNT(*) AS count
        FROM procurement_slots
    """).fetchone()["count"]


    # -----------------------------
    # OPEN PROCUREMENT SLOTS
    # -----------------------------

    open_slots = connection.execute("""
        SELECT COUNT(*) AS count
        FROM procurement_slots
        WHERE booked_count < capacity
    """).fetchone()["count"]


    # -----------------------------
    # TOTAL PRODUCE QUANTITY
    # -----------------------------

    total_quantity = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0) AS total
        FROM produce
    """).fetchone()["total"]

        # -----------------------------
    # PAYMENT STATISTICS
    # -----------------------------

    pending_payments = connection.execute("""
        SELECT COUNT(*) AS count
        FROM produce
        WHERE payment_status = 'Pending'
    """).fetchone()["count"]


    paid_payments = connection.execute("""
        SELECT COUNT(*) AS count
        FROM produce
        WHERE payment_status = 'Paid'
    """).fetchone()["count"]


    connection.close()


    return render_template(
    "admin_dashboard.html",

    total_farmers=total_farmers,

    total_bookings=total_bookings,

    total_produce=total_produce,

    total_slots=total_slots,

    open_slots=open_slots,

    total_quantity=total_quantity,

    pending_payments=pending_payments,

    paid_payments=paid_payments
)
@app.route("/admin/farmers")
def admin_farmers():

    # Make sure admin is logged in
    if "admin_id" not in session:

        flash(
            "Please login as administrator.",
            "error"
        )

        return redirect(
            url_for("admin_login")
        )

    connection = get_db_connection()

    farmers = connection.execute("""
        SELECT
            id,
            farmer_id,
            name,
            phone,
            email,
            address,
            created_at
        FROM farmers
        ORDER BY created_at DESC
    """).fetchall()

    connection.close()

    return render_template(
        "admin_farmers.html",
        farmers=farmers
    )


@app.route("/admin/slots", methods=["GET", "POST"])
def admin_slots():

    # Make sure admin is logged in
    if "admin_id" not in session:

        flash(
            "Please login as administrator.",
            "error"
        )

        return redirect(
            url_for("admin_login")
        )


    connection = get_db_connection()


    # --------------------------------
    # CREATE NEW SLOT
    # --------------------------------

    if request.method == "POST":

        slot_date = request.form.get(
            "slot_date",
            ""
        ).strip()

        slot_time = request.form.get(
            "slot_time",
            ""
        ).strip()

        capacity = request.form.get(
            "capacity",
            ""
        ).strip()


        # Check required fields

        if not slot_date or not slot_time or not capacity:

            connection.close()

            flash(
                "Please fill in all slot details.",
                "error"
            )

            return redirect(
                url_for("admin_slots")
            )


        # Check capacity

        try:

            capacity = int(capacity)

            if capacity <= 0:

                raise ValueError

        except ValueError:

            connection.close()

            flash(
                "Capacity must be a positive number.",
                "error"
            )

            return redirect(
                url_for("admin_slots")
            )


        # Check whether the slot already exists

        existing_slot = connection.execute("""
            SELECT id
            FROM procurement_slots
            WHERE slot_date = ?
            AND slot_time = ?
        """, (
            slot_date,
            slot_time
        )).fetchone()


        if existing_slot:

            connection.close()

            flash(
                "This procurement slot already exists.",
                "error"
            )

            return redirect(
                url_for("admin_slots")
            )


        # Create slot

        connection.execute("""
            INSERT INTO procurement_slots
            (
                slot_date,
                slot_time,
                capacity,
                booked_count
            )
            VALUES (?, ?, ?, 0)
        """, (
            slot_date,
            slot_time,
            capacity
        ))


        connection.commit()

        connection.close()


        flash(
            "Procurement slot created successfully!",
            "success"
        )

        return redirect(
            url_for("admin_slots")
        )


    # --------------------------------
    # DISPLAY EXISTING SLOTS
    # --------------------------------

    slots = connection.execute("""
        SELECT
            id,
            slot_date,
            slot_time,
            capacity,
            booked_count,
            created_at
        FROM procurement_slots
        ORDER BY slot_date ASC, slot_time ASC
    """).fetchall()


    connection.close()


    return render_template(
        "admin_slots.html",
        slots=slots
    )

@app.route("/admin/bookings")
def admin_bookings():

    # Make sure admin is logged in
    if "admin_id" not in session:

        flash(
            "Please login as administrator.",
            "error"
        )

        return redirect(
            url_for("admin_login")
        )


    connection = get_db_connection()


    bookings = connection.execute("""
        SELECT
            bookings.id,
            bookings.booking_number,
            bookings.status,
            bookings.created_at,

            farmers.farmer_id,
            farmers.name,
            farmers.phone,

            procurement_slots.slot_date,
            procurement_slots.slot_time

        FROM bookings

        JOIN farmers
            ON bookings.farmer_id = farmers.id

        JOIN procurement_slots
            ON bookings.slot_id = procurement_slots.id

        ORDER BY
            procurement_slots.slot_date ASC,
            procurement_slots.slot_time ASC,
            bookings.booking_number ASC

    """).fetchall()


    connection.close()


    return render_template(
        "admin_bookings.html",
        bookings=bookings
    )

@app.route("/admin/produce")
def admin_produce():

    # Make sure admin is logged in
    if "admin_id" not in session:

        flash(
            "Please login as administrator.",
            "error"
        )

        return redirect(
            url_for("admin_login")
        )

    connection = get_db_connection()

    produce = connection.execute("""
        SELECT
            produce.id,
            produce.produce_name,
            produce.quantity,
            produce.unit,
            produce.expected_price,
            produce.status,
            produce.payment_status,
            produce.created_at,

            farmers.farmer_id,
            farmers.name,
            farmers.phone

        FROM produce

        JOIN farmers
            ON produce.farmer_id = farmers.id

        ORDER BY produce.created_at DESC

    """).fetchall()

    connection.close()

    return render_template(
        "admin_produce.html",
        produce=produce
    )

@app.route("/admin/produce/<int:produce_id>/status", methods=["POST"])
def update_produce_status(produce_id):

    # Make sure admin is logged in
    if "admin_id" not in session:

        flash(
            "Please login as administrator.",
            "error"
        )

        return redirect(
            url_for("admin_login")
        )


    new_status = request.form.get(
        "status",
        ""
    ).strip()


    # Only allow these statuses
    if new_status not in ["Accepted", "Rejected"]:

        flash(
            "Invalid produce status.",
            "error"
        )

        return redirect(
            url_for("admin_produce")
        )


    connection = get_db_connection()


    # Check whether produce exists
    produce = connection.execute("""
        SELECT id, status
        FROM produce
        WHERE id = ?
    """, (
        produce_id,
    )).fetchone()


    if produce is None:

        connection.close()

        flash(
            "Produce submission not found.",
            "error"
        )

        return redirect(
            url_for("admin_produce")
        )


    # Update status
    connection.execute("""
        UPDATE produce
        SET status = ?
        WHERE id = ?
    """, (
        new_status,
        produce_id
    ))


    connection.commit()

    connection.close()


    flash(
        f"Produce status updated to {new_status}.",
        "success"
    )


    return redirect(
        url_for("admin_produce")
    )

@app.route("/admin/produce/<int:produce_id>/payment", methods=["POST"])
def update_payment_status(produce_id):

    # Make sure staff is logged in
    if "admin_id" not in session:

        flash(
            "Please login as administrator.",
            "error"
        )

        return redirect(
            url_for("admin_login")
        )

    connection = get_db_connection()

    produce = connection.execute("""
        SELECT id, status, payment_status
        FROM produce
        WHERE id = ?
    """, (
        produce_id,
    )).fetchone()

    if produce is None:

        connection.close()

        flash(
            "Produce submission not found.",
            "error"
        )

        return redirect(
            url_for("admin_produce")
        )

    # Only accepted produce can be paid
    if produce["status"] != "Accepted":

        connection.close()

        flash(
            "Payment can only be made for accepted produce.",
            "error"
        )

        return redirect(
            url_for("admin_produce")
        )

    # Mark payment as paid
    connection.execute("""
        UPDATE produce
        SET payment_status = 'Paid'
        WHERE id = ?
    """, (
        produce_id,
    ))

    connection.commit()
    connection.close()

    flash(
        "Payment status updated to Paid.",
        "success"
    )

    return redirect(
        url_for("admin_produce")
    )

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        if not username or not password:

            flash(
                "Please enter username and password.",
                "error"
            )

            return render_template(
                "admin_login.html"
            )


        connection = get_db_connection()

        admin = connection.execute("""
            SELECT *
            FROM admins
            WHERE username = ?
        """, (
            username,
        )).fetchone()

        connection.close()


        if admin is None:

            flash(
                "Invalid username or password.",
                "error"
            )

            return render_template(
                "admin_login.html"
            )


        if not check_password_hash(
            admin["password_hash"],
            password
        ):

            flash(
                "Invalid username or password.",
                "error"
            )

            return render_template(
                "admin_login.html"
            )


        session["admin_id"] = admin["id"]

        session["admin_username"] = admin["username"]


        flash(
            "Admin login successful!",
            "success"
        )


        return redirect(
            url_for("admin_dashboard")
        )


    return render_template(
        "admin_login.html"
    )

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_id", None)

    session.pop("admin_username", None)

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("admin_login")
    )

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )