# 🌾 Smart Farmer Procurement System

A web-based application designed to simplify the agricultural produce procurement process for farmers and procurement staff.

The **Smart Farmer Procurement System** allows farmers to register, book procurement slots, receive queue numbers, submit produce details, and track their payment status. Staff members can manage farmer produce submissions, accept or reject produce, and update payment status.

---

## 📌 Project Overview

In traditional agricultural procurement systems, farmers may face long waiting times, difficulty managing procurement schedules, and limited visibility into the status of their produce and payments.

The Smart Farmer Procurement System provides a simple digital solution for managing this process.

The application has two main user roles:

- 👨‍🌾 **Farmer**
- 👨‍💼 **Staff/Admin**

The system is built using **Flask and SQLite**, making it lightweight and suitable for local or small-scale deployments.

---

## ✨ Features

### 👨‍🌾 Farmer Features

- Farmer registration
- Farmer login and logout
- Unique Farmer ID
- Phone number registration
- Optional email address
- Procurement slot booking
- Queue/booking number generation
- View booked procurement slots
- Submit agricultural produce details
- View submitted produce
- Track produce status
- View payment status
- View pending and paid payment summary

### 👨‍💼 Staff/Admin Features

- Secure staff login
- Staff dashboard
- View procurement bookings
- View farmer produce submissions
- Accept submitted produce
- Reject submitted produce
- Mark accepted produce as paid
- Track payment status

### 💰 Payment Management

The application supports two payment states:

- **Pending**
- **Paid**

The typical workflow is:

```text
Farmer submits produce
        ↓
Status: Submitted
        ↓
Staff reviews produce
        ↓
Accepted / Rejected
        ↓
If Accepted
        ↓
Payment: Pending
        ↓
Staff marks payment as Paid
        ↓
Farmer can view updated payment status
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML | Page structure |
| CSS | User interface styling |
| Jinja2 | Template rendering |
| Werkzeug | Password hashing |

---

## 📂 Project Structure

```text
farmer_procurement_system/
│
├── app.py
├── database.py
├── README.md
├── requirements.txt
│
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── book_slot.html
│   ├── my_queue.html
│   ├── add_produce.html
│   ├── my_produce.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── admin_produce.html
│
├── static/
│   └── css/
│       └── style.css
│
└── .gitignore
```

> Some filenames may vary depending on the final project structure.

---

# 👥 User Roles

## 👨‍🌾 Farmer

A farmer can:

1. Register an account
2. Log in
3. Book a procurement slot
4. Receive a queue number
5. Submit produce details
6. View submitted produce
7. Check produce status
8. Check payment status

### Farmer Workflow

```text
Register
   ↓
Login
   ↓
Book Procurement Slot
   ↓
Receive Queue Number
   ↓
Submit Produce
   ↓
Staff Reviews Produce
   ↓
Accepted / Rejected
   ↓
Payment Status
```

---

## 👨‍💼 Staff/Admin

A staff member can:

1. Log in to the staff portal
2. View procurement information
3. View submitted produce
4. Accept or reject produce
5. Mark accepted produce as paid

### Staff Workflow

```text
Staff Login
     ↓
Staff Dashboard
     ↓
View Submitted Produce
     ↓
Accept / Reject
     ↓
Mark Accepted Produce as Paid
```

---

# 🗄️ Database

The project uses **SQLite** as the database.

The main tables include:

| Table | Description |
|---|---|
| `farmers` | Stores farmer account information |
| `admins` | Stores staff/admin login information |
| `procurement_slots` | Stores available procurement slots |
| `bookings` | Stores farmer slot bookings and queue numbers |
| `produce` | Stores submitted produce and payment information |

---

# 🚀 Installation and Setup

## 1. Clone the Repository

```bash
git clone https://github.com/nishathnourine432/smart-farmer-procurement-system.git
```

Move into the project folder:

```bash
cd smart-farmer-procurement-system
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

---

## 3. Activate the Virtual Environment

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

