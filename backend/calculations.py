from backend.db import get_db_connection

# BASIC CONSTANTS
DEFAULT_MONTHLY_DEPOSIT = 500
DEFAULT_INTEREST_RATE = 2  # percent

# WALLET & SUMMARY

def get_total_savings(shg_id: int) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT IFNULL(SUM(amount),0) FROM deposits WHERE shg_id=%s",
        (shg_id,)
    )
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def get_total_loan_given(shg_id: int) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT IFNULL(SUM(loan_amount),0) FROM loans WHERE shg_id=%s",
        (shg_id,)
    )
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def get_wallet_balance(shg_id: int) -> int:
    """
    Wallet = Total savings - total loan principal given
    """
    return get_total_savings(shg_id) - get_total_loan_given(shg_id)

# LOAN CALCULATIONS

def calculate_monthly_interest(
    loan_amount: int,
    interest_rate: float = DEFAULT_INTEREST_RATE
) -> int:
    """
    Monthly interest (simple interest)
    """
    return int((loan_amount * interest_rate) / 100)


def calculate_monthly_payable(
    loan_amount: int,
    interest_rate: float = DEFAULT_INTEREST_RATE,
    monthly_deposit: int = DEFAULT_MONTHLY_DEPOSIT
) -> int:
    """
    Monthly payable = deposit + interest
    """
    interest = calculate_monthly_interest(loan_amount, interest_rate)
    return monthly_deposit + interest


def get_loan_repaid_amount(loan_id: int) -> int:
    """
    Total principal repaid so far
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM loan_payments
        WHERE loan_id=%s AND payment_type='principal'
    """, (loan_id,))
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def get_loan_interest_paid(loan_id: int) -> int:
    """
    Total interest paid so far
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM loan_payments
        WHERE loan_id=%s AND payment_type='interest'
    """, (loan_id,))
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total


def get_loan_outstanding(loan_id: int) -> int:
    """
    Outstanding principal = loan amount - repaid principal
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT loan_amount FROM loans WHERE id=%s",
        (loan_id,)
    )
    loan_amount = cur.fetchone()[0]
    cur.close()
    conn.close()

    repaid = get_loan_repaid_amount(loan_id)
    return loan_amount - repaid


def is_loan_fully_paid(loan_id: int) -> bool:
    """
    Loan is closed only when principal is fully paid
    """
    return get_loan_outstanding(loan_id) <= 0


def close_loan_if_paid(loan_id: int) -> None:
    """
    Mark loan as closed if principal fully paid
    """
    if not is_loan_fully_paid(loan_id):
        return

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE loans
        SET status='closed', closed_date=CURDATE()
        WHERE id=%s
    """, (loan_id,))
    conn.commit()
    cur.close()
    conn.close()
