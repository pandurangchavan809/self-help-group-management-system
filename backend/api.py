"""
backend/api.py
--------------
Service-layer functions used by Streamlit pages.
No UI code here.
"""

from backend.db import get_db_connection
from backend.calculations import close_loan_if_paid


# -------------------------------------------------
# MEMBER MANAGEMENT
# -------------------------------------------------
def add_member(shg_id, first_name, last_name, mobile, monthly_deposit=500):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO members (
            shg_id, first_name, last_name, mobile, monthly_deposit
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (shg_id, first_name, last_name, mobile, monthly_deposit))

    conn.commit()
    cur.close()
    conn.close()


# -------------------------------------------------
# DEPOSIT
# -------------------------------------------------
def add_deposit(shg_id, member_id, amount, month, year):
    conn = get_db_connection()
    cur = conn.cursor()

    # 1️⃣ Save deposit
    cur.execute("""
        INSERT INTO deposits (
            shg_id, member_id, amount, deposit_month, deposit_year
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (shg_id, member_id, amount, month, year))

    # 2️⃣ Log transaction (PASSBOOK ENTRY)
    cur.execute("""
        INSERT INTO transactions (
            shg_id, member_id, txn_type, amount, created_by
        )
        VALUES (%s, %s, 'deposit', %s, 'president')
    """, (shg_id, member_id, amount))

    conn.commit()
    cur.close()
    conn.close()


# -------------------------------------------------
# LOANS
# -------------------------------------------------
def give_loan(shg_id, member_id, loan_amount, interest_rate, remarks=None):
    conn = get_db_connection()
    cur = conn.cursor()

    # 1️⃣ Create loan
    cur.execute("""
        INSERT INTO loans (
            shg_id, member_id, loan_amount, interest_rate, loan_date, remarks
        )
        VALUES (%s, %s, %s, %s, CURDATE(), %s)
    """, (shg_id, member_id, loan_amount, interest_rate, remarks))

    loan_id = cur.lastrowid

    # 2️⃣ Log transaction
    cur.execute("""
        INSERT INTO transactions (
            shg_id, member_id, txn_type, amount, created_by
        )
        VALUES (%s, %s, 'loan_given', %s, 'president')
    """, (shg_id, member_id, loan_amount))

    conn.commit()
    cur.close()
    conn.close()

    return loan_id


# -------------------------------------------------
# LOAN REPAYMENT
# -------------------------------------------------
def repay_loan(loan_id, amount, payment_type):
    conn = get_db_connection()
    cur = conn.cursor()

    # 1️⃣ Record repayment
    cur.execute("""
        INSERT INTO loan_payments (
            loan_id, amount, payment_type, payment_date
        )
        VALUES (%s, %s, %s, CURDATE())
    """, (loan_id, amount, payment_type))

    # 2️⃣ Log transaction
    cur.execute("""
        INSERT INTO transactions (
            shg_id,
            member_id,
            txn_type,
            amount,
            created_by
        )
        SELECT
            l.shg_id,
            l.member_id,
            'loan_payment',
            %s,
            'president'
        FROM loans l
        WHERE l.id = %s
    """, (amount, loan_id))

    conn.commit()
    cur.close()
    conn.close()

    # 3️⃣ Auto-close loan if principal fully paid
    close_loan_if_paid(loan_id)

def update_member(member_id, first_name, last_name, mobile, monthly_deposit):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE members
        SET first_name=%s,
            last_name=%s,
            mobile=%s,
            monthly_deposit=%s
        WHERE id=%s
    """, (first_name, last_name, mobile, monthly_deposit, member_id))
    conn.commit()
    cur.close()
    conn.close()


def deactivate_member(member_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE members
        SET status='left'
        WHERE id=%s
    """, (member_id,))
    conn.commit()
    cur.close()
    conn.close()

def activate_member(member_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE members
        SET status='active'
        WHERE id=%s
    """, (member_id,))
    conn.commit()
    cur.close()
    conn.close()
