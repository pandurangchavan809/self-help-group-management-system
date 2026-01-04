"""
backend/auth.py
----------------
All authentication & SHG identity logic lives here.

Responsibilities:
- President login
- Member login (view only)
- SHG creation (unique, no overlap)
- SHG ID fetch

NO Streamlit code here.
"""

from backend.db import get_db_connection


# -------------------------------------------------
# SHG HELPERS
# -------------------------------------------------

def shg_exists(shg_number: str) -> bool:
    """Check if SHG group number already exists"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM shg_groups WHERE shg_number = %s",
        (shg_number,)
    )
    exists = cur.fetchone() is not None

    cur.close()
    conn.close()
    return exists


def get_shg_id(shg_number: str):
    """Get SHG internal ID from SHG number"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM shg_groups WHERE shg_number = %s AND is_active = 1",
        (shg_number,)
    )
    row = cur.fetchone()

    cur.close()
    conn.close()
    return row[0] if row else None


# -------------------------------------------------
# PRESIDENT AUTH
# -------------------------------------------------

def president_login(shg_number: str, username: str, password: str) -> bool:
    """
    President login using:
    - SHG group number
    - Username
    - Password
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM shg_groups
        WHERE shg_number = %s
          AND president_username = %s
          AND president_password = %s
          AND is_active = 1
    """, (shg_number, username, password))

    success = cur.fetchone() is not None

    cur.close()
    conn.close()
    return success


def create_shg(
    shg_number: str,
    shg_name: str,
    village: str,
    president_username: str,
    president_password: str
) -> bool:
    """
    Create new SHG.
    RULE:
    - SHG number MUST be unique
    - One president per SHG
    """
    if shg_exists(shg_number):
        return False

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO shg_groups (
            shg_number,
            shg_name,
            village,
            president_username,
            president_password
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        shg_number,
        shg_name,
        village,
        president_username,
        president_password
    ))

    conn.commit()
    cur.close()
    conn.close()
    return True


def change_president_password(
    shg_number: str,
    old_password: str,
    new_password: str
) -> bool:
    """Allow president to change password"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE shg_groups
        SET president_password = %s
        WHERE shg_number = %s
          AND president_password = %s
    """, (new_password, shg_number, old_password))

    conn.commit()
    updated = cur.rowcount == 1

    cur.close()
    conn.close()
    return updated


# -------------------------------------------------
# MEMBER AUTH (VIEW ONLY)
# -------------------------------------------------

def member_login(
    shg_number: str,
    first_name: str,
    last_name: str,
    mobile: str
):
    """
    Member login using:
    - First name
    - Last name
    - Mobile number (acts as password)
    - SHG group number

    Returns member_id if valid, else None
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.id
        FROM members m
        JOIN shg_groups s ON s.id = m.shg_id
        WHERE s.shg_number = %s
          AND m.first_name = %s
          AND m.last_name = %s
          AND m.mobile = %s
          AND m.status = 'active'
    """, (shg_number, first_name, last_name, mobile))

    row = cur.fetchone()

    cur.close()
    conn.close()
    return row[0] if row else None