After activation, you should see:

```text
(venv)
```

---

## 4. Install Dependencies

If the project contains a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Otherwise:

```bash
pip install flask
```

---

## 5. Initialize the Database

Run:

```bash
python database.py
```

This creates the required database tables and initial procurement data.

---

## 6. Run the Application

Start the Flask application:

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

Open this address in your web browser.

---

# 🔐 Default Staff Login

The database setup creates a default staff account:

```text
Username: admin
Password: admin123
```

> ⚠️ This is intended for development and demonstration purposes. The password should be changed before any real deployment.

---

# 📱 Local Network Access

The application can also be accessed from a mobile phone when the computer and phone are connected to the same Wi-Fi or local network.

When running Flask, an address similar to this may appear:

```text
http://192.168.x.x:5000
```

Open that address on a phone connected to the same network.

This allows the system to be used within a local network without requiring deployment to a public web server.

---

# 🧪 Application Workflow

The complete system workflow is:

```text
                 🌾 SMART FARMER SYSTEM
                           │
            ┌──────────────┴──────────────┐
            │                             │
        👨‍🌾 FARMER                    👨‍💼 STAFF
            │                             │
      Register/Login                  Staff Login
            │                             │
       Book Slot                    View Produce
            │                             │
      Queue Number                  Accept/Reject
            │                             │
      Submit Produce                 Mark as Paid
            │                             │
            └──────────────┬──────────────┘
                           │
                    💰 PAYMENT STATUS
                           │
                    Pending → Paid
```

---

# 🧪 Testing

To test the complete system:

### Farmer

1. Register a new farmer.
2. Log in.
3. Book a procurement slot.
4. Check the generated queue number.
5. Submit produce details.
6. Confirm the produce status is **Submitted**.
7. Confirm the payment status is **Pending**.

### Staff

8. Log in as staff.
9. Open the produce management page.
10. Accept the submitted produce.
11. Mark the payment as **Paid**.

### Farmer

12. Log in again as the farmer.
13. Open the dashboard.
14. Check the payment summary.
15. Open **My Produce**.
16. Confirm the produce status is **Accepted**.
17. Confirm the payment status is **Paid**.

---

# 🌐 Offline / Local Usage

The system uses:

- Flask
- SQLite
- Local storage

Therefore, it does not require a cloud database or an external database server for basic operation.

The application can run on a local computer and can be accessed by other devices on the same local network.

This makes it suitable for demonstrations and environments where internet connectivity may be limited.

---

# 🔒 Security Notes

This project is intended primarily for educational and demonstration purposes.

For production use, the following improvements are recommended:

- Change default admin credentials
- Use a secure Flask secret key
- Disable debug mode
- Use HTTPS
- Add stronger validation
- Add role-based access control
- Use a production WSGI server
- Protect database backups and user data

---

# 🔮 Future Improvements

Possible future enhancements include:

- 🌐 Multiple language support
- 📱 Improved mobile responsiveness
- 📩 SMS notifications
- 🧾 Printable receipts
- 📊 Procurement reports
- 📈 Dashboard analytics
- 🔍 Search and filtering
- 📄 Export to PDF or Excel
- 👥 Multiple staff accounts
- 🔐 Role-based permissions
- 💳 Digital payment integration
- ☁️ Cloud deployment

---

# 🎯 Project Objectives

The main objectives of the Smart Farmer Procurement System are:

1. To simplify the agricultural procurement process.
2. To reduce waiting time for farmers through slot booking.
3. To provide queue numbers for procurement management.
4. To allow farmers to submit produce information digitally.
5. To help staff manage and process produce submissions.
6. To provide transparency regarding produce status.
7. To allow farmers to track payment status.
8. To provide a lightweight system using SQLite.
9. To support local network usage.

---

# 📄 License

This project was developed for educational and academic purposes.

---

## 🌾 Smart Farmer Procurement System

**A simple digital solution for managing agricultural produce procurement.**
