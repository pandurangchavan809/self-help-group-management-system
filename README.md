# Self Help Group Management System

This project is a digital ledger and reporting system designed for **Mahila Bachat Gats (Self Help Groups)**.  
It helps SHG presidents maintain transparent records of savings, loans, repayments, and reports without handling real money.

The system is intentionally simple so it can be used comfortably by rural users while still being reliable for audits, NGOs, and banks.

---

## Purpose

Mahila Bachat Gats usually maintain records in notebooks.  
This project replaces manual registers with a **clear, structured, and trustworthy digital system**.

The application:
- Does **not** handle real money transfers
- Acts only as a **record-keeping and reporting tool**
- Ensures transparency among all members

---

## Key Features

### User Roles

**President**
- Creates and manages the SHG
- Adds, edits, deactivates, and reactivates members
- Records deposits, loans, and repayments
- Generates PDF reports
- Copies WhatsApp and SMS messages

**Member (View Only)**
- Logs in using name and mobile number
- Views own deposits, loans, and past loan history
- Cannot edit any data

**Admin**
- System-level access
- Can view all SHGs
- Can audit and manage records if required

---

## Core Functionalities

### Member Management
- Add members with name and mobile number
- Monthly deposit amount per member
- Members can be marked inactive instead of deleted
- Reactivation supported without data loss

### Deposits
- Monthly deposits
- Bulk deposit entry
- Missed deposits are visible
- All deposits are logged permanently

### Loan Management
- Loans have **no fixed duration**
- Interest is monthly (configurable, e.g., 2%)
- Partial repayments allowed
- Loan automatically moves to past loans once fully repaid

### Transaction History
- Every deposit, loan, and repayment is logged
- No record can be deleted
- Used for transparency and audits

---

## Reports

### PDF Reports
- Custom date range selection
- Clean summary (Savings, Loans, Available Cash)
- Embedded pie chart
- Member-wise summary for long-term history
- Loan summary (active and closed)
- Printable and audit-ready

### WhatsApp Messages
- System generates formatted messages
- President copies and sends manually
- No WhatsApp API required
- No cost involved

### SMS Support
- Designed to work with Fast2SMS or DLT-based SMS providers
- Messages for deposits, loans, and repayments

---

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MySQL
- **PDF Generation**: ReportLab + Matplotlib
- **Charts**: Matplotlib (non-interactive)
- **SMS**: Fast2SMS (optional)

---

## Project Structure

```text
self-help-group-management/
├── app.py                  # Login and entry point
├── pages/
│   ├── dashboard.py        # Dashboard view
│   ├── members.py          # Member, deposit, loan management
│   └── reports.py          # Reports and messaging
├── backend/
│   ├── db.py               # Database connection
│   ├── auth.py             # Authentication logic
│   ├── api.py              # Service-layer functions
│   ├── calculations.py     # Financial calculations
│   └── sms.py              # SMS helpers
├── pdf/
│   └── generator.py        # PDF report generation
├── requirements.txt
├── README.md
└── .env                    # Environment variables

```
---
## Installation

### 1. Clone the repository

git clone <https://github.com/pandurangchavan809/self-help-group-management-system.git>

### 2. Create a virtual environment

python -m venv venv
venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Configure environment variables

Create a `.env` file in the project root directory and add the following:

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=mahila_bachat_gat

### 5. Run the application

streamlit run app.py

---

## Design Principles

- Simple language and large text
- Minimal screens and navigation
- No complex or interactive graphs
- Focus on trust, clarity, and transparency
- Suitable for low-end mobile and desktop devices

---
## Important Notes

- This system does not handle real money
- All amounts are records only
- Data deletion is intentionally restricted to maintain trust
- Temporary files used during PDF generation are safely handled by the operating system (Windows compatible)

---
## License

This project is provided for educational and community use.  
You are free to modify and deploy it for SHGs, NGOs, or local organizations.
